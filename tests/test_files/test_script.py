from omegaconf import DictConfig

from hydra_filter_sweeper import AbstractFilter


class SomeFilter(AbstractFilter):
    def filter(self, config: DictConfig, directory: str, **kwargs) -> bool:
        return config.return_value
