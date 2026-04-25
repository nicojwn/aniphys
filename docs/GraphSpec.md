# Graph Specification

## Purpose

`Graph` represents one set of axes in one animation frame.

It owns:

- one or more `Curve` objects,
- optional `LegendTracker` objects,
- one Matplotlib `Axes` object after initialization,
- an optional Matplotlib legend.

## Curves

A graph can contain one curve:

```python
Graph(Curve(equation))
```

or multiple curves plotted on the same axes:

```python
Graph([Curve(equation_1), Curve(equation_2)])
```

## Display Options

- `_generate_colours`: when true, assigns colours from the default colour map.
- `_auto_scale_axes`: used by `generate_animation(...)` to compute fixed global
  axis limits across all frames.

`animator(...)` creates graphs with both options enabled by default.

## Key Methods

- `init_graph(axes, row=None, col=None)`: attaches curves and legends to a
  Matplotlib axes.
- `update_lines()`: recomputes all contained curves.
- `update_legend()`: refreshes legend text from legend trackers.

## Typical Use

Most users should not need to construct `Graph` directly. Use it when you need
manual control over which curves share an axes.

