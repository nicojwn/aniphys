# AniPhys

AniPhys is a small Python library for animating mathematical and physical
equations with Matplotlib.

It is designed for students who want to visualize how equations change when
parameters such as time, frequency, width, or amplitude are varied.

## Installation

Install directly from a local checkout:

```bash
cd aniphys
pip install .
```

For editable development:

```bash
cd aniphys
pip install -e .
```

With `uv`:

```bash
cd aniphys
uv sync
```

From a Git repository:

```bash
pip install "git+https://github.com/nicojwn/aniphys.git"
```

Replace `USER/REPO` with the actual repository path.

## Minimal Example

```python
import numpy as np
import matplotlib.pyplot as plt

from aniphys.animation_logic import animator, generate_animation


def wave(x, k=1):
    return np.sin(k * x)


frames = animator(wave, k=np.linspace(1, 5, 80))
ani = generate_animation(frames)

plt.show()
```

## Documentation

- [Student Guide](STUDENT_GUIDE.md)
- [Curve specification](docs/CurveSpec.md)
- [LegendTracker specification](docs/LegendTrackerSpec.md)
- [Graph specification](docs/GraphSpec.md)
- [GraphMatrix specification](docs/GraphMatrixSpec.md)
- [Animation helper specification](docs/AnimationLogicSpec.md)

