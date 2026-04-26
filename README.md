# AniPhys

AniPhys is a small Python library for animating mathematical equations with Matplotlib.
It is designed for students who want to visualize how equations change when parameters
such as time, frequency, width, or amplitude are varied.

## Installation

From the Git repository:

```bash
pip install "git+https://github.com/nicojwn/aniphys.git"
```

Directly from a local checkout:

```bash
cd aniphys
pip install .
```


## Minimal Example

```python
import numpy as np

from aniphys.animate import animator, generate_animation


def wave(x, k=1):
    return np.sin(k * x)


domain = np.linspace(0, 2 * np.pi, 1000)
frames = animator(wave, domain=domain, k=np.linspace(1, 5, 80))
animation = generate_animation(frames, show=True)
```

## Display Behavior

- In a script, `generate_animation(..., show=True)` opens the animation window.
- In a notebook, prefer `show=False` and leave the returned animation as the
  last line of the cell.
- If you assign the animation to a variable in a notebook, display it with the
  last line `animation` or `display(animation)`.

Notebook pattern:

```python
animation = generate_animation(frames, show=False)
animation
```

## Example Progression

- [01_minimal_template.py](examples/01_minimal_template.py): baseline workflow
- [02_example_animation.py](examples/02_example_animation.py): one changing parameter
- [03_sinkx.py](examples/03_sinkx.py): explicit custom domain
- [04_how_parameters_work.py](examples/04_how_parameters_work.py): parameter matching
- [05_several_changing_parameters.py](examples/05_several_changing_parameters.py): multiple varying parameters
- [06_multiple_axes.py](examples/06_multiple_axes.py): one equation per axes
- [07_multiple_curves_same_axes.py](examples/07_multiple_curves_same_axes.py): multiple curves on one axes
- [08_shared_parameter_across_axes.py](examples/08_shared_parameter_across_axes.py): shared parameters across graphs
- [09_combining_axes_and_curves.py](examples/09_combining_axes_and_curves.py): mixed layout
- [10_editing_figure.py](examples/10_editing_figure.py): edit axes before playback
- [11_legend_tracker.py](examples/11_legend_tracker.py): animated legends

The same sequence is available in [examples.ipynb](examples.ipynb).

## Documentation

- [Student Guide](STUDENT_GUIDE.md)
- [Curve specification](docs/CurveSpec.md)
- [LegendTracker specification](docs/LegendTrackerSpec.md)
- [Graph specification](docs/GraphSpec.md)
- [GraphMatrix specification](docs/GraphMatrixSpec.md)
- [Animation helper specification](docs/AnimationLogicSpec.md)
