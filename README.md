# Hydra Filter Sweeper Plugin

`hydra-filter-sweeper` is a plugin for [Hydra](https://hydra.cc/) that extends the [basic sweeper](https://hydra.cc/docs/tutorials/basic/running_your_app/multi-run/#sweeper) by the addition of filters, enabling more targeted parameter sweeps.

`hydra-filter-sweeper` is compatible with any [launcher](https://hydra.cc/docs/tutorials/basic/running_your_app/multi-run/#launcher) and can be used with any Hydra application.

The minimum required Hydra version is 1.3.2.

## Features

- **Customizable Filters**: Apply expressions, existence checks, or custom filter scripts to the sweep.
- **Flexible Filter Conditions**: Include fail-safe conditions to gracefully handle undefined configurations.
- **Dynamic Script Execution**: Execute custom scripts with additional arguments.

## Installation

To install the plugin, use pip:

```bash
pip install hydra-filter-sweeper
```

## Usage

To use `hydra-filter-sweeper`, override the default sweeper with `filter-sweeper` at the end of the defaults list.

Filters are specified as a list of dictionaries and can be of type `expr`, `exists`, or `script`.
If a filters evaluates to `True`, the current configuration is excluded from the sweep.
If no `filters` list is provided or all filters evaluate to `False`, all configurations are included, acting as the default behavior of hydra.

All filters support OmegaConf's [interpolation syntax](https://omegaconf.readthedocs.io/en/latest/usage.html#variable-interpolation) and are automatically resolved.

##### Example Configuration

```yaml
defaults:
  - _self_
  - override hydra/sweeper: filter-sweeper

some_value: four

hydra:
  mode: MULTIRUN
  sweeper:
    params:
      +foo: 1,2,3
      +bar: one, two, three
    filters:
      - type: expr
        expr: "foo == 1 and bar == 'two'"
      - type: expr
        expr: "bar == ${some_value}" # OmegaConf interpolation syntax
      - type: expr
        expr: "undefined == 1 and bar == 'two'"
        fail: False # Fail-safe condition to gracefully handle undefined configurations
      - type: exists
        path: some_folder/some.file
      - type: script
        path: some_folder/some_filter.py
        some_arg: ${some_value} # Additional arguments passed to the script
```

## Filters

#### Expression Filter (`expr`)

Filter parameters based on a Python expression that evaluates to `True` or `False`.
The configuration is excluded if the expression evaluates to `True`.

**Parameters**:

- `expr`: Python expression to evaluate.

#### Exists Filter (`exists`)

Checks if a specified file or directory exists in the run's folder.
The configuration is excluded if the file or directory exists.

**Parameters**:

- `path`: Path to the file or directory to check if it exists.

#### Script Filter (`script`)

Runs a custom Python script as a filter.

A filter has to inherit from `AbstractFilter` and implement the `filter` method.
Additional arguments can be passed to the script and hydra's interpolation syntax is supported.
The configuration is excluded if any of the filters in the script returns `True`.

**Parameters**:

- `path`: Path to the Python script.
- `*`: Additional keyword arguments passed to the script.

**Note**: All classes inheriting from `AbstractFilter` in the script are executed.

##### Example `some_filter.py`:

```python
from hydra_filter_sweeper import AbstractFilter

class SomeFilter(AbstractFilter):
    def filter(self, config, directory, **kwargs) -> bool:
        return config.foo == 1 and config.bar == "two"
```
