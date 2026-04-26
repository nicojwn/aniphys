# aniphys/animate.py


from __future__ import annotations

from collections.abc import Callable
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
from tqdm import tqdm

from aniphys.frame_objects import (
    Curve,
    Graph,
    GraphMatrix,
    LegendTracker,
    _normalize_domain,
)
from aniphys.type_defs import ArrayLike1D, Domain


def animator(
    *equations: Callable[..., Any] | list[Callable[..., Any]],
    domain: ArrayLike1D | None = None,
    legend_trackers: list[LegendTracker] | None = None,
    **equation_parameters: Any,
) -> list[GraphMatrix]:
    """
    Build a sequence of `GraphMatrix` frames from equations and frame parameters.

    Each positional callable becomes one graph with one curve. Each positional
    list of callables becomes one graph with multiple curves. `domain`, when
    provided, is used as the shared x-domain for every generated curve. Keyword
    arguments are applied to every curve whose equation exposes a matching
    parameter name.
    """

    graph_specs = _normalize_equation_specs(equations)
    normalized_domain = _normalize_animator_domain(domain)
    _validate_legend_trackers(legend_trackers)
    parameter_frames = _normalize_parameter_frames(
        graph_specs,
        equation_parameters,
    )

    graph_matrices: list[GraphMatrix] = []
    for frame_parameters in parameter_frames:
        graphs: list[Graph] = []

        for graph_idx, equations_for_graph in enumerate(graph_specs):
            curves: list[Curve] = []

            for curve_idx, equation in enumerate(equations_for_graph):
                curve = Curve(
                    equation,
                    domain=normalized_domain,
                    validate_equation=False,
                    label=f"curve_{graph_idx}_{curve_idx}",
                )
                curve_parameters = {
                    name: value
                    for name, value in frame_parameters.items()
                    if name in curve._equation_parameter_names
                }
                curve.update_line(**curve_parameters)
                curves.append(curve)

            graphs.append(
                Graph(
                    curves,
                    legend_trackers=legend_trackers or [],
                    auto_scale_axes=True,
                    generate_colours=True,
                )
            )

        graph_matrices.append(GraphMatrix(graphs))

    return graph_matrices


def _normalize_animator_domain(domain: ArrayLike1D | None) -> Domain | None:
    if domain is None:
        return None

    try:
        return _normalize_domain(domain)
    except ValueError as exc:
        raise ValueError(
            "Please check the following arguments: domain -> " + str(exc)
        ) from exc


def _generate_animation(
    graph_matrices: list[GraphMatrix],
    fps: int = 60,
    suppress_progress_bar: bool = False,
) -> FuncAnimation:
    """
    Generate an animation from a sequence of `GraphMatrix` frame objects.

    The first matrix owns the displayed figure and artists. Later matrices are
    treated as frame data whose line values are copied into the display matrix.
    """

    _validate_graph_matrices(graph_matrices)

    display_matrix = graph_matrices[0]
    frames = graph_matrices[1:] or graph_matrices

    changed_artists = _collect_changed_artists(display_matrix)

    if suppress_progress_bar:
        for matrix in graph_matrices:
            matrix.update_graphs()
    else:
        with tqdm(
            total=len(graph_matrices),
            desc="Computing frames",
            ncols=80,
            mininterval=0.1,
            unit="frames",
        ) as progress_bar:
            for matrix in graph_matrices:
                matrix.update_graphs()
                progress_bar.update()

    _apply_global_axis_limits(display_matrix, graph_matrices)

    def init_animation() -> tuple[Artist, ...]:
        """
        Initialize the animation state required for blitting.

        The line y-data is masked so matplotlib has artists to work with before
        the first real frame is drawn.
        """

        for graph in display_matrix.graphs:
            for curve in graph.curves:
                curve.line.set_ydata(np.ma.array(curve.line.get_ydata(), mask=True))

        return changed_artists

    def animate(frame: GraphMatrix) -> tuple[Artist, ...]:
        """
        Render a single animation frame.
        """

        _copy_frame_data(display_matrix, frame)
        _copy_legend_labels(display_matrix, frame)

        return changed_artists

    for frame in graph_matrices[1:]:
        plt.close(frame.figure)

    return FuncAnimation(
        fig=display_matrix.figure,
        func=animate,
        frames=frames,
        init_func=init_animation,
        interval=1000 / fps,
        blit=True,
    )


def generate_animation(
    graph_matrices: list[GraphMatrix],
    fps: int = 60,
    suppress_progress_bar: bool = False,
    show: bool = True,
) -> FuncAnimation:
    if not isinstance(show, bool):
        raise ValueError("show must be a boolean")

    ani = _generate_animation(
        graph_matrices=graph_matrices,
        fps=fps,
        suppress_progress_bar=suppress_progress_bar,
    )

    if show:
        plt.show()

    return ani


def _normalize_equation_specs(
    equations: tuple[Callable[..., Any] | list[Callable[..., Any]], ...],
) -> list[list[Callable[..., Any]]]:
    if not equations:
        raise ValueError("animator requires at least one callable or list of callables")

    graph_specs: list[list[Callable[..., Any]]] = []
    errors: dict[str, str] = {}

    for idx, equation_or_equations in enumerate(equations):
        if callable(equation_or_equations):
            graph_specs.append([equation_or_equations])
            continue

        if isinstance(equation_or_equations, list):
            if not equation_or_equations:
                errors[f"equations[{idx}]"] = "must not be an empty list"
            elif not all(callable(equation) for equation in equation_or_equations):
                errors[f"equations[{idx}]"] = "must contain only callables"
            else:
                graph_specs.append(equation_or_equations)
            continue

        errors[f"equations[{idx}]"] = "must be callable or a list of callables"

    if errors:
        raise ValueError(
            "Please check the following arguments: "
            + "; ".join(f"{argument} -> {error}" for argument, error in errors.items())
        )

    return graph_specs


def _validate_legend_trackers(
    legend_trackers: list[LegendTracker] | None,
) -> None:
    if legend_trackers is None:
        return

    if not isinstance(legend_trackers, list):
        raise ValueError(
            "Please check the following arguments: "
            "legend_trackers -> must be a list of LegendTracker objects or None"
        )

    if not all(isinstance(tracker, LegendTracker) for tracker in legend_trackers):
        raise ValueError(
            "Please check the following arguments: "
            "legend_trackers -> must contain only LegendTracker objects"
        )


def _normalize_parameter_frames(
    graph_specs: list[list[Callable[..., Any]]],
    equation_parameters: dict[str, Any],
) -> list[dict[str, Any]]:
    accepted_parameter_names = _collect_accepted_parameter_names(graph_specs)

    unknown_parameters = set(equation_parameters) - accepted_parameter_names
    if unknown_parameters:
        raise ValueError(
            "Unknown equation parameters: " + ", ".join(sorted(unknown_parameters))
        )

    frame_parameters: dict[str, list[Any] | Any] = {}
    frame_lengths: dict[str, int] = {}

    for name, value in equation_parameters.items():
        if _is_frame_sequence(value):
            values = list(value)
            if not values:
                raise ValueError(f"Equation parameter {name!r} must not be empty")
            frame_parameters[name] = values
            frame_lengths[name] = len(values)
        else:
            frame_parameters[name] = value

    unique_lengths = set(frame_lengths.values())
    if len(unique_lengths) > 1:
        raise ValueError(
            "Frame-varying equation parameters must have the same length: "
            + ", ".join(
                f"{name}={length}" for name, length in sorted(frame_lengths.items())
            )
        )

    number_of_frames = unique_lengths.pop() if unique_lengths else 1
    frames: list[dict[str, Any]] = []

    for frame_idx in range(number_of_frames):
        parameters_for_frame: dict[str, Any] = {}
        for name, value in frame_parameters.items():
            if name in frame_lengths:
                parameters_for_frame[name] = value[frame_idx]
            else:
                parameters_for_frame[name] = value
        frames.append(parameters_for_frame)

    return frames


def _collect_accepted_parameter_names(
    graph_specs: list[list[Callable[..., Any]]],
) -> set[str]:
    accepted_parameter_names: set[str] = set()

    for equations_for_graph in graph_specs:
        for equation in equations_for_graph:
            curve = Curve(equation, validate_equation=False)
            accepted_parameter_names.update(curve._equation_parameter_names)

    return accepted_parameter_names


def _is_frame_sequence(value: Any) -> bool:
    if isinstance(value, (str, bytes)):
        return False

    if isinstance(value, np.ndarray):
        return value.ndim > 0

    if isinstance(value, np.number):
        return False

    if isinstance(value, (int, float, complex, bool)):
        return False

    try:
        iter(value)
    except TypeError:
        return False

    return True


def _validate_graph_matrices(graph_matrices: list[GraphMatrix]) -> None:
    if not isinstance(graph_matrices, list):
        raise TypeError("graph_matrices must be a list of GraphMatrix objects")
    if not graph_matrices:
        raise ValueError("graph_matrices must contain at least one frame")
    if not all(isinstance(matrix, GraphMatrix) for matrix in graph_matrices):
        raise TypeError("graph_matrices must contain only GraphMatrix objects")

    graph_count = len(graph_matrices[0].graphs)
    curve_counts = [len(graph.curves) for graph in graph_matrices[0].graphs]

    for matrix in graph_matrices[1:]:
        if len(matrix.graphs) != graph_count:
            raise ValueError("all GraphMatrix frames must have the same graph count")

        for graph_idx, graph in enumerate(matrix.graphs):
            if len(graph.curves) != curve_counts[graph_idx]:
                raise ValueError("corresponding graphs must have the same curve count")


def _apply_global_axis_limits(
    display_matrix: GraphMatrix,
    graph_matrices: list[GraphMatrix],
) -> None:
    for graph_idx, display_graph in enumerate(display_matrix.graphs):
        if not display_graph._auto_scale_axes or display_graph.axes is None:
            continue

        x_values: list[float] = []
        y_values: list[float] = []

        for matrix in graph_matrices:
            for curve in matrix.graphs[graph_idx].curves:
                x_data = np.asarray(curve.line.get_xdata(), dtype=float)
                y_data = np.asarray(curve.line.get_ydata(), dtype=float)

                finite_x = x_data[np.isfinite(x_data)]
                finite_y = y_data[np.isfinite(y_data)]

                if len(finite_x) > 0:
                    x_values.extend([float(np.min(finite_x)), float(np.max(finite_x))])
                if len(finite_y) > 0:
                    y_values.extend([float(np.min(finite_y)), float(np.max(finite_y))])

        if not x_values or not y_values:
            continue

        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        x_padding = _axis_padding(x_min, x_max)
        y_padding = _axis_padding(y_min, y_max)

        display_graph.axes.set_xlim(x_min - x_padding, x_max + x_padding)
        display_graph.axes.set_ylim(y_min - y_padding, y_max + y_padding)


def _axis_padding(minimum: float, maximum: float) -> float:
    return 0.05 * (maximum - minimum) if maximum != minimum else 1.0


def _collect_changed_artists(graph_matrix: GraphMatrix) -> tuple[Artist, ...]:
    artists: list[Artist] = []

    for graph in graph_matrix.graphs:
        artists.extend(curve.line for curve in graph.curves)
        if graph.legend is not None:
            artists.extend(graph.legend.get_texts())

    return tuple(artists)


def _copy_frame_data(display_matrix: GraphMatrix, frame: GraphMatrix) -> None:
    for display_graph, frame_graph in zip(display_matrix.graphs, frame.graphs):
        for display_curve, frame_curve in zip(display_graph.curves, frame_graph.curves):
            display_curve.line.set_xdata(frame_curve.line.get_xdata())
            display_curve.line.set_ydata(frame_curve.line.get_ydata())


def _copy_legend_labels(display_matrix: GraphMatrix, frame: GraphMatrix) -> None:
    for display_graph, frame_graph in zip(display_matrix.graphs, frame.graphs):
        if display_graph.legend is None:
            continue

        labels = [
            tracker.make_tracking_label(frame_graph.curves)
            for tracker in display_graph.legend_trackers
        ]

        for text, label in zip(display_graph.legend.get_texts(), labels):
            text.set_text(label)
