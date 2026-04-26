import numpy as np

from aniphys.animate import animator

# Prerequisites:
# - 04_how_parameters_work.py: parameter matching by name.
# - 06_multiple_axes.py: how separate positional equations create separate axes.

# If multiple equations share a parameter name, one keyword drives them all.
def position(x, t=0):
    return np.sin(x - t)


def envelope(x, t=0):
    return np.exp(-((x - t) ** 2))


# Passing `t=...` here updates both equations with the same value per frame.
frames = animator(
    position,
    envelope,
    t=np.linspace(0, 4, 100),
)
