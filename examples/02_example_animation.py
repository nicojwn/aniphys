import numpy as np

from aniphys.animate import animator, generate_animation

# Prerequisites:
# - 01_minimal_template.py: basic animator/generate_animation usage and display behavior.


# AniPhys calls the equation with the current x-domain as the first argument.
def wave(x, k=1):
    return np.sin(k * x)


# Varying `k` across this array produces one animation frame per entry.
parameter_evolution = np.linspace(1, 5, 80)

# Without `domain=...`, AniPhys uses its default generated x-domain.
frames = animator(wave, k=parameter_evolution)

animation = generate_animation(frames, show=True)
