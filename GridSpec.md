# Grid — Consumer Specification

## Purpose

`Curve` provides a minimal, consistent interface for generating and updating a **single plotted line per animation frame**.

Each instance represents:

* one domain (x-values),
* one equation,
* one parameter state,
* one `Line2D` object.

It is designed for **frame-by-frame recomputation** with mutable parameters.

---

# Core Model

## Conceptual mapping

```
(domain) ──▶ line_equation(domain, **params) ──▶ y-values ──▶ Line2D
```

* The domain is fixed per instance (unless explicitly regenerated).
* The equation maps the domain to y-values.
* Parameters can be updated between frames.

---

# Requirements

## 1. Equation contract

The provided function **must** satisfy:

```python
y = f(domain: np.ndarray, **params) -> array-like
```

Constraints:

* First argument:

  * Must accept a 1D numpy array (`domain`)
* Return value:

  * Must be 1-dimensional
  * Must be numeric
  * Must have length equal to `len(domain)`

Supported styles:

* **Vectorized (preferred):**

  ```python
  def f(x, a, b):
      return a * np.sin(b * x)
  ```

* **Scalar (fallback supported):**

  ```python
  def f(x, a, b):
      return a * math.sin(b * x)
  ```

Unsupported:

* Returning multi-dimensional arrays
* Returning non-numeric data
* Using `*args` or `**kwargs` in the equation signature

---

## 2. Domain definition

The domain is defined by:

* `number_of_grid_points` (N)
* `step` (Δx)

Generated as:

```
[-N/2 * step, ..., +N/2 * step)
```

Properties:

* 1D numpy array
* evenly spaced
* symmetric around zero
* length exactly `number_of_grid_points`

Constraints:

* `number_of_grid_points > 0`
* `step > 0`

---

## 3. Equation parameters

* Extracted automatically from the equation signature
* Stored as instance attributes
* Mutable between frames

Example:

```python
def f(x, amplitude=1.0, frequency=2.0):
    ...
```

Becomes:

```python
grid.amplitude
grid.frequency
```

Behavior:

* Default values are respected
* Missing defaults → initialized as `None`
* Can be updated at any time

---

# Lifecycle

## 1. Initialization

```python
grid = Grid(
    line_equation=f,
    number_of_grid_points=1000,
    step=0.01,
    line_colour="blue"
)
```

Effects:

* Domain is generated
* Equation parameters are extracted
* `Line2D` object is created (x-data set, y-data empty)

---

## 2. Parameter update

```python
grid.generate_line(amplitude=2.0)
```

Behavior:

* Only provided parameters are updated
* Unspecified parameters retain previous values

---

## 3. Computation

Internally:

* Parameters are collected from instance attributes
* Equation is evaluated
* Vectorization is detected once and cached
* Output is validated

---

## 4. Line update

* `Line2D.set_ydata(...)` is called
* X-data remains unchanged
* Line is ready for rendering

---

# Guarantees

After `generate_line(...)`:

* `line.get_xdata()` is unchanged
* `line.get_ydata()`:

  * is 1D
  * is numeric
  * has length `number_of_grid_points`

---

# Error Handling

The class raises:

* `TypeError`

  * invalid argument types
  * non-numeric outputs
* `ValueError`

  * invalid parameter names
  * shape mismatches
  * invalid domain configuration

No silent failures.

---

# Performance Characteristics

* Domain generation: O(N)
* Vectorized compute: O(N)
* Scalar fallback: O(N) with Python loop (slower)
* Vectorization detection: performed once per instance

---

# Usage Pattern

Typical animation loop:

```python
for t in frames:
    grid.generate_line(amplitude=t)
    ax.draw_artist(grid.line)
```

Multiple lines:

```python
grids = [Grid(f1), Grid(f2), Grid(f3)]

for frame in frames:
    for g in grids:
        g.generate_line(...)
```

---

# Non-Goals

* Multi-line output per grid
* Multi-dimensional domains
* Automatic axis scaling
* State history across frames

Each `Curve` is intentionally **stateless across frames except for parameters**.

---

# Summary

A `Curve` is a thin abstraction over:

* domain generation,
* parameterized function evaluation,
* matplotlib line updating.

It enforces:

* strict shape correctness,
* explicit parameter control,
* predictable per-frame behavior.
