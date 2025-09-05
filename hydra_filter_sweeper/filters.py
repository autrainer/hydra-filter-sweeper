from abc import ABC, abstractmethod
import os
from typing import Any, Dict, Optional, Union

from evalidate import Expr, base_eval_model
from omegaconf import DictConfig


class AbstractFilter(ABC):
    def __init__(self, config: DictConfig, directory: str) -> None:
        """Base class for filtering based on the given configuration and directory.

        Args:
            config: The configuration to be used for filtering.
            directory: The Hydra job output directory.
        """
        self.config = config
        self.directory = directory

    @abstractmethod
    def filter(self, *args: Any, **kwargs: Any) -> bool:
        """Abstract method for filtering.

        This method should be implemented by subclasses to define the filtering
        logic based on the provided arguments.

        Returns:
            True if the filter condition is met, False otherwise.
        """

    def reason(self, *args: Any, **kwargs: Any) -> Optional[str]:  # pragma: no cover
        """Optional method to provide a reason for filtering.

        Returns:
            A string explaining the reason for filtering, or None if not implemented.
        """
        return None


class Expression(AbstractFilter):
    def filter(self, expr: str) -> bool:
        """Filter a configuration based on the evaluation of a Python expression using
        the configuration as context.

        All keys in the configuration are added to the attributes list of the
        evaluation model in addition to lists, tuples, and safe function calls
        (e.g., str, int, float, len).

        Args:
            expr: The Python expression to be evaluated.

        Raises:
            ValueError: If there is an error evaluating the expression.

        Returns:
            True if the expression evaluates to True, False otherwise.

        """
        model = base_eval_model.clone()
        model.nodes.extend(["List", "Tuple", "Attribute", "Call"])
        model.allowed_functions.extend(["str", "int", "float", "len"])
        model.attributes.extend(["startswith", "endswith"])

        keys = set()

        def extract_keys(cfg: Union[DictConfig, Dict[str, Any]]) -> None:
            for key, value in cfg.items():
                if isinstance(value, (dict, DictConfig)):
                    extract_keys(value)
                keys.add(key)

        extract_keys(self.config)
        model.attributes.extend(keys)

        return Expr(expr, model=model).eval(self.config)

    def reason(self, expr: str) -> str:  # pragma: no cover
        return f"Expression '{expr}' evaluated to True."


class Exists(AbstractFilter):
    def filter(self, path: str) -> bool:
        """Filter a configuration based on the existence of a file or directory relative
        to the job output directory.

        Args:
            path: The path to the file or directory to check for existence.

        Returns:
            True if the file or directory exists, False otherwise.
        """
        return os.path.exists(os.path.join(self.directory, path))

    def reason(self, path: str) -> str:  # pragma: no cover
        p = os.path.join(self.directory, path)
        name = "File" if os.path.isfile(p) else "Directory"
        return f"{name} '{path}' exists in directory '{self.directory}'."
