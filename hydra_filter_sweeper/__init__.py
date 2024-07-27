from typing import Dict

from hydra_filter_sweeper.filters import (
    AbstractFilter,
    FilterClass,
    FilterExists,
    FilterExpr,
)


FILTERMAP: Dict[str, AbstractFilter] = {
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
