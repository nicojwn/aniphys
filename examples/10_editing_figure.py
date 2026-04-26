import numpy as np

from aniphys.animate import animator, generate_animation

# Prerequisites:
# - 01_minimal_template.py: basic animator/generate_animation usage and display behavior.

def wave(x, k=1):
    return np.sin(k * x)


# `animator(...)` returns frame objects before the animation is built.
frames = animator(wave, k=np.linspace(1, 5, 80))

# The first frame owns the matplotlib axes that will be displayed.
graph = frames[0].graphs[0]
graph.axes.set_title("Changing the wave number")
graph.axes.set_xlabel("x")
graph.axes.set_ylabel("sin(kx)")

animation = generate_animation(frames, show=True)
