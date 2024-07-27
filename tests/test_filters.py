from evalidate import EvalException
from omegaconf import DictConfig
import pytest

from hydra_filter_sweeper.filters import (
    AbstractFilter,
    FilterExists,
    FilterExpr,
    FilterScript,
)


@pytest.fixture
def filter_exists():
    return FilterExists()


@pytest.fixture
def filter_expr():
    return FilterExpr()


@pytest.fixture
def filter_script():
    return FilterScript()


class TestAbstractFilter:
    def test_filter(self):
        # Test case for instantiating an AbstractFilter object
        with pytest.raises(TypeError):
            AbstractFilter()


class TestFilterExists:
    def test_filter(self, filter_exists):
        # Test case for filtering a file that exists
        assert filter_exists.filter({}, "tests/test_files", "some.file")

        # Test case for filtering a directory that exists
        assert filter_exists.filter({}, "tests/test_files", "subdir")

        # Test case for filtering a file that does not exist
        assert not filter_exists.filter(
            {}, "tests/test_files", "nonexistent.file"
        )

        # Test case for filtering a directory that does not exist
        assert not filter_exists.filter(
            {}, "tests/test_files", "nonexistent_directory"
        )

    def test_filter_with_subdir(self, filter_exists):
        # Test case for filtering a file in a subdir that exists
        assert filter_exists.filter({}, "tests/test_files", "subdir/some.file")

        # Test case for filtering a file in a subdir that does not exist
        assert not filter_exists.filter(
            {}, "tests/test_files", "subdir/nonexistent.file"
        )


class TestFilterExpr:
    def test_filter(self, filter_expr):
        # Test case for evaluating a valid expression that returns True
        assert filter_expr.filter(
            DictConfig({"foo": "bar"}), "", "foo == 'bar'"
        )

        # Test case for evaluating a valid expression that returns False
        assert not filter_expr.filter(
            DictConfig({"foo": "bar"}), "", "foo == 'baz'"
        )

        # Test case for evaluating an invalid expression with missing variable
        with pytest.raises(EvalException):
            filter_expr.filter(
                DictConfig({"foo": "bar"}), "", "foo == invalid"
            )

        # Test case for evaluating an unsafe expression
        with pytest.raises(EvalException):
            filter_expr.filter(
                DictConfig({}),
                "",
                "__import__('os').system('echo unsafe')",
            )


class TestFilterScript:
    def test_filter(self, filter_script):
        # Test case for filtering a script that returns True
        assert filter_script.filter(
            DictConfig({"return_value": True}),
            "",
            "tests/test_files/test_script.py",
        )

        # Test case for filtering a script that returns False
        assert not filter_script.filter(
            DictConfig({"return_value": False}),
            "",
            "tests/test_files/test_script.py",
        )

        # Test case for filtering an empty script
        with pytest.raises(ValueError):
            filter_script.filter(
                {}, "", "tests/test_files/test_script_empty.py"
            )

        # Test case for filtering a nonexistent script
        with pytest.raises(ValueError):
            filter_script.filter({}, "", "nonexistent_script.py")

        # Test case for filtering a script with additional arguments
        assert filter_script.filter(
            DictConfig({"return_value": True}),
            "",
            "tests/test_files/test_script.py",
            arg1="value1",
            arg2="value2",
        )
