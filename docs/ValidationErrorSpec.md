# Validation Error Spec

Use this format for new validation code in `aniphys`.

## Exception Type

- Raise `TypeError` when the type is wrong.
- Raise `ValueError` when the type is acceptable but the value is invalid.

Standard format:

- `{VARIABLE_NAME} must be {TYPE}`
- `{VARIABLE_NAME} must {be|contain|...} {CONDITION}`

Examples:
- `label must be a str`
- `number_of_grid_points must be positive`

## Multi-Argument Validation

When validating several independent arguments in one function or constructor:

1. collect all argument errors first,
2. store them as `dict[str, str]`,
3. raise one combined `ValueError` with `_raise_validation_errors(...)`.

Required format:

```text
Please check the following arguments: <name> -> <problem>; <name> -> <problem>
```

Per-argument message fragments should be short and direct:

- `must be callable`
- `must be a bool`
- `must contain only Curve objects`
- `must not be empty`
- `is not a valid argument`

Example pattern:

```python
errors: dict[str, str] = {}

if foo is not None and not isinstance(foo, int):
    errors["foo"] = "must be an int or None"
elif foo is not None and foo <= 0:
    errors["foo"] = "must be positive"

if kwargs:
    errors.update({name: "is not a valid argument" for name in kwargs})

_raise_validation_errors(errors)
```

## Single Errors

Use a direct exception instead of the combined format when the failure is not
just one bad argument value, for example:

- unknown parameter names,
- mismatched lengths or dimensions,
- out-of-range indices,
- invalid callback or equation behavior,
- computed runtime invariants.

Examples:

- `Unknown equation parameters: kappa`
- `Graph index out of range: expected 0 <= idx < 3, got 5`
- `line_equation must return a one-dimensional result`

## Message Style

- Prefer `must be ...`, `must contain ...`, `must not ...`.
- Keep wording parallel across similar checks.
- Include concrete values only when they help debug the failure.
- Do not use empty exception messages.

## Current Project Pattern

`src/aniphys/frame_objects.py` already follows the preferred aggregate style via
`_raise_validation_errors(...)`.

Keep new validation code consistent with that pattern, and use the same message
shapes in other modules.
