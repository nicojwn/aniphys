# Animation Logic Specification

## Purpose

`animation_logic.py` contains the high-level helpers that most users interact
with.

The two public helpers are:

- `animator(...)`
- `generate_animation(...)`

## `animator(...)`

Builds a list of `GraphMatrix` frames from equations and changing parameters.

```python
frames = animator(
    equation,
    parameter=np.linspace(0, 1, 100),
)
```

Input rules:

- each callable creates one graph with one curve,
- each list of callables creates one graph with multiple curves,
- keyword arrays define frame-by-frame parameter values,
- scalar keyword values are applied to every frame,
- all keyword arrays must have the same length.

The returned value is:

```python
list[GraphMatrix]
```

## `generate_animation(...)`

Turns a list of `GraphMatrix` frames into a Matplotlib `FuncAnimation`.

```python
ani = generate_animation(frames)
```

The first `GraphMatrix` owns the displayed figure. Later matrices provide the
frame data copied into that first figure during playback.

## Typical Workflow

```python
frames = animator(equation, parameter=np.linspace(0, 1, 100))

frames[0].graphs[0].axes.set_xlabel("x")
frames[0].graphs[0].axes.set_ylabel("y")

ani = generate_animation(frames)
plt.show()
```

