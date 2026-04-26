import numpy as np

from aniphys.animate import animator, generate_animation


# Group equations in a list when they should share one set of axes.
def sine(x, t=0):
    return np.sin(x - t)


def cosine(x, t=0):
    return np.cos(x - t)


# Both curves are drawn on the same plot and updated with the same `t`.
frames = animator(
    [sine, cosine],
    t=np.linspace(0, 2 * np.pi, 100),
)

animation = generate_animation(frames, show=True)
