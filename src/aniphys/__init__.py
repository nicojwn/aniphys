# aniphys/__init__.py

import matplotlib.pyplot as plt
from typing import TYPE_CHECKING

# Required for the animation to work
plt.rcParams["animation.html"] = "jshtml"
plt.rcParams["figure.dpi"] = 150
plt.ioff()

if TYPE_CHECKING:
    from .frame_objects import Curve, Graph, GraphMatrix

__all__ = ["Curve", "Graph", "GraphMatrix"]

__version__ = "0.1.0"


def __getattr__(name: str):
    if name in __all__:
        from .frame_objects import Curve, Graph, GraphMatrix

        exports = {
            "Curve": Curve,
            "Graph": Graph,
            "GraphMatrix": GraphMatrix,
        }
        return exports[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
