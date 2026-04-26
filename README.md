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
import matplotlib.pyplot as plt

from aniphys import animator, generate_animation


def wave(x, k=1):
    return np.sin(k * x)


domain = np.linspace(0, 2 * np.pi, 1000)
frames = animator(wave, domain=domain, k=np.linspace(1, 5, 80))
ani = generate_animation(frames, show=True)
```

## Documentation

- [Student Guide](STUDENT_GUIDE.md)
- [Curve specification](docs/CurveSpec.md)
- [LegendTracker specification](docs/LegendTrackerSpec.md)
- [Graph specification](docs/GraphSpec.md)
- [GraphMatrix specification](docs/GraphMatrixSpec.md)
- [Animation helper specification](docs/AnimationLogicSpec.md)
