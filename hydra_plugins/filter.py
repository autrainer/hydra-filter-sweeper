from copy import deepcopy
from dataclasses import dataclass, field
import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union

import hydra
from hydra._internal.core_plugins.basic_sweeper import BasicSweeper
from hydra.core.config_store import ConfigStore
from hydra.core.override_parser.types import Override
from hydra.errors import InstantiationException
from omegaconf import OmegaConf

from hydra_filter_sweeper import AbstractFilter


log = logging.getLogger(__name__)


@dataclass
class FilterSweeperConfig:
    _target_: str = "hydra_plugins.filter.FilterSweeper"
    max_batch_size: Optional[int] = None
    params: Dict[str, Any] = field(default_factory=dict)
    filters: List[str] = field(default_factory=list)


ConfigStore.instance().store(
    group="hydra/sweeper", name="filter", node=FilterSweeperConfig
)


class FilterSweeper(BasicSweeper):
    """
    `FilterSweeper` extends the hydra `BasicSweeper` and provides additional
    functionality for filtering overrides based on specified filters.
    """

    def __init__(
        self,
        max_batch_size: Optional[int],
        params: Optional[Dict[str, str]] = None,
        filters: Optional[List[dict]] = None,
    ) -> None:
        """Filter configurations based on a list of filters.

        Args:
            max_batch_size: The maximum batch size for the sweeper.
            params: Sweeper override parameters.
            filters: A list of filters to apply to the overrides.
        """
        super().__init__(max_batch_size, params)
        self.filters = filters

    def split_arguments(  # type: ignore[override]
        self,
        overrides: List[Override],
        max_batch_size: Optional[int],
    ) -> List[List[List[str]]]:
        """
        Splits the overrides into batches and applies the filters.

        Args:
            overrides: The list of overrides to split.
            max_batch_size: The maximum batch size for the sweeper.

        Returns:
            The batched and filtered overrides.

        """
        ov = BasicSweeper.split_arguments(overrides, max_batch_size)
        if self.filters:
            return self._filter_overrides_list(ov)
        return ov

    def _filter_overrides_list(
        self,
        overrides: List[List[List[str]]],
    ) -> List[List[List[str]]]:
        """
        Filters the overrides based on the specified filters.

        Args:
            overrides: The list of overrides to filter.

        Returns:
            The filtered overrides.

        """
        idx = 0
        out_overrides = []
        for batch in overrides:
            out_batch = []
            for override in batch:
                if not self._filter_override(override, idx=idx):
                    idx += 1
                    out_batch.append(override)
            if out_batch:
                out_overrides.append(out_batch)
        return out_overrides

    @staticmethod
    def _split_cfg(filter: Union[str, Dict[str, Any]]) -> Tuple[str, Dict[str, Any]]:
        if isinstance(filter, str):
            return filter, {}

        key = next(iter(filter.keys()))  # assuming only one key or first is relevant
        if len(filter.keys()) == 1:
            return key, filter[key]

        msg = (
            f"Multiple keys found in filter definition:\n\t{filter}\n"
            "This is likely due to missing indentation."
        )
        log.warning(msg)
        filter.pop(key)
        return key, filter

    @staticmethod
    def _instantiate(key: str, **kwargs: Any) -> AbstractFilter:
        try:
            kwargs.setdefault("_convert_", "all")
            kwargs.setdefault("_recursive_", False)
            return hydra.utils.instantiate({"_target_": key, **kwargs})
        except InstantiationException as e:
            raise ValueError(f"Failed to instantiate filter {key}: {e}") from e

    def _filter_override(self, override: List[str], idx: int) -> bool:
        """
        Applies a single filter to an override.

        Args:
            override: The override to filter.
            idx: The index of the override.

        Returns:
            True if the override should be filtered, False otherwise.

        Raises:
            ValueError: If the filter type is not specified, not supported,
            or fails and `fail` is `True`.

        """
        if not self.config or not self.hydra_context:
            return False  # pragma: no cover
        config = self.hydra_context.config_loader.load_sweep_config(
            self.config,
            override,
        )
        OmegaConf.set_struct(config, False)
        OmegaConf.resolve(config)
        run_directory = os.path.join(
            config.hydra.sweep.dir,
            config.hydra.sweep.get("subdir", str(idx)),
        )
        if not self.filters:
            return False  # pragma: no cover
        del config["hydra"]
        for f in self.filters.copy():
            filter_type, kwargs = self._split_cfg(f)
            should_fail = kwargs.pop("_fail_", True)
            should_log = kwargs.pop("_log_", True)
            filter_cls = self._instantiate(
                filter_type,
                config=deepcopy(config),
                directory=run_directory,
            )
            try:
                should_filter = filter_cls.filter(**kwargs)
            except Exception as e:
                if should_fail:
                    raise ValueError(f"Filter {f} failed: {e}") from e
                should_filter = False

            if should_filter:
                if should_log:
                    msg = f"Filtered: {' '.join(override)} with '{filter_type}'"
                    reason = filter_cls.reason(**kwargs)
                    if reason:
                        msg += f": {reason}"
                    else:  # pragma: no cover
                        msg += "."
                    log.info(msg)
                return True
        return False
