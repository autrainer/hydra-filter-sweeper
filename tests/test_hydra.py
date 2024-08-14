from hydra.core.plugins import Plugins
from hydra.plugins.sweeper import Sweeper
from hydra.test_utils.launcher_common_tests import (
    BatchedSweeperTestSuite,
    IntegrationTestSuite,
    LauncherTestSuite,
)
from pytest import mark

from hydra_plugins.filter import FilterSweeper


def test_discovery() -> None:
    assert FilterSweeper.__name__ in [
        x.__name__ for x in Plugins.instance().discover(Sweeper)
    ]


@mark.parametrize(
    "launcher_name, overrides",
    [
        (
            "basic",
            ["hydra/sweeper=filter"],
        )
    ],
)
class TestFilterSweeper(LauncherTestSuite): ...


@mark.parametrize(
    "launcher_name, overrides",
    [
        (
            "basic",
            [
                "hydra/sweeper=filter",
                "hydra.sweeper.max_batch_size=2",
            ],
        )
    ],
)
class TestFilterSweeperWithBatching(BatchedSweeperTestSuite): ...


@mark.parametrize(
    "task_launcher_cfg, extra_flags",
    [
        (
            {},
            [
                "-m",
                "hydra/sweeper=filter",
                "hydra/launcher=basic",
            ],
        )
    ],
)
class TestFilterSweeperIntegration(IntegrationTestSuite): ...
