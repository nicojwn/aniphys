"""
Common typing utilities for grid-based plotting.

This module centralizes reusable type aliases used across the codebase,
particularly for numerical arrays, equation callables, and matplotlib-related types.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypeAlias

import numpy as np
from matplotlib.lines import Line2D
from numpy.typing import NDArray

# =========================
# Numerical Types
# =========================

Number: TypeAlias = int | float | np.number

NumericArray: TypeAlias = NDArray[np.float64]
ArrayLike1D: TypeAlias = Iterable[Number] | NDArray[np.float64]


# =========================
# Equation Types
# =========================

# Callable that maps a domain (1D numpy array) + parameters → numeric 1D output
LineEquation: TypeAlias = Callable[..., ArrayLike1D]


# =========================
# Grid / Plot Types
# =========================

Domain: TypeAlias = NDArray[np.float64]
YValues: TypeAlias = NDArray[np.float64]

MatplotlibLine: TypeAlias = Line2D


# =========================
# Parameter Types
# =========================

EquationParameters: TypeAlias = dict[str, Number]


# =========================
# Colour Types
# =========================

# Matplotlib supports many formats; runtime validation is handled via
# matplotlib.colors.is_color_like(...)
ColorLike: TypeAlias = object


# =========================
# Optional Convenience Types
# =========================

MaybeNumber: TypeAlias = Number | None
MaybeArrayLike1D: TypeAlias = ArrayLike1D | None
