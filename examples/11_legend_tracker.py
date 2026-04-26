import numpy as np

from aniphys.animate import animator, generate_animation
from aniphys.frame_objects import LegendTracker


def wave(x, k=1):
    return np.sin(k * x)


# Legend tracker callbacks receive curves by their auto-generated labels.
def show_k(curve_0_0):
    return f"{curve_0_0.k:.2f}"


# The legend text updates on every frame as `k` changes.
frames = animator(
    wave,
    legend_trackers=[LegendTracker("k", show_k)],
    k=np.linspace(1, 5, 80),
)

animation = generate_animation(frames, show=True)
