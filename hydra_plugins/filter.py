from dataclasses import dataclass, field
import logging
import os
from typing import Any, Dict, List, Optional

from hydra._internal.core_plugins.basic_sweeper import BasicSweeper
from hydra.core.config_store import ConfigStore
from hydra.core.override_parser.types import Override
from omegaconf import OmegaConf

from hydra_filter_sweeper import FILTERMAP


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

    def split_arguments(
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
        overrides = BasicSweeper.split_arguments(overrides, max_batch_size)
        if self.filters:
            return self._filter_overrides_list(overrides)
        return overrides

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
        del config["hydra"]
        for f in self.filters.copy():
            try:
                filter_type = f.pop("type")
            except KeyError:
                raise ValueError(f"Filter type not specified: {f}")
            try:
                filter_cls = FILTERMAP[filter_type]
            except KeyError:
                raise ValueError(f"Filter type '{filter_type}' not supported")
            fail = f.pop("fail", True)
            try:
                should_filter = filter_cls().filter(
                    config=config,
                    directory=run_directory,
                    **f,
                )
            except Exception as e:
                if fail:
                    raise ValueError(f"Filter {f} failed: {e}") from e

            if should_filter:
                override = " ".join(override)
                log.info(f"Filtered: {override} with {filter_type}: {f}")
                return True
        return False
