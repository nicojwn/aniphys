import numpy as np

from aniphys.animate import animator, generate_animation

# Prerequisites:
# - 01_minimal_template.py: basic animator/generate_animation usage and display behavior.
# - 02_example_animation.py: default-domain animation with one changing parameter.

"""
This example shows how to animate the function $\sin(kx)$ on the domain $x\in[0,2\pi]$
as the parameter $k$ increases from $1$ to $10$.
"""


# First express the sine function as a Python function.
# The first argument is always the x-domain.
# Any later arguments become parameters that AniPhys varies between frames.
def wave(x, k=1):
    return np.sin(k * x)


# We want 120 animation frames, with k moving from 1 to 10.
# AniPhys will evaluate `wave(x, k=...)` once for each entry in `parameter_evolution`.
frame_count = 120
parameter_evolution = np.linspace(1, 10, frame_count)

# Here we choose the explicit x-domain to plot on.
resolution = 1000
domain = np.linspace(0, 2 * np.pi, resolution)

# `animator(...)` reuses the same domain for every frame and varies `k`.
frames = animator(wave, domain=domain, k=parameter_evolution)


animation = generate_animation(frames, show=True)
