import logging
from pathlib import Path
import tempfile
from typing import Generator, Type

from hydra.test_utils.test_utils import TSweepRunner
import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.mark.parametrize(
    ("config_name", "expected"),
    [
        ("without_filters", 9),
        ("with_filters", 7),
    ],
)
def test_filter_configurations(
    hydra_sweep_runner: TSweepRunner,
    config_name: str,
    expected: int,
    temp_dir: Path,
) -> None:
    sweep = hydra_sweep_runner(
        calling_file=__file__,
        calling_module=None,
        config_path="test_config",
        config_name=config_name + ".yaml",
        task_function=None,
        overrides=None,
        temp_dir=temp_dir,
    )
    with sweep:
        assert sweep.returns is not None
        job_ret = sweep.returns[0]
        assert len(job_ret) == expected


@pytest.mark.parametrize(
    ("config_name", "raises"),
    [
        ("unknown_filter_type", ValueError),
        ("failing_filter_type", ValueError),
    ],
)
def test_error_types(
    hydra_sweep_runner: TSweepRunner,
    config_name: str,
    raises: Type[Exception],
    temp_dir: Path,
) -> None:
    sweep = hydra_sweep_runner(
        calling_file=__file__,
        calling_module=None,
        config_path="test_config",
        config_name=config_name + ".yaml",
        task_function=None,
        overrides=None,
        temp_dir=temp_dir,
    )
    with pytest.raises(raises), sweep:
        ...  # pragma: no cover


def test_suppress_logs(
    hydra_sweep_runner: TSweepRunner,
    temp_dir: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    sweep = hydra_sweep_runner(
        calling_file=__file__,
        calling_module=None,
        config_path="test_config",
        config_name="with_suppressed_filters.yaml",
        task_function=None,
        overrides=None,
        temp_dir=temp_dir,
    )
    with caplog.at_level(logging.INFO), sweep:
        assert sweep.returns is not None
        job_ret = sweep.returns[0]
        assert len(job_ret) == 7

    print(caplog.text)

    assert "Filtered: +foo=1 +bar=two" in caplog.text
    assert "Filtered: +foo=2 +bar=three" not in caplog.text
    assert "+foo=2 +bar=three" not in caplog.text
