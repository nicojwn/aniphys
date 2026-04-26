# AniPhys Student Guide

AniPhys helps you animate mathematical functions $f(x)$ while changing one
or more parameters. It is meant for situations like:

- How does a sine wave change when its frequency changes?
- How does a Gaussian wave packet move as time changes?
- How does a potential curve change when a parameter is varied?

You express you mathematical function using python and AniPhys turns it into Matplotlib
plots and animations.

## Basic Idea

The basic idea is best illustrated using an example. Say you want to animate the
evolution of $\sin(kx)$ as $k$ increases $1$ to $10$ on the domain $x\in[0,2\pi]$.

### 1. Define the function
First you would have to express the function in python as below

```python
import numpy as np

def wave(x, k=1):
    return np.sin(k * x)
```

The following things are worth noticing:
- Using numpy as generally recommended for faster rendering.
- The python function needs at least one argument.
- The first argument is always the domain with any additional arguments being parameters which you can animate.

### 2. Define the domain and parameter evolution
In order to plot and animate the function, AniPhys requires an array of input values $x$ and
an array of parameter values $k$. The idea is that for each entry of the parameter
array, the function is plotted given that parameter on the domain. The resulting plots
are then spliced together forming a moving image.

The numpy library makes very easy with the
`np.linspace` function:
1. Given the domain $[0,2\pi]$ we'll define $1000$ points (to make the plot look
   smooth).
2. Given the parameter should increase from $1$ to $10$ we'll define $120$ points (which
   will yield an animation with $120$ frames).

To make the values more intuitive we assign the variables `resolution` and `frame_count`.
```python
import numpy as np

def wave(x, k=1):
    return np.sin(k * x)

resolution = 1000
frame_count = 120

domain = np.linspace(0, 2 * np.pi, resolution)
parameter_evolution = np.linspace(1, 10, frame_count)
```
Given these building blocks the `animator` and `generate_animation` functions can now
generate the animation. The `animator` function packages the information in the
`domain` and `parameter_evolution` arrays with the `wave` function to yield the frames
which are then turned into an animation by the `generate_animation` function.

```python
import numpy as np
from aniphys.animate import animator, generate_animation

def wave(x, k=1):
    return np.sin(k * x)

resolution = 1000
frame_count = 120

domain = np.linspace(0, 2 * np.pi, resolution)
parameter_evolution = np.linspace(1, 10, frame_count)

frames = animator(wave, domain=domain, k=parameter_evolution)
animation = generate_animation(frames, show=True)
```
Notice the following things:
- The `animator` function takes two types of arguments: The function to animate and the
  parameters to vary between frames, plus an optional `domain=...` keyword.
- The `animator` function can infer the names of the `wave` function's arguments so that
  passing the keyword argument `k=[1,2,3,4]` makes it generate an animation with frames
  `wave(x, k=1)`, `wave(x, k=2)`, `wave(x, k=3)`, and `wave(x, k=4)`.
- The `generate_animation` function then takes these generated frames and turns them
  into an animation. Passing `show=True` makes the animation immediately appear.


## Example animation

```python
import numpy as np
import matplotlib.pyplot as plt

from aniphys.animation_logic import animator, generate_animation


def wave(x, k=1):
    return np.sin(k * x)


frames = animator(
    wave,
    k=np.linspace(1, 5, 80),
)

ani = generate_animation(frames)
plt.show()
```

This creates 80 frames. In the first frame `k = 1`, and in the last frame
`k = 5`.

## How Parameters Work

The keyword arguments you give to `animator(...)` are matched by name.

```python
def equation(x, a=1, b=0):
    return a * x + b


frames = animator(
    equation,
    a=np.linspace(1, 4, 60),
    b=2,
)
```

Here:

- `a` changes over 60 frames.
- `b` is fixed at `2` for every frame.

If two equations both have a parameter called `t`, then `t=...` is applied to
both equations.

```python
def position(x, t=0):
    return np.sin(x - t)


def envelope(x, t=0):
    return np.exp(-(x - t) ** 2)


frames = animator(
    position,
    envelope,
    t=np.linspace(0, 4, 100),
)
```

This creates two separate axes, and both curves evolve with the same value of
`t` in each frame.

## Multiple Curves on the Same Axes

Use a list of equations when you want several curves on the same plot.

```python
def sine(x, t=0):
    return np.sin(x - t)


def cosine(x, t=0):
    return np.cos(x - t)


frames = animator(
    [sine, cosine],
    t=np.linspace(0, 2 * np.pi, 100),
)

ani = generate_animation(frames)
plt.show()
```

This creates one set of axes containing two curves.

## Multiple Axes

Use several positional arguments when you want several plots.

```python
def electric_field(x, t=0):
    return np.sin(x - t)


def intensity(x, t=0):
    return electric_field(x, t) ** 2


frames = animator(
    electric_field,
    intensity,
    t=np.linspace(0, 2 * np.pi, 100),
)
```

This creates two axes:

- one for `electric_field`
- one for `intensity`

## Combining Both

You can combine both ideas:

```python
frames = animator(
    [sine, cosine],   # first axes: two curves
    intensity,        # second axes: one curve
    t=np.linspace(0, 2 * np.pi, 100),
)
```

## Several Changing Parameters

If several parameters are arrays, they must have the same length.

```python
def gaussian(x, center=0, width=1):
    return np.exp(-((x - center) / width) ** 2)


frames = animator(
    gaussian,
    center=np.linspace(-2, 2, 100),
    width=np.linspace(0.5, 1.5, 100),
)
```

In frame 0, AniPhys uses the first value of `center` and the first value of
`width`. In frame 1, it uses the second value of each, and so on.

This will not work because the arrays have different lengths:

```python
frames = animator(
    gaussian,
    center=np.linspace(-2, 2, 100),
    width=np.linspace(0.5, 1.5, 50),
)
```

## Legends That Show Parameter Values

AniPhys can update legend text during an animation using `LegendTracker`.

The helper labels curves automatically:

```text
curve_0_0
curve_0_1
curve_1_0
...
```

The first number is the axes number. The second number is the curve number on
that axes.

Example:

```python
import numpy as np
import matplotlib.pyplot as plt

from aniphys.animation_logic import animator, generate_animation
from aniphys.frame_objects import LegendTracker


def wave(x, k=1):
    return np.sin(k * x)


def show_k(curve_0_0):
    return f"{curve_0_0.k:.2f}"


frames = animator(
    wave,
    legend_trackers=[LegendTracker("k", show_k)],
    k=np.linspace(1, 5, 80),
)

ani = generate_animation(frames)
plt.show()
```

The legend will display the current value of `k`.

## Editing the Figure Before Animating

`animator(...)` returns a list of `GraphMatrix` objects. The first object owns
the figure that will be displayed.

You can edit it before calling `generate_animation(...)`.

```python
frames = animator(wave, k=np.linspace(1, 5, 80))

first_frame = frames[0]
graph = first_frame.graphs[0]

graph.axes.set_title("Changing the wave number")
graph.axes.set_xlabel("x")
graph.axes.set_ylabel("sin(kx)")

ani = generate_animation(frames)
plt.show()
```

## Common Mistakes

### The parameter name must match the function

This works:

```python
def wave(x, k=1):
    return np.sin(k * x)


frames = animator(wave, k=np.linspace(1, 5, 80))
```

This does not work, because the function has no parameter named `frequency`:

```python
frames = animator(wave, frequency=np.linspace(1, 5, 80))
```

### The first argument is the x-axis

AniPhys assumes the first argument is the horizontal plotting variable.

Good:

```python
def equation(x, t=0):
    return np.sin(x - t)
```

Avoid:

```python
def equation(t, x=0):
    return np.sin(x - t)
```

### Use NumPy functions for array input

The equation receives many `x` values at once, so use NumPy functions:

```python
def good(x):
    return np.sin(x)
```

Avoid Python's `math.sin`, which expects only one number:

```python
import math


def bad(x):
    return math.sin(x)
```

## Minimal Template

```python
import numpy as np
import matplotlib.pyplot as plt

from aniphys.animation_logic import animator, generate_animation


def equation(x, parameter=1):
    return np.sin(parameter * x)


frames = animator(
    equation,
    parameter=np.linspace(1, 5, 100),
)

frames[0].graphs[0].axes.set_xlabel("x")
frames[0].graphs[0].axes.set_ylabel("y")
frames[0].graphs[0].axes.set_title("My animation")

ani = generate_animation(frames)
plt.show()
```
