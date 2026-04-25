# LegendTracker Specification

## Purpose

`LegendTracker` creates dynamic legend text for animation frames.

It stores:

- a legend label prefix,
- a callback function,
- an invisible dummy line used as the legend handle.

## Callback Model

Callbacks receive curves by label. When using `animator(...)`, curves are
automatically labeled:

```text
curve_0_0
curve_0_1
curve_1_0
```

Example:

```python
def show_k(curve_0_0):
    return f"{curve_0_0.k:.2f}"


tracker = LegendTracker("k", show_k)
```

The legend entry becomes:

```text
k=1.00
```

## Key Methods

- `make_tracking_label(curves)`: builds one legend label for a graph.
- `make_tracking_labels(curves, legend_trackers)`: builds all legend labels for
  a graph.
- `dummy_lines(legend_trackers)`: returns invisible lines used by Matplotlib's
  legend system.

## Typical Use

Most users pass trackers into `animator(...)`:

```python
frames = animator(
    wave,
    legend_trackers=[LegendTracker("k", show_k)],
    k=np.linspace(1, 5, 80),
)
```

