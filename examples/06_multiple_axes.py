import numpy as np

from aniphys.animate import animator


# Separate positional equations create separate axes.
def electric_field(x, t=0):
    return np.sin(x - t)


def intensity(x, t=0):
    return electric_field(x, t) ** 2


# This creates one axes for the field and one for its intensity.
frames = animator(
    electric_field,
    intensity,
    t=np.linspace(0, 2 * np.pi, 100),
)
