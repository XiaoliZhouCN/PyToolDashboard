from __future__ import annotations


def box_center(box: dict[str, float]) -> tuple[float, float]:
    """Return the visual center of a node or subgraph box."""

    return box["x"] + box["width"] / 2, box["y"] + box["height"] / 2


def resolve_box_side_anchor(
    box: dict[str, float],
    side: str,
) -> tuple[float, float] | None:
    """Resolve an explicit anchor side into a concrete point on the box."""

    center_x, center_y = box_center(box)
    if side == "top":
        return center_x, box["y"]
    if side == "right":
        return box["x"] + box["width"], center_y
    if side == "bottom":
        return center_x, box["y"] + box["height"]
    if side == "left":
        return box["x"], center_y
    return None


def resolve_anchor_point(
    box: dict[str, float],
    toward: tuple[float, float],
    *,
    side_override: str | None = None,
) -> tuple[float, float]:
    """Resolve the best anchor point for an edge endpoint on a box."""

    explicit_side = side_override or str(box.get("anchor_side", "auto"))
    explicit = resolve_box_side_anchor(box, explicit_side)
    if explicit is not None:
        return explicit

    center_x, center_y = box_center(box)
    dx = toward[0] - center_x
    dy = toward[1] - center_y
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        return center_x, center_y

    half_width = box["width"] / 2
    half_height = box["height"] / 2
    scale = 1.0 / max(abs(dx) / half_width, abs(dy) / half_height)
    return center_x + dx * scale, center_y + dy * scale


def build_edge_curve(
    source: tuple[float, float],
    target: tuple[float, float],
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Build cubic bezier control points for a readable edge path."""

    delta_x = target[0] - source[0]
    delta_y = target[1] - source[1]
    abs_x = abs(delta_x)
    abs_y = abs(delta_y)

    if abs_y >= abs_x:
        handle = min(96.0, max(24.0, abs_y * 0.32))
        direction = 1.0 if delta_y >= 0 else -1.0
        return (
            (source[0], source[1] + handle * direction),
            (target[0], target[1] - handle * direction),
        )

    handle = min(96.0, max(24.0, abs_x * 0.35))
    direction = 1.0 if delta_x >= 0 else -1.0
    return (
        (source[0] + handle * direction, source[1]),
        (target[0] - handle * direction, target[1]),
    )
