import numpy as np

from aniphys.animate import animator, generate_animation


# Replace this equation and parameter with your own problem.
def equation(x, parameter=1):
    return np.sin(parameter * x)


frames = animator(
    equation,
    parameter=np.linspace(1, 5, 100),
)

# The first frame exposes the axes so you can label the plot before playback.
graph = frames[0].graphs[0]
graph.axes.set_xlabel("x")
graph.axes.set_ylabel("y")
graph.axes.set_title("My animation")

animation = generate_animation(frames, show=True)
