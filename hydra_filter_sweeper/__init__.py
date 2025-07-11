from typing import Dict, Type

from hydra_filter_sweeper.filters import (
    AbstractFilter,
    FilterClass,
    FilterExists,
    FilterExpr,
)


FILTERMAP: Dict[str, Type[AbstractFilter]] = {
    "exists": FilterExists,
    "expr": FilterExpr,
    "class": FilterClass,
}

__all__ = [
    "AbstractFilter",
    "FilterExists",
    "FilterExpr",
    "FilterClass",
    "FILTERMAP",
]
