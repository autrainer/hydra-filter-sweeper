from typing import Dict

from hydra_filter_sweeper.filters import (
    AbstractFilter,
    FilterExists,
    FilterExpr,
    FilterScript,
)


FILTERMAP: Dict[str, AbstractFilter] = {
    "exists": FilterExists,
    "expr": FilterExpr,
    "script": FilterScript,
}

__all__ = [
    "AbstractFilter",
    "FilterExists",
    "FilterExpr",
    "FilterScript",
    "FILTERMAP",
]
