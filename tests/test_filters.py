from evalidate import EvalException
from omegaconf import DictConfig
import pytest

from hydra_filter_sweeper import Exists, Expression


@pytest.fixture
def exists() -> Exists:
    return Exists(DictConfig({}), "tests/test_files")


def test_exists_files(exists: Exists) -> None:
    assert exists.filter("some.file")
    assert not exists.filter("missing.file")


def test_exists_directories(exists: Exists) -> None:
    assert exists.filter("subdir")
    assert not exists.filter("missing_dir")


def test_exists_directories_trailing_slashes(exists: Exists) -> None:
    assert exists.filter("subdir/")
    assert not exists.filter("missing_dir/")


def test_exists_with_subdir(exists: Exists) -> None:
    assert exists.filter("subdir/some.file")
    assert not exists.filter("subdir/missing.file")


def test_expression() -> None:
    expr = Expression(DictConfig({"foo": "bar"}), "")
    assert expr.filter("foo == 'bar'")
    assert not expr.filter("foo == 'baz'")
    assert expr.filter('foo == "bar"')
    assert not expr.filter('foo == "baz"')


def test_expression_attribute_access() -> None:
    expr = Expression(DictConfig({"foo": {"bar": "baz"}}), "")
    assert expr.filter("foo.bar == 'baz'")
    assert not expr.filter("foo.bar == 'qux'")


def test_expression_fn_call() -> None:
    expr = Expression(DictConfig({"foo": {"bar": "baz"}}), "")
    assert expr.filter("len(str(foo.bar)) == 3")
    assert expr.filter("foo.bar in ['baz', 'qux']")

    expr = Expression(DictConfig({"foo": {"bar": 123}}), "")
    assert expr.filter("foo.bar + 1 == 124")
    assert not expr.filter("foo.bar + 1 == 123")
    assert expr.filter("str(foo.bar) == '123'")
    assert expr.filter("foo.bar == int('123')")


def test_expression_invalid_syntax() -> None:
    expr = Expression(DictConfig({"foo": "bar"}), "")
    with pytest.raises(EvalException):
        expr.filter("foo == 'bar' +")
    with pytest.raises(EvalException):
        expr.filter("foo == 'bar' * 2")


def test_expression_invalid_attribute_access() -> None:
    with pytest.raises(EvalException):
        Expression(DictConfig({}), "").filter("foo == 'value'")


def test_expression_unsafe_code() -> None:
    with pytest.raises(EvalException):
        Expression(DictConfig({}), "").filter("__import__('os').system('echo unsafe')")
