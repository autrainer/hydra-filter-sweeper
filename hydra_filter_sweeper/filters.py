from abc import ABC, abstractmethod
import importlib
import os

from evalidate import Expr
from omegaconf import DictConfig


class AbstractFilter(ABC):
    """
    Abstract class for filtering based on the given configuration and
    directory.
    """

    @abstractmethod
    def filter(self, config: DictConfig, directory: str, **kwargs) -> bool:
        """
        Abstract method for filtering based on the given configuration and
        directory.

        If the filter condition is met and the configuration should be
        excluded, returns True. Otherwise, returns False.

        Args:
            config: The configuration to be used for filtering.
            directory: The directory to be filtered.
            **kwargs: Additional keyword arguments.

        Returns:
            True if the filter condition is met, False otherwise.
        """


class FilterExists(AbstractFilter):
    """
    Filter based on the existence of a file or directory in the directory
    of the job.
    """

    def filter(self, config: DictConfig, directory: str, path: str) -> bool:
        """
        Filter based on the existence of a file or directory in the directory
        of the job.

        If the filter condition is met and the configuration should be
        excluded, returns True. Otherwise, returns False.

        Args:
            config: The configuration to be used for filtering.
            directory: The directory to be filtered.
            path: The path to the file or directory.

        Returns:
            True if the file or directory exists, False otherwise.
        """
        return os.path.exists(os.path.join(directory, path))


class FilterExpr(AbstractFilter):
    """
    Filter based on the evaluation of a Python expression using the
    configuration context.
    """

    def filter(self, config: DictConfig, directory: str, expr: str) -> bool:
        """
        Filter based on the evaluation of a Python expression using the
        configuration context.

        If the filter condition is met and the configuration should be
        excluded, returns True. Otherwise, returns False.

        Args:
            config (DictConfig): The configuration to be used for filtering.
            directory (str): The directory to be filtered.
            expr: The Python expression to be evaluated.

        Returns:
            bool: True if the expression evaluates to True, False otherwise.

        Raises:
            ValueError: If there is an error evaluating the expression.
        """
        return Expr(expr).eval(config)


class FilterScript(AbstractFilter):
    """
    Filter based on the return value of any of the filter classes in the
    given Python script.
    """

    def filter(
        self,
        config: DictConfig,
        directory: str,
        path: str,
        **kwargs,
    ) -> bool:
        """
        Filter based on the return value of any of the filter classes in the
        given Python script.

        If the filter condition is met and the configuration should be
        excluded, returns True. Otherwise, returns False.

        Args:
            config: The configuration to be used for filtering.
            directory: The directory to be filtered.
            path: The path to the Python script.
            **kwargs: Additional keyword arguments.

        Returns:
            True if any of the filter classes in the script return True,
            False otherwise.

        Raises:
            ValueError: If the script does not exist or does not contain any
            filter classes.
        """
        if not os.path.exists(path):
            raise ValueError(f"Script '{path}' does not exist")
        module = path.replace("/", ".").replace(".py", "")
        module = importlib.import_module(module)
        filter_classes = [
            cls
            for cls in module.__dict__.values()
            if isinstance(cls, type)
            and issubclass(cls, AbstractFilter)
            and cls is not AbstractFilter
        ]
        if not filter_classes:
            raise ValueError(
                f"Script '{path}' does not contain any filter classes"
            )
        for cls in filter_classes:
            if cls().filter(config, directory, **kwargs):
                return True
        return False
