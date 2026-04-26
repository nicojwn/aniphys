import numpy as np

from aniphys.animate import animator, generate_animation

# Prerequisites: none.

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

# Display behavior:
# In a script, `show=True` opens the animation window immediately.
# In a notebook, `show=False` avoids a separate blank matplotlib figure.
# To display the notebook animation while still keeping the variable, make
# `animation` the last line of the cell or call `display(animation)`.
animation = generate_animation(frames, show=True)
