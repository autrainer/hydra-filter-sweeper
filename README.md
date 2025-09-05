# Hydra Filter Sweeper Plugin

[![PyPI Version](https://img.shields.io/pypi/v/hydra-filter-sweeper?logo=pypi&logoColor=b4befe&color=b4befe)](https://pypi.org/project/hydra-filter-sweeper/)
[![Python Versions](https://img.shields.io/pypi/pyversions/hydra-filter-sweeper?logo=python&logoColor=b4befe&color=b4befe)](https://pypi.org/project/hydra-filter-sweeper/)
[![License](https://img.shields.io/badge/license-MIT-b4befe?logo=c)](https://github.com/autrainer/hydra-filter-sweeper/blob/main/LICENSE)

`hydra-filter-sweeper` is a plugin for [Hydra](https://hydra.cc/) that extends the [basic sweeper](https://hydra.cc/docs/tutorials/basic/running_your_app/multi-run/#sweeper) by the addition of filters, enabling more targeted parameter sweeps.

The plugin is compatible with any [Hydra launcher plugin](https://hydra.cc/docs/tutorials/basic/running_your_app/multi-run/#launcher).
The minimum required Hydra version is `1.3.2`.

## Features

**Customizable Filters**

- Apply [expressions](#expression-filter), [existence checks](#exists-filter), or [custom filter classes](#custom-filters) to the sweep.

**Flexible Filter Conditions**

- Include fail-safe conditions to gracefully [handle possible exceptions](#fail-and-log-options) or [suppress log messages](#fail-and-log-options).

**Interpolation Support**

- Utilize [OmegaConf's interpolation syntax](https://omegaconf.readthedocs.io/en/latest/usage.html#variable-interpolation) to reference configuration values.

## Installation

Install `hydra-filter-sweeper` via pip:

```bash
pip install hydra-filter-sweeper
```

## Usage

To use `hydra-filter-sweeper`, override the default sweeper with `filter` at the end of the defaults list.

Filters are specified as a list of configurations under the `hydra/sweeper/filters` key.

If any filter evaluates to `True`, the current configuration **is excluded** from the sweep.

If no `filters` list is provided or all filters evaluate to `False`, all configurations are included and the
sweeper resembles the default behavior of Hydra's basic sweeper.

**Example Configuration**

```yaml
defaults:
  - _self_
  - override hydra/sweeper: filter

some_value: four

hydra:
  mode: MULTIRUN
  sweeper:
    params:
      +foo: 1,2,3
      +bar: one, two, three
    filters:
      - hydra_filter_sweeper.Expression:
          expr: foo == 1 and bar == "two"
      - hydra_filter_sweeper.Exists:
          path: some_directory/some.file
      - some_custom_filter.SomeFilter:
          some_arg: ${some_value}
```

## Filters

### Expression Filter

Filter a configuration based on the evaluation of a Python expression using the configuration as context.

All keys in the configuration are added to the attributes list of the evaluation model in addition to lists,
tuples, and safe function calls (e.g., str, int, float, len).

The configuration is excluded if the expression evaluates to `True`.

**Parameters**:

- `expr` (_str_): The Python expression to be evaluated.

**Example Configurations**

```yaml
hydra/sweeper/filters:
  - hydra_filter_sweeper.Expression:
      expr: foo == 1 and bar == "two"
  - hydra_filter_sweeper.Expression:
      expr: bar == ${some_value}
  - hydra_filter_sweeper.Expression:
      expr: undefined == 1 and bar == "two"
      _fail_: false
      _log_: false
```

### Exists Filter

Filter a configuration based on the existence of a file or directory relative to the job output directory.

The configuration is excluded if the file or directory exists.

**Parameters**:

- `path` (_str_): The path to the file or directory to check for existence.

**Example Configurations**

```yaml
hydra/sweeper/filters:
  - hydra_filter_sweeper.Exists:
      path: some_directory/some.file
  - hydra_filter_sweeper.Exists:
      path: some_directory
      _log_: false
  - hydra_filter_sweeper.Exists:
      path: some_directory/${some_value}.file
  - hydra_filter_sweeper.Exists:
      path: null
      _fail_: false
```

### Custom Filters

Filter a configuration using a custom filter class that implements the `hydra_filter_sweeper.AbstractFilter` interface.
The filter class should be specified by its Python relative import path.

The the `filter` method is called with any additional keyword arguments provided in the configuration.

The optional `reason` method can return an explanation for filtering the provided configuration and receives the same arguments as filter.

**Example Configurations**

```python
from hydra_filter_sweeper import AbstractFilter


class SomeFilter(AbstractFilter):
    def filter(self, some_arg: str) -> bool:
        return some_arg == "expected_value"

    def reason(self, some_arg: str) -> str:
        return f"Filtered because 'some_arg' matched the expected value!"

class WithoutArguments(AbstractFilter):
    def filter(self) -> bool:
        return self.config.some_value == "expected_value"

class AnotherFilter(AbstractFilter):
    def filter(self, first_arg: str, second_arg: str) -> bool:
        return first_arg == "expected_value" and second_arg == "another_expected_value"
```

```yaml
hydra/sweeper/filters:
  - some_custom_filter.SomeFilter:
      some_arg: ${some_value}
  - some_custom_filter.WithoutArguments
  - some_custom_filter.AnotherFilter:
      first_arg: ${some_value}
      second_arg: ${another_value}
      _fail_: false
      _log_: false
```

### Fail and Log Options

For all filters, the `_fail_` and `_log_` options can be used to control the behaviour of the filter:

- `_fail_` (_bool_, default: `True`): If `True`, the filter will raise an exception if it fails to evaluate.
  If `False`, the filter will not raise an exception, and the configuration will be included in the sweep.
- `_log_` (_bool_, default: `True`): If `True`, the filter will log a message when it is applied.
  If `False`, no log message is logged.

## Contributing

Contributions are welcome!
For bug reports or requests, please [submit an issue](https://github.com/autrainer/hydra-filter-sweeper/issues).

To contribute, please fork the repository and submit a [pull request](https://github.com/autrainer/hydra-filter-sweeper/pulls).

We use [uv](https://docs.astral.sh/uv/) for dependency management,
[Ruff](https://astral.sh/ruff) for code formatting,
[codespell](https://github.com/codespell-project/codespell) for spell checking,
[pytest](https://docs.pytest.org/en/stable/) for testing,
and [pre-commit](https://pre-commit.com/) for managing the hooks.

Install the development dependencies with:

```bash
uv sync
pre-commit install
```

Both formatting and spell checking are enforced by pre-commit hooks.

We strive for 100% test coverage. To run the tests locally, use:

```bash
pytest
```
