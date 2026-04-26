import numpy as np

from aniphys.animate import animator


def sine(x, t=0):
    return np.sin(x - t)


def cosine(x, t=0):
    return np.cos(x - t)


def intensity(x, t=0):
    return np.sin(x - t) ** 2


# A list creates multiple curves on one axes; a separate callable creates
# another axes.
frames = animator(
    [sine, cosine],
    intensity,
    t=np.linspace(0, 2 * np.pi, 100),
)
