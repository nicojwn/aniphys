import numpy as np

from aniphys.animate import animator


# AniPhys matches keyword arguments by parameter name.
def equation(x, a=1, b=0):
    return a * x + b


# `a` changes from frame to frame, while `b` stays fixed for all frames.
frames = animator(
    equation,
    a=np.linspace(1, 4, 60),
    b=2,
)
