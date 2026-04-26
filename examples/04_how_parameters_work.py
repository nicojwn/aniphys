import numpy as np

from aniphys.animate import animator

# Prerequisites:
# - 01_minimal_template.py: basic animator/generate_animation usage and display behavior.
# - 02_example_animation.py: one parameter changing across frames.

# AniPhys matches keyword arguments by parameter name.
def equation(x, a=1, b=0):
    return a * x + b


# `a` changes from frame to frame, while `b` stays fixed for all frames.
frames = animator(
    equation,
    a=np.linspace(1, 4, 60),
    b=2,
)
