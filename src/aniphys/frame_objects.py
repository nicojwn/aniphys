from __future__ import annotations

import inspect
import keyword
from collections.abc import Callable
from dataclasses import dataclass
from inspect import Parameter, Signature
from typing import Any, overload

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.lines import Line2D

try:
    from .type_defs import (
        ArrayLike1D,
        Domain,
        EquationParameters,
        LineEquation,
        Number,
        YValues,
    )
except ImportError:
    from type_defs import (
        ArrayLike1D,
        Domain,
        EquationParameters,
        LineEquation,
        Number,
        YValues,
    )


@dataclass
class FunctionSpec:
    positional_only: list[str]
    positional: list[str]
    keyword_only: dict[str, Any | inspect._empty]
    var_positional: str | None
    var_keyword: str | None


def parse_signature(func: Callable[..., Any]) -> FunctionSpec:
    sig: Signature = inspect.signature(func)

    positional_only: list[str] = []
    positional: list[str] = []
    var_positional: str | None = None
    keyword_only: dict[str, Any] = {}
    var_keyword: str | None = None

    for param in sig.parameters.values():
        if param.kind is Parameter.POSITIONAL_ONLY:
            positional_only.append(param.name)

        elif param.kind is Parameter.POSITIONAL_OR_KEYWORD:
            positional.append(param.name)

        elif param.kind is Parameter.VAR_POSITIONAL:
            var_positional = param.name

        elif param.kind is Parameter.KEYWORD_ONLY:
            keyword_only[param.name] = param.default

        elif param.kind is Parameter.VAR_KEYWORD:
            var_keyword = param.name

    return FunctionSpec(
        positional_only=positional_only,
        positional=positional,
        keyword_only=keyword_only,
        var_positional=var_positional,
        var_keyword=var_keyword,
    )


def _raise_validation_errors(errors: dict[str, str]) -> None:
    if not errors:
        return

    raise ValueError(
        "Please check the following arguments: "
        + "; ".join([f"{argument} -> {error}" for argument, error in errors.items()])
    )


_MISSING = object()


class Defaults:
    """
    Container for package-level default values used when constructing grids.

    Attributes:
        number_of_grid_points:
            Default number of samples used to build a grid domain.
        step:
            Default spacing between neighboring domain values.
    """

    number_of_grid_points: int = 1000
    step: float = 0.005
    cmap: Any = plt.colormaps["viridis"]


class Curve:
    """
    Compute and manage the data required to draw a single line for one animation frame.

    A `Curve` represents one domain, one equation, one resulting y-series, and one
    matplotlib `Line2D` object. Equation parameters are inferred from the callable
    signature and exposed as mutable instance attributes.

    The line equation must accept the domain as its first argument and return a
    one-dimensional numeric result matching the domain length.
    """

    _equation_parameter_names: set[str]
    _domain: Domain
    _line_equation: LineEquation
    _vectorized: bool | None

    line: Line2D
    number_of_grid_points: int
    step: Number
    _label: str | None

    def __init__(
        self,
        line_equation: LineEquation,
        number_of_grid_points: int | None = None,
        step: Number | None = None,
        validate_equation: bool = True,
        label: str | None = None,
    ) -> None:
        self._validate_arguments(
            line_equation=line_equation,
            number_of_grid_points=number_of_grid_points,
            step=step,
            validate_equation=validate_equation,
            label=label,
        )

        self._line_equation = line_equation
        self._vectorized = None

        self._record_equation_parameter_names(line_equation)
        if validate_equation:
            self._validate_equation_with_dummy_domain()
        self._init_domain(number_of_grid_points=number_of_grid_points, step=step)

        self.line = Line2D(self._domain, [])
        self.label = label

    @property
    def label(self):
        "The curve's label primarily meant to identify it in legend tracker callback functions."
        return self._label

    @label.setter
    def label(self, label: str | None):
        if label is None:
            self._label = None
            return

        self._validate_arguments(label=label)
        self._label = label

    @label.deleter
    def label(self):
        self._label = None

    def _validate_arguments(
        self,
        **kwargs: Any,
    ) -> None:
        line_equation = kwargs.pop("line_equation", _MISSING)
        number_of_grid_points = kwargs.pop("number_of_grid_points", None)
        step = kwargs.pop("step", None)
        validate_equation = kwargs.pop("validate_equation", None)
        label = kwargs.pop("label", None)

        errors: dict[str, str] = dict()

        if line_equation is not _MISSING and not callable(line_equation):
            errors["line_equation"] = "must be callable"

        if number_of_grid_points is not None:
            if not isinstance(number_of_grid_points, int):
                errors["number_of_grid_points"] = "must be an int or None"
            elif number_of_grid_points <= 0:
                errors["number_of_grid_points"] = "must be positive"

        if step is not None:
            if not isinstance(step, (int, float, np.number)):
                errors["step"] = "must be numeric or None"
            elif step <= 0:
                errors["step"] = "must be positive"

        if validate_equation is not None and not isinstance(validate_equation, bool):
            errors["validate_equation"] = "must be a bool"

        if label is not None:
            if not isinstance(label, str):
                errors["label"] = "must be str or None"
            elif not label.isidentifier():
                errors["label"] = "must be a valid Python identifier"
            elif keyword.iskeyword(label):
                errors["label"] = "must not be a Python keyword"

        if kwargs:
            errors.update({name: "is not a valid argument" for name in kwargs})

        _raise_validation_errors(errors)

    def _validate_equation_with_dummy_domain(self) -> None:
        """
        Validate that the line equation is compatible with a domain input.

        Uses a small dummy domain to verify:
        - Output is 1D
        - Output length matches input
        - Output is numeric
        - Supports either vectorized or scalar execution
        """
        dummy_domain = np.array([-1.0, 0.0, 1.0])
        equation_parameters = self._collect_equation_parameters()

        # Try vectorized evaluation first
        try:
            result = self._line_equation(dummy_domain, **equation_parameters)
            self._validate_compute_result(result, expected_length=len(dummy_domain))
            return
        except Exception:
            pass

        # Fallback: scalar evaluation
        try:
            result = [
                self._line_equation(x, **equation_parameters) for x in dummy_domain
            ]
            self._validate_compute_result(result, expected_length=len(dummy_domain))
        except Exception as exc:
            raise ValueError(
                "line_equation is incompatible with the expected domain interface. "
                "It must accept either a 1D array (vectorized) or scalar inputs "
                "and return a 1D numeric result of matching length."
            ) from exc

    def _record_equation_parameter_names(self, eqn: LineEquation) -> None:
        spec = parse_signature(eqn)
        parameters = list(inspect.signature(eqn).parameters.values())

        if not spec.positional_only and not spec.positional:
            raise ValueError(
                "line_equation must accept at least one argument: the domain"
            )

        if spec.var_positional is not None or spec.var_keyword is not None:
            raise TypeError(
                "line_equation must use explicit named parameters; "
                "*args and **kwargs are not supported"
            )

        # First positional argument is the domain → skip it
        self._equation_parameter_names = set()

        # Remaining explicit parameters become mutable equation parameters.
        for param in parameters[1:]:
            if param.kind not in (
                Parameter.POSITIONAL_ONLY,
                Parameter.POSITIONAL_OR_KEYWORD,
                Parameter.KEYWORD_ONLY,
            ):
                continue

            value = None if param.default is inspect.Parameter.empty else param.default
            setattr(self, param.name, value)
            self._equation_parameter_names.add(param.name)

    def _init_domain(
        self,
        number_of_grid_points: int | None,
        step: Number | None,
    ) -> None:
        self.number_of_grid_points = (
            number_of_grid_points
            if number_of_grid_points is not None
            else Defaults.number_of_grid_points
        )
        self.step = step if step is not None else Defaults.step

        self._validate_arguments(
            number_of_grid_points=self.number_of_grid_points,
            step=self.step,
        )

        self._regenerate_domain()

    def _regenerate_domain(self) -> None:
        self._domain = np.arange(
            start=-self.step * self.number_of_grid_points / 2,
            stop=self.step * self.number_of_grid_points / 2,
            step=self.step,
        )

        if self._domain.ndim != 1:
            raise ValueError("Generated domain must be one-dimensional")

        if len(self._domain) != self.number_of_grid_points:
            raise ValueError(
                "Generated domain length does not match number_of_grid_points "
                f"({len(self._domain)=}, {self.number_of_grid_points=})"
            )

    def _collect_equation_parameters(self) -> EquationParameters:
        return {name: getattr(self, name) for name in self._equation_parameter_names}

    def _compute(self) -> YValues:
        equation_parameters = self._collect_equation_parameters()

        if self._vectorized is None:
            self._vectorized = self._supports_vectorized_evaluation(equation_parameters)

        if self._vectorized:
            result = self._line_equation(self._domain, **equation_parameters)
        else:
            result = [
                self._line_equation(x, **equation_parameters) for x in self._domain
            ]

        return self._validate_compute_result(result)

    def _supports_vectorized_evaluation(
        self,
        equation_parameters: EquationParameters,
    ) -> bool:
        try:
            test_result = self._line_equation(
                self._domain[:1],
                **equation_parameters,
            )
            self._validate_compute_result(test_result, expected_length=1)
        except Exception:
            return False

        return True

    def _validate_compute_result(
        self,
        result: ArrayLike1D,
        expected_length: int | None = None,
    ) -> YValues:
        expected_length = (
            expected_length if expected_length is not None else len(self._domain)
        )

        result_array = np.asarray(result)

        if result_array.ndim != 1:
            raise ValueError("line_equation must return a one-dimensional result")

        if len(result_array) != expected_length:
            raise ValueError(
                "line_equation output length does not match the domain length "
                f"({len(result_array)=}, {expected_length=})"
            )

        if not np.issubdtype(result_array.dtype, np.number):
            raise TypeError("line_equation output must be numeric")

        return result_array

    def update_line(self, **equation_parameters: Number) -> None:
        unknown_parameters = set(equation_parameters) - self._equation_parameter_names

        if unknown_parameters:
            raise ValueError(f"Unknown equation parameters: {unknown_parameters}")

        for name, value in equation_parameters.items():
            setattr(self, name, value)

        result = self._compute()
        self.line.set_ydata(result)


class LegendTracker:
    """
    Build dynamic legend labels for animation frames.

    A legend tracker stores a static label name and a callback. The callback is
    called with the current `Curve` and its result is appended to the label when the
    legend is updated.

    Attributes:
        dummy_line:
            Invisible matplotlib line used as a legend handle.
        label:
            Display label prefix with leading underscores removed.
        callback:
            Callable that extracts or formats the tracked value from a grid.
    """

    label: str
    callback: Callable[[Curve], str]
    dummy_line: Line2D

    def __init__(self, label: str, callback: Callable[[Curve], str]):
        """
        Initialize a legend tracker.

        Args:
            label:
                Text prefix displayed before the callback value. Leading
                underscores are removed before display.
            callback:
                Function called with the active `Curve` to produce the value portion
                of the legend label. Keyword argument names are matched with curve
                labels to give the user controlled access to all curves in a graph.
        """

        self._validate_arguments(label=label, callback=callback)

        self.dummy_line = Line2D([], [], linestyle="none")
        self.label = label.lstrip("_")
        self.callback = self._callback_wrapper(callback)

    @staticmethod
    def _validate_arguments(**kwargs: Any) -> None:
        label = kwargs.pop("label", None)
        callback = kwargs.pop("callback", None)
        curves = kwargs.pop("curves", None)
        legend_trackers = kwargs.pop("legend_trackers", None)

        errors: dict[str, str] = dict()

        if label is not None and not isinstance(label, str):
            errors["label"] = "must be a str"

        if callback is not None and not callable(callback):
            errors["callback"] = "must be callable"

        if curves is not None:
            if not isinstance(curves, list):
                errors["curves"] = "must be a list of Curve objects"
            elif not all(isinstance(curve, Curve) for curve in curves):
                errors["curves"] = "must contain only Curve objects"

        if legend_trackers is not None:
            if not isinstance(legend_trackers, list):
                errors["legend_trackers"] = (
                    "must be a list of LegendTracker objects"
                )
            elif not all(
                isinstance(legend_tracker, LegendTracker)
                for legend_tracker in legend_trackers
            ):
                errors["legend_trackers"] = (
                    "must contain only LegendTracker objects"
                )

        if kwargs:
            errors.update({name: "is not a valid argument" for name in kwargs})

        _raise_validation_errors(errors)

    @staticmethod
    def _callback_wrapper(callback: Callable[[Curve], str]) -> Callable[[Curve], str]:
        callback_spec: FunctionSpec = parse_signature(callback)

        def wrapper(*curves: Curve, **named_curves: Curve | list[Curve]) -> Any:
            label_to_curve: dict[str, Curve] = {}

            for curve in curves:
                if curve.label is not None:
                    label_to_curve[curve.label] = curve

            for label, curve_or_curves in named_curves.items():
                if label == "nolabel":
                    continue
                if isinstance(curve_or_curves, Curve):
                    label_to_curve[label] = curve_or_curves

            label_to_curve_original = label_to_curve.copy()

            positional_only: list[Curve] = []
            positional_or_keyword: dict[str, Curve] = dict()
            keyword_only: dict[str, Curve] = dict()
            kwargs: dict[str, Curve] = dict()

            skipped: list[str] = []

            for label in callback_spec.positional_only:
                curve = label_to_curve.get(label, None)
                if curve is None:
                    skipped.append(label)
                    continue
                positional_only.append(label_to_curve.pop(label))

            for label in callback_spec.positional:
                curve = label_to_curve.get(label, None)
                if curve is None:
                    skipped.append(label)
                    continue
                positional_or_keyword[label] = label_to_curve.pop(label)

            for label in callback_spec.keyword_only:
                curve = label_to_curve.get(label, None)
                if curve is None:
                    skipped.append(label)
                    continue
                keyword_only[label] = label_to_curve.pop(label)

            missing = [
                name
                for name in callback_spec.positional_only + callback_spec.positional
                if name not in label_to_curve_original
            ]
            if missing:
                raise ValueError(
                    "Legend callback requires missing curve labels: "
                    + ", ".join(missing)
                )

            if skipped and callback_spec.var_keyword is None:
                print(
                    "Warning, skipped the following keyword arguments: "
                    + ", ".join(skipped)
                )

            if callback_spec.var_keyword is not None:
                kwargs = label_to_curve.copy()

            return callback(
                *positional_only, **positional_or_keyword, **keyword_only, **kwargs
            )

        return wrapper

    def make_tracking_label(
        self,
        curves: list[Curve],
    ) -> str:
        """
        Return the legend text for the supplied curve.

        Args:
            curves

        Returns:
            Formatted legend entry in the form `"<label>=<value>"`.
        """

        self._validate_arguments(curves=curves)

        kwargs: dict[str, Curve | list[Curve]] = {"nolabel": []}
        for curve in curves:
            if curve.label is not None:
                kwargs[curve.label] = curve
                continue
            kwargs["nolabel"].append(curve)

        return f"{self.label}={self.callback(**kwargs)}"

    @staticmethod
    def make_tracking_labels(
        curves: list[Curve], legend_trackers: list[LegendTracker]
    ) -> list[str]:
        LegendTracker._validate_arguments(
            curves=curves,
            legend_trackers=legend_trackers,
        )

        tracking_labels: list[str] = []
        for legend_tracker in legend_trackers:
            tracking_labels.append(legend_tracker.make_tracking_label(curves))

        return tracking_labels

    @staticmethod
    def dummy_lines(legend_trackers: list[LegendTracker]) -> list[Line2D]:
        LegendTracker._validate_arguments(legend_trackers=legend_trackers)

        return [legend_tracker.dummy_line for legend_tracker in legend_trackers]


class Graph:
    curves: list[Curve]
    domain: ArrayLike1D
    legend_trackers: list[LegendTracker] | None
    axes: Axes | None
    legend: Legend | None

    _row: int
    _col: int
    _generate_colours: bool
    _auto_scale_axes: bool

    def __init__(
        self,
        curves: list[Curve] | Curve | None = None,
        legend_trackers: list[LegendTracker] | LegendTracker | None = None,
        row: int | None = None,
        col: int | None = None,
        auto_scale_axes: bool = False,
        generate_colours: bool = False,
    ) -> None:

        self._validate_arguments(
            curves=curves,
            legend_trackers=legend_trackers,
            row=row,
            col=col,
            auto_scale_axes=auto_scale_axes,
            generate_colours=generate_colours,
        )

        if curves is None:
            self.curves = []
        elif isinstance(curves, list):
            self.curves = curves
        else:
            self.curves = [curves]
        if legend_trackers is None:
            self.legend_trackers = []
        elif isinstance(legend_trackers, list):
            self.legend_trackers = legend_trackers
        else:
            self.legend_trackers = [legend_trackers]
        self._auto_scale_axes = auto_scale_axes
        self._generate_colours = generate_colours
        self._row = row
        self._col = col
        self.axes = None
        self.legend = None

    def _validate_arguments(self, **kwargs):

        curves = kwargs.pop("curves", None)
        legend_trackers = kwargs.pop("legend_trackers", None)
        row = kwargs.pop("row", None)
        col = kwargs.pop("col", None)
        auto_scale_axes = kwargs.pop("auto_scale_axes", None)
        generate_colours = kwargs.pop("generate_colours", None)
        axes = kwargs.pop("axes", None)

        errors: dict[str, str] = dict()

        if curves is not None:
            curve_list = curves if isinstance(curves, list) else [curves]
            if not all(isinstance(curve, Curve) for curve in curve_list):
                errors["curves"] = "must be a Curve or list of Curve objects"
            else:
                curve_labels = [
                    curve.label for curve in curve_list if curve.label is not None
                ]
                if len(set(curve_labels)) != len(curve_labels):
                    errors["curves"] = "must not contain duplicate curve labels"

        if row is not None and not isinstance(row, int):
            errors["row"] = "must be an int or None"
        if col is not None and not isinstance(col, int):
            errors["col"] = "must be an int or None"

        if legend_trackers is not None:
            legend_tracker_list = (
                legend_trackers
                if isinstance(legend_trackers, list)
                else [legend_trackers]
            )
            if not all(
                isinstance(legend_tracker, LegendTracker)
                for legend_tracker in legend_tracker_list
            ):
                errors["legend_trackers"] = (
                    "must be a LegendTracker or list of LegendTracker objects"
                )
        if auto_scale_axes is not None and not isinstance(auto_scale_axes, bool):
            errors["auto_scale_axes"] = "must be a bool"

        if generate_colours is not None and not isinstance(generate_colours, bool):
            errors["generate_colours"] = "must be a bool"

        if axes is not None and not isinstance(axes, Axes):
            errors["axes"] = "must be a matplotlib Axes object"

        if kwargs:
            errors.update({name: "is not a valid argument" for name in kwargs})

        _raise_validation_errors(errors)

    def _init_colours(self) -> None:
        cmap = Defaults.cmap
        norm = mcolors.Normalize(vmin=0, vmax=len(self.curves) - 1)
        for i, curve in enumerate(self.curves):
            curve.line.set_color(cmap(norm(i)))

    def update_legend(self) -> None:
        if self.legend is None or not self.legend_trackers:
            return

        labels = LegendTracker.make_tracking_labels(self.curves, self.legend_trackers)

        for text, label in zip(self.legend.get_texts(), labels):
            text.set_text(label)

    def update_lines(self) -> None:
        for curve in self.curves:
            curve.update_line()

    def init_graph(
        self,
        axes: Axes,
        row: int | None = None,
        col: int | None = None,
    ) -> None:
        """
        This function takes care of setting up the legend trackers on the axes.
        """

        self._validate_arguments(row=row, col=col, axes=axes)

        # If the row or column were not set they are automatically defined by the
        # `GraphMatrix` class when animating.
        self._row = row if self._row is None else self._row
        self._col = col if self._col is None else self._col
        self.axes = axes

        if self.legend_trackers:
            self.legend = self.axes.legend(
                LegendTracker.dummy_lines(self.legend_trackers),
                LegendTracker.make_tracking_labels(self.curves, self.legend_trackers),
            )
            self.legend.set_in_layout(False)

        if self._generate_colours:
            self._init_colours()

        for curve in self.curves:
            if len(curve.line.get_ydata()) != len(curve.line.get_xdata()):
                curve.line.set_ydata(np.ma.array(curve.line.get_xdata(), mask=True))
            self.axes.add_line(curve.line)

        self.axes.relim()
        self.axes.autoscale_view()


class GraphMatrix:
    ncols: int
    nrows: int
    figure: Figure
    graphs: list[Graph]

    def __init__(
        self,
        graphs: list[Graph],
        ncols: int | None = None,
        column_size_multiplier: float = 1.0,
        row_size_multiplier: float = 1.0,
    ):
        self._validate_arguments(
            graphs=graphs,
            ncols=ncols,
            column_size_multiplier=column_size_multiplier,
            row_size_multiplier=row_size_multiplier,
        )

        self.graphs = graphs

        self.ncols: int | None = None
        if len(graphs) == 1:
            self.ncols = ncols or 1
        else:
            self.ncols = ncols or 2
        self.nrows = int(np.ceil(len(graphs) / self.ncols))

        self.column_size_multiplier: float = column_size_multiplier
        self.row_size_multiplier: float = row_size_multiplier

        self.init_fig()

    @staticmethod
    def _validate_arguments(**kwargs: Any) -> None:
        graphs = kwargs.pop("graphs", None)
        ncols = kwargs.pop("ncols", None)
        column_size_multiplier = kwargs.pop("column_size_multiplier", None)
        row_size_multiplier = kwargs.pop("row_size_multiplier", None)
        row = kwargs.pop("row", None)
        col = kwargs.pop("col", None)
        idx = kwargs.pop("idx", None)

        errors: dict[str, str] = dict()

        if graphs is not None:
            if not isinstance(graphs, list):
                errors["graphs"] = "must be a list of Graph objects"
            elif not all(isinstance(graph, Graph) for graph in graphs):
                errors["graphs"] = "must contain only Graph objects"
            elif len(graphs) == 0:
                errors["graphs"] = "must contain at least one Graph"

        if ncols is not None:
            if not isinstance(ncols, int):
                errors["ncols"] = "must be an int or None"
            elif ncols <= 0:
                errors["ncols"] = "must be positive"

        if column_size_multiplier is not None:
            if not isinstance(column_size_multiplier, (int, float, np.number)):
                errors["column_size_multiplier"] = "must be numeric"
            elif column_size_multiplier <= 0:
                errors["column_size_multiplier"] = "must be positive"

        if row_size_multiplier is not None:
            if not isinstance(row_size_multiplier, (int, float, np.number)):
                errors["row_size_multiplier"] = "must be numeric"
            elif row_size_multiplier <= 0:
                errors["row_size_multiplier"] = "must be positive"

        if row is not None and not isinstance(row, int):
            errors["row"] = "must be an int"

        if col is not None and not isinstance(col, int):
            errors["col"] = "must be an int"

        if idx is not None and not isinstance(idx, int):
            errors["idx"] = "must be an int"

        if kwargs:
            errors.update({name: "is not a valid argument" for name in kwargs})

        _raise_validation_errors(errors)

    def init_fig(self):
        self.figure, axes = plt.subplots(
            ncols=self.ncols,
            nrows=self.nrows,
            figsize=(
                6 * self.ncols * self.column_size_multiplier,
                4 * self.nrows * self.row_size_multiplier,
            ),
        )

        if isinstance(axes, Axes):
            axes = np.asarray([axes])
        else:
            axes = np.asarray(axes).ravel()

        unique_coords = set()
        for i, graph in enumerate(self.graphs):
            row, col = self.idx_to_coord(i)
            graph.init_graph(axes[i], row=row, col=col)
            unique_coords.add((row, col))

        if len(unique_coords) != len(self.graphs):
            raise ValueError(
                "Some graphs have overlapping coordinates. "
                f"{len(unique_coords)} != {len(self.graphs)}"
            )

    def coord_to_idx(self, row: int, col: int) -> int:
        self._validate_arguments(row=row, col=col)
        return col + row * self.ncols

    def idx_to_coord(self, idx: int) -> tuple[int, int]:
        self._validate_arguments(idx=idx)
        return idx // self.ncols, idx % self.ncols

    def update_graphs(self) -> None:
        for graph in self.graphs:
            graph.update_lines()
            graph.update_legend()

    @overload
    def get_graph(self, idx: int) -> Graph: ...
    @overload
    def get_graph(self, row: int, col: int) -> Graph: ...
    def get_graph(self, **kwargs: int) -> Graph:

        idx = kwargs.pop("idx", None)
        row = kwargs.pop("row", None)
        col = kwargs.pop("col", None)

        if kwargs:
            self._validate_arguments(**kwargs)

        if idx is not None:
            self._validate_arguments(idx=idx)
        elif row is not None and col is not None:
            self._validate_arguments(row=row, col=col)
            idx = self.coord_to_idx(row, col)
        else:
            raise ValueError(
                "`get_graph` takes either `idx` or `row` and `col` as keyword arguments. If `idx` is provided then all other arguments and keyword arguments are ignored."
            )

        if not 0 <= idx < len(self.graphs):
            raise ValueError(
                f"Graph index out of range: expected 0 <= idx < {len(self.graphs)}, "
                f"got {idx}"
            )
        return self.graphs[idx]
