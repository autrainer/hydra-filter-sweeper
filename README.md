# Hydra Filter Sweeper Plugin

[![PyPI Version](https://img.shields.io/pypi/v/hydra-filter-sweeper?logo=pypi&logoColor=b4befe&color=b4befe)](https://pypi.org/project/hydra-filter-sweeper/)
[![Python Versions](https://img.shields.io/pypi/pyversions/hydra-filter-sweeper?logo=python&logoColor=b4befe&color=b4befe)](https://pypi.org/project/hydra-filter-sweeper/)
[![License](https://img.shields.io/badge/license-MIT-b4befe?logo=c)](https://github.com/autrainer/hydra-filter-sweeper/blob/main/LICENSE)

`hydra-filter-sweeper` is a plugin for [Hydra](https://hydra.cc/) that extends the [basic sweeper](https://hydra.cc/docs/tutorials/basic/running_your_app/multi-run/#sweeper) by the addition of filters, enabling more targeted parameter sweeps.

The plugin is compatible with any [Hydra launcher plugin](https://hydra.cc/docs/tutorials/basic/running_your_app/multi-run/#launcher).
The minimum required Hydra version is `1.3.2`.

## Features

**Customizable Filters**

- Apply [expressions](#expression-filter-expr), [existence checks](#exists-filter-exists), or [custom filter classes](#class-filter-class) to the sweep.

**Flexible Filter Conditions**

- Include fail-safe conditions to gracefully handle possible exceptions raised by filters.

**Interpolation Support**

- Utilize [OmegaConf's interpolation syntax](https://omegaconf.readthedocs.io/en/latest/usage.html#variable-interpolation) to reference configuration values.

## Installation

To install the plugin, use pip:

```bash
pip install hydra-filter-sweeper
```

## Usage

To use `hydra-filter-sweeper`, override the default sweeper with `filter` at the end of the defaults list.

Filters are specified as a list of dictionaries and can be of type `expr`, `exists`, or `class`.

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
      - type: expr
        expr: foo == 1 and bar == "two"
      - type: exists
        path: some_directory/some.file
      - type: class
        target: some_filter.SomeFilter
        some_arg: ${some_value}
```

## Filters

### Expression Filter (`expr`)

Filter configurations based on a Python expression that evaluates to `True` or `False`.
The context of the expression is the configuration itself.
The configuration is excluded if the expression evaluates to `True`.

**Parameters**:

- `expr` (_str_): Python expression to evaluate.
- `fail` (_bool_): Whether to fail if the expression raises an exception. Default is `True`.

**Example Configuration**

```yaml
hydra/sweeper/filters:
  - type: expr
    expr: foo == 1 and bar == "two"
  - type: expr
    expr: bar == ${some_value}
  - type: expr
    expr: undefined == 1 and bar == "two"
    fail: false
```

### Exists Filter (`exists`)

Checks if a specified file or directory exists in the run's directory.
The configuration is excluded if the file or directory exists.

**Parameters**:

- `path` (_str_): Path to the file or directory to check if it exists in the run's directory.
- `fail` (_bool_): Whether to fail if the expression raises an exception. Default is `True`.

**Example Configuration**

```yaml
hydra/sweeper/filters:
  - type: exists
    path: some_directory/some.file
  - type: exists
    path: some_directory
  - type: exists
    path: some_directory/${some_value}.file
  - type: exists
    path: null
    fail: false
```

### Class Filter (`class`)

Applies a custom filter class to the sweep.
The configuration is excluded if the filter method returns `True`.

**Parameters**:

- `target` (_str_): Python relative import path to the class.
- `*` (_Any_): Additional keyword arguments passed to the filter method of the class.
- `fail` (_bool_): Whether to fail if the expression raises an exception. Default is `True`.

**Example Configuration**

```yaml
hydra/sweeper/filters:
  - type: class
    target: some_filter.SomeFilter
    some_arg: ${some_value}
  - type: class
    target: some_filter.NonExistentFilter
    some_arg: ${some_value}
    fail: false
```

The `SomeFilter` class should inherit from `AbstractFilter` and implement the `filter`
method that returns `True` if the configuration should be excluded.

The `filter` method receives the configuration, the run's directory, and any additional keyword arguments as parameters.

```python
from omegaconf import DictConfig

from hydra_filter_sweeper import AbstractFilter


class SomeFilter(AbstractFilter):
    def filter(self, config: DictConfig, directory: str, some_arg: str) -> bool:
        return config.foo == 1 and config.bar == "two" and some_arg == "four"
```

## Contributing

Contributions are welcome!
For bug reports or requests, please [submit an issue](https://github.com/autrainer/hydra-filter-sweeper/issues).

To contribute, please fork the repository and submit a [pull request](https://github.com/autrainer/hydra-filter-sweeper/pulls).

We use [Poetry](https://python-poetry.org/) for dependency management,
[Ruff](https://astral.sh/ruff) for code formatting,
[codespell](https://github.com/codespell-project/codespell) for spell checking,
[pytest](https://docs.pytest.org/en/stable/) for testing,
and [pre-commit](https://pre-commit.com/) for managing the hooks.

Install the development dependencies with:

```bash
poetry install
pre-commit install
```

Both formatting and spell checking are enforced by pre-commit hooks.

We strive for 100% test coverage. To run the tests locally, use:

```bash
pytest
```
