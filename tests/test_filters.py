from evalidate import EvalException
from hydra.errors import InstantiationException
from omegaconf import DictConfig
import pytest

from hydra_filter_sweeper.filters import (
    AbstractFilter,
    FilterClass,
    FilterExists,
    FilterExpr,
)


@pytest.fixture
def filter_exists():
    return FilterExists()


@pytest.fixture
def filter_expr():
    return FilterExpr()


@pytest.fixture
def filter_class():
    return FilterClass()


class TestAbstractFilter:
    def test_filter(self):
        # Test case for instantiating an AbstractFilter object
        with pytest.raises(TypeError):
            AbstractFilter()


class TestFilterExists:
    def test_filter(self, filter_exists: FilterExists):
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

    def test_filter_with_subdir(self, filter_exists: FilterExists):
        # Test case for filtering a file in a subdir that exists
        assert filter_exists.filter({}, "tests/test_files", "subdir/some.file")

        # Test case for filtering a file in a subdir that does not exist
        assert not filter_exists.filter(
            {}, "tests/test_files", "subdir/nonexistent.file"
        )


class TestFilterExpr:
    def test_filter(self, filter_expr: FilterExpr):
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


class TestFilterClass:
    def test_filter(self, filter_class: FilterClass):
        # Test case for filtering a class that returns True
        assert filter_class.filter(
            DictConfig({"return_value": True}),
            "",
            "tests.test_files.test_filter_classes.TestReturnFilter",
        )

        # Test case for filtering a class that returns False
        assert not filter_class.filter(
            DictConfig({"return_value": False}),
            "",
            "tests.test_files.test_filter_classes.TestReturnFilter",
        )

        # Test case for filtering a nonexistent module
        with pytest.raises(InstantiationException):
            filter_class.filter({}, "", "nonexistent_module")

        # Test case for filtering a nonexistent class
        with pytest.raises(InstantiationException):
            filter_class.filter(
                {},
                "",
                "tests.test_files.test_filter_classes.NonexistentFilter",
            )

        # Test case for filtering a class not inheriting from AbstractFilter
        with pytest.raises(TypeError):
            filter_class.filter(
                DictConfig({"return_value": True}),
                "",
                "tests.test_files.test_filter_classes.TestInvalidFilter",
            )

        # Test case for filtering with additional arguments
        assert not filter_class.filter(
            DictConfig({"return_value": True}),
            "",
            "tests.test_files.test_filter_classes.TestArgEqualsFilter",
            arg1="value1",
            arg2="value2",
        )

        # Test case for filtering a class with too many arguments
        with pytest.raises(TypeError):
            filter_class.filter(
                DictConfig({"return_value": True}),
                "",
                "tests.test_files.test_filter_classes.TestReturnFilter",
                arg1="value1",
                arg2="value2",
            )

        # Test case for filtering a class with too few arguments
        with pytest.raises(TypeError):
            filter_class.filter(
                DictConfig({"return_value": True}),
                "",
                "tests.test_files.test_filter_classes.TestArgEqualsFilter",
            )
