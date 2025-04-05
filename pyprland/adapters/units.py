"""Conversion functions for units used in Pyprland & plugins."""

from ..common import is_rotated
from ..types import MonitorInfo

def convert_negative_dimension(size: int, ref_value: float) -> int:
    """Returns the original dimension if non-negative, otherwise returns the
    reference value minus the original dimension. Used so the user can specify
    a negative dimension and have it subtracted from the reference dimension.

    Example: allow user to make a scratchpad 50px less wide than the monitor by
    setting its width to "-50px".
    """
    if size < 0:
        return int(ref_value + size)
    else:
        return size

def convert_monitor_dimension(size: int | str, ref_value: int, monitor: MonitorInfo) -> int:
    """Convert `size` into pixels (given a reference value applied to a `monitor`).

    if size is an integer, assumed pixels & return it
    if size is a string, expects a "%" or "px" suffix
    else throws an error
    """

    scaled_ref_value = ref_value / monitor["scale"]

    if isinstance(size, int):
        return convert_negative_dimension(size, scaled_ref_value)

    if isinstance(size, str):
        if size.endswith("%"):
            p = int(size[:-1])
            return int(scaled_ref_value * p / 100)
        if size.endswith("px"):
            return convert_negative_dimension(int(size[:-2]), scaled_ref_value)

    msg = f"Unsupported format: {size} (applied to {ref_value})"
    raise ValueError(msg)


def convert_coords(coords: str, monitor: MonitorInfo) -> list[int]:
    """Convert a string like "X Y" to coordinates relative to monitor.

    Supported formats for X, Y:
    - Percentage: "V%". V in [0; 100]
    - Pixels: "Vpx". V should fit in your screen and not be zero

    Example:
    "10% 20%", monitor 800x600 => 80, 120
    """
    return [
        convert_monitor_dimension(name, monitor[ref], monitor)  # type: ignore
        for (name, ref) in zip(
            [coord.strip() for coord in coords.split()],
            (("height", "width") if is_rotated(monitor) else ("width", "height")),
            strict=False,
        )
    ]
