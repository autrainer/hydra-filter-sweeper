from abc import ABC, abstractmethod
import os

from evalidate import Expr
import hydra
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


class FilterClass(AbstractFilter):
    """
    Filter based on the return value of a given filter class.

    """

    def filter(
        self,
        config: DictConfig,
        directory: str,
        target: str,
        **kwargs,
    ) -> bool:
        """Filter based on the return value of the filter class.

        If the filter condition is met and the configuration should be
        excluded, returns True. Otherwise, returns False.

        Args:
            config: The configuration to be used for filtering.
            directory: The current job directory.
            target: Python relative import path to the filter class inheriting
                from AbstractFilter.

        Returns:
            True if the filter class returns True, False otherwise.
        """
        filter_class = hydra.utils.instantiate({"_target_": target})

        if not isinstance(filter_class, AbstractFilter):
            raise TypeError(
                f"Filter class {target} does not inherit from AbstractFilter"
            )

        return filter_class.filter(config, directory, **kwargs)
