# Curve Specification

## Purpose

`Curve` represents one mathematical curve on one set of axes for one animation
frame.

It owns:

- one x-domain,
- one equation,
- one set of equation parameters,
- one Matplotlib `Line2D` object.

## Equation Contract

The equation must accept the domain as its first argument:

```python
def equation(x, parameter=1):
    return parameter * x
```

The return value must be one-dimensional, numeric, and have the same length as
the generated domain.

## Parameters

`Curve` inspects the equation signature and turns all parameters after the first
argument into mutable attributes.

```python
def wave(x, k=1):
    return np.sin(k * x)


curve = Curve(wave)
curve.k = 2
```

`update_line(...)` can update any known parameter and recompute the y-data:

```python
curve.update_line(k=3)
```

Unknown parameters raise a `ValueError`.

## Domain

The x-domain is generated from:

- `number_of_grid_points`
- `step`

The domain is symmetric around zero and has exactly
`number_of_grid_points` samples.

## Key Methods

- `update_line(**equation_parameters)`: updates parameters and recomputes line
  y-data.
- `label`: optional identifier used by `LegendTracker` callbacks.

## Typical Use

Most users should create curves through `animator(...)`. Use `Curve` directly
when you need lower-level control over domains, labels, or manual frame
construction.

