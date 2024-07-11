from hydra.test_utils.test_utils import TSweepRunner
import pytest
from pytest import mark


@mark.parametrize(
    "config_name, expected",
    [
        ("without_filters", 9),
        ("with_filters", 7),
    ],
)
def test_filter_configurations(
    hydra_sweep_runner: TSweepRunner,
    config_name: str,
    expected: int,
) -> None:
    sweep = hydra_sweep_runner(
        calling_file=__file__,
        calling_module=None,
        config_path="test_config",
        config_name=config_name + ".yaml",
        task_function=None,
        overrides=None,
    )
    with sweep:
        assert sweep.returns is not None
        job_ret = sweep.returns[0]
        assert len(job_ret) == expected


@mark.parametrize(
    "config_name, raises",
    [
        ("missing_filter_type", ValueError),
        ("unknown_filter_type", ValueError),
        ("failing_filter_type", ValueError),
    ],
)
def test_error_types(
    hydra_sweep_runner: TSweepRunner,
    config_name: str,
    raises: Exception,
) -> None:
    sweep = hydra_sweep_runner(
        calling_file=__file__,
        calling_module=None,
        config_path="test_config",
        config_name=config_name + ".yaml",
        task_function=None,
        overrides=None,
    )
    with pytest.raises(raises):
        with sweep:
            ...  # pragma: no cover
