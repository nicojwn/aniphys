# GraphMatrix Specification

## Purpose

`GraphMatrix` represents a full animation frame.

It owns:

- a Matplotlib `Figure`,
- one or more `Graph` objects,
- the subplot grid used to place those graphs.

`generate_animation(...)` treats each `GraphMatrix` in a list as one animation
frame.

## Layout

Graphs are placed into a subplot grid. If no column count is provided:

- one graph uses one column,
- multiple graphs default to two columns.

## Key Methods

- `update_graphs()`: recomputes all graphs and legends in the frame.
- `get_graph(idx=...)`: retrieves a graph by flat index.
- `get_graph(row=..., col=...)`: retrieves a graph by grid coordinate.
- `idx_to_coord(idx)`: converts flat index to `(row, col)`.
- `coord_to_idx(row, col)`: converts `(row, col)` to flat index.

## Typical Use

Most users receive `GraphMatrix` objects from `animator(...)`:

```python
frames = animator(wave, k=np.linspace(1, 5, 80))
first_frame = frames[0]
first_frame.graphs[0].axes.set_title("Changing k")
```

Then pass the full frame list into `generate_animation(...)`.

