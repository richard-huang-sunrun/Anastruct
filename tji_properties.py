"""
Trus Joist TJI section properties by series and nominal depth (in).

Used when DETDB indicates membertype TJI and supplies tji_model / tji_depth.
Values substitute E, I, A, S, Fb, Fv (and E·I for reference) in current_calculation.
"""

from __future__ import annotations

from typing import Any, Mapping

# Nominal depths (in) matching manufacturer tables
TJI_DEPTHS: tuple[float, ...] = (9.5, 11.875, 14.0, 16.0)

# Keys per depth index 0..3
# NA / missing Excel cells are omitted from inner dicts — lookup returns None.
TJI_TABLE: dict[int, dict[float, dict[str, float]]] = {
    110: {
        9.5: {
            "EI": 157_000_000.0,
            "I": 109.999349,
            "E": 1427281.175,
            "A": 3.4375,
            "S": 23.15775768,
            "Fb": 1295.462213,
            "Fv": 354.9090909,
            "Moment_ftlb": 2500.0,
            "Shear_lb": 1220.0,
        },
        11.875: {
            "EI": 267_000_000.0,
            "I": 180.5547078,
            "E": 1478776.174,
            "A": 3.4375,
            "S": 30.39641546,
            "Fb": 1247.515519,
            "Fv": 453.8181818,
            "Moment_ftlb": 3160.0,
            "Shear_lb": 1560.0,
        },
        14.0: {
            "EI": 392_000_000.0,
            "I": 262.4720052,
            "E": 1493492.61,
            "A": 3.4375,
            "S": 37.49600074,
            "Fb": 1196.927649,
            "Fv": 541.0909091,
            "Moment_ftlb": 3740.0,
            "Shear_lb": 1860.0,
        },
        16.0: {
            "EI": 535_000_000.0,
            "I": 357.4563802,
            "E": 1496686.112,
            "A": 3.4375,
            "S": 44.68204753,
            "Fb": 1149.454934,
            "Fv": 1495.272727,
            "Moment_ftlb": 4280.0,
            "Shear_lb": 5140.0,
        },
    },
    210: {
        9.5: {
            "EI": 186_000_000.0,
            "I": 127.7280273,
            "E": 1456219.155,
            "A": 4.21875,
            "S": 26.89011102,
            "Fb": 1338.782126,
            "Fv": 315.2592593,
            "Moment_ftlb": 3000.0,
            "Shear_lb": 1330.0,
        },
        11.875: {
            "EI": 315_000_000.0,
            "I": 208.1985474,
            "E": 1512978.856,
            "A": 4.21875,
            "S": 35.0502605,
            "Fb": 1299.277077,
            "Fv": 394.6666667,
            "Moment_ftlb": 3795.0,
            "Shear_lb": 1665.0,
        },
        14.0: {
            "EI": 462_000_000.0,
            "I": 300.8549805,
            "E": 1535623.573,
            "A": 4.21875,
            "S": 42.97928292,
            "Fb": 1253.627244,
            "Fv": 461.037037,
            "Moment_ftlb": 4490.0,
            "Shear_lb": 1945.0,
        },
        16.0: {
            "EI": 629_000_000.0,
            "I": 407.5581055,
            "E": 1543338.217,
            "A": 4.21875,
            "S": 50.94476318,
            "Fb": 1210.723068,
            "Fv": 519.1111111,
            "Moment_ftlb": 5140.0,
            "Shear_lb": 2190.0,
        },
    },
    230: {
        9.5: {
            "EI": 206_000_000.0,
            "I": 141.9109701,
            "E": 1451614.346,
            "A": 4.84375,
            "S": 29.8759937,
            "Fb": 1337.528733,
            "Fv": 274.5806452,
            "Moment_ftlb": 3330.0,
            "Shear_lb": 1330.0,
        },
        11.875: {
            "EI": 347_000_000.0,
            "I": 230.313619,
            "E": 1506641.255,
            "A": 4.84375,
            "S": 38.77333653,
            "Fb": 1304.504707,
            "Fv": 341.6774194,
            "Moment_ftlb": 4215.0,
            "Shear_lb": 1655.0,
        },
        14.0: {
            "EI": 509_000_000.0,
            "I": 331.5613607,
            "E": 1535160.789,
            "A": 4.84375,
            "S": 47.36590867,
            "Fb": 1264.200386,
            "Fv": 401.5483871,
            "Moment_ftlb": 4990.0,
            "Shear_lb": 1945.0,
        },
        16.0: {
            "EI": 691_000_000.0,
            "I": 447.6394857,
            "E": 1543652.922,
            "A": 4.84375,
            "S": 55.95493571,
            "Fb": 1224.556853,
            "Fv": 452.1290323,
            "Moment_ftlb": 5710.0,
            "Shear_lb": 2190.0,
        },
    },
    360: {
        11.875: {
            "EI": 419_000_000.0,
            "I": 248.9384562,
            "E": 1683146.937,
            "A": 5.328125,
            "S": 41.90883101,
            "Fb": 1769.555442,
            "Fv": 320.0,
            "Moment_ftlb": 6180.0,
            "Shear_lb": 1705.0,
        },
        14.0: {
            "EI": 612_000_000.0,
            "I": 357.1059367,
            "E": 1713777.166,
            "A": 5.328125,
            "S": 51.01513381,
            "Fb": 1725.370364,
            "Fv": 374.4281525,
            "Moment_ftlb": 7335.0,
            "Shear_lb": 1995.0,
        },
        16.0: {
            "EI": 830_000_000.0,
            "I": 480.6957804,
            "E": 1726663.794,
            "A": 5.328125,
            "S": 60.08697255,
            "Fb": 1678.566846,
            "Fv": 411.026393,
            "Moment_ftlb": 8405.0,
            "Shear_lb": 2190.0,
        },
    },
    560: {
        11.875: {
            "EI": 636_000_000.0,
            "I": 368.5362854,
            "E": 1725745.945,
            "A": 8.421875,
            "S": 62.04314569,
            "Fb": 1837.431012,
            "Fv": 243.4137291,
            "Moment_ftlb": 9500.0,
            "Shear_lb": 2050.0,
        },
        14.0: {
            "EI": 926_000_000.0,
            "I": 525.0518392,
            "E": 1763635.38,
            "A": 8.421875,
            "S": 75.0074056,
            "Fb": 1803.821888,
            "Fv": 283.7847866,
            "Moment_ftlb": 11275.0,
            "Shear_lb": 2390.0,
        },
        16.0: {
            "EI": 1_252_000_000.0,
            "I": 702.3259277,
            "E": 1782648.128,
            "A": 8.421875,
            "S": 87.79074097,
            "Fb": 1766.701116,
            "Fv": 321.7810761,
            "Moment_ftlb": 12925.0,
            "Shear_lb": 2710.0,
        },
    },
}


def _normalize_depth(depth: float) -> float | None:
    """Map incoming DETDB depth (in) to table key."""
    for d in TJI_DEPTHS:
        if abs(float(depth) - d) < 0.02:
            return d
    return None


def lookup_tji_properties(
    tji_model: int | str | None,
    tji_depth: float | str | None,
) -> dict[str, Any] | None:
    """
    Return section property dict for (model, depth), or None if not in table.
    """
    if tji_model is None or tji_depth is None:
        return None
    try:
        model = int(str(tji_model).strip())
    except (TypeError, ValueError):
        return None
    try:
        depth_f = float(tji_depth)
    except (TypeError, ValueError):
        return None

    depth_key = _normalize_depth(depth_f)
    if depth_key is None:
        return None

    by_model = TJI_TABLE.get(model)
    if not by_model:
        return None
    return by_model.get(depth_key)


def apply_tji_to_roof_inputs(
    roof_data: Mapping[str, Any],
    *,
    member_type: str,
) -> dict[str, Any]:
    """
    If member is TJI and DETDB fields resolve in the table, return overrides
    for modulus_E, member_I, member_A, bending_stress_Fb, shear_stress_Fv,
    framing_depth, and capacity section overrides I/S.

    Otherwise return {}.
    """
    mt = (member_type or "").strip().upper()
    if mt != "TJI":
        return {}

    props = lookup_tji_properties(
        roof_data.get("tji_model") or roof_data.get("TJI_model"),
        roof_data.get("tji_depth") or roof_data.get("TJI_depth"),
    )
    if not props:
        return {}

    out: dict[str, Any] = {
        "modulus_E": props["E"],
        "member_I": props["I"],
        "member_A": props["A"],
        "bending_stress_Fb": props["Fb"],
        "shear_stress_Fv": props["Fv"],
        "framing_depth": float(
            roof_data.get("tji_depth") or roof_data.get("TJI_depth") or props.get("I", 0)
        ),
        "_tji_name": roof_data.get("tji_name") or roof_data.get("TJI_name"),
        "_tji_properties_row": props,
    }
    # Optional explicit section overrides for calculate_capacity (skip bd^2/6 etc.)
    out["_capacity_I_in4"] = props["I"]
    out["_capacity_S_in3"] = props["S"]
    return out
