import numpy as np

from aniphys.animate import animator


# Any parameter passed as an array changes frame by frame.
def gaussian(x, center=0, width=1):
    return np.exp(-((x - center) / width) ** 2)


# Arrays for changing parameters must all have the same length.
frames = animator(
    gaussian,
    center=np.linspace(-2, 2, 100),
    width=np.linspace(0.5, 1.5, 100),
)
