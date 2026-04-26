# aniphys/__init__.py

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

# Required for the animation to work
plt.rcParams["animation.html"] = "jshtml"
plt.rcParams["figure.dpi"] = 150
plt.ioff()

if TYPE_CHECKING:
    from .animate import animator, generate_animation
    from .frame_objects import Curve, Graph, GraphMatrix

__all__ = ["Curve", "Graph", "GraphMatrix", "animator", "generate_animation"]

__version__ = "0.1.0"


def __getattr__(name: str):
    if name in __all__:
        from .animate import animator, generate_animation
        from .frame_objects import Curve, Graph, GraphMatrix

        exports = {
            "Curve": Curve,
            "Graph": Graph,
            "GraphMatrix": GraphMatrix,
            "animator": animator,
            "generate_animation": generate_animation,
        }

        return exports[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
