from omegaconf import DictConfig

from hydra_filter_sweeper import AbstractFilter


class TestReturnFilter(AbstractFilter):
    def filter(self, config: DictConfig, directory: str) -> bool:  # type: ignore[override]
        return config.return_value


class TestArgEqualsFilter(AbstractFilter):
    def filter(  # type: ignore[override]
        self,
        config: DictConfig,
        directory: str,
        arg1: str,
        arg2: str,
    ) -> bool:
        return arg1 == arg2


class TestInvalidFilter:
    def filter(self, config: DictConfig, directory: str) -> bool:  # type: ignore[override]
        return True  # pragma: no cover
