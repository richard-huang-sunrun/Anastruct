"""Purlin sub-analysis: second structural pass on an existing roof plane."""

from __future__ import annotations

import copy
import math
import re
from typing import Any, Callable, Dict, List, Optional, Tuple


def _first(roof_data: dict, *keys: str, default=None):
    for key in keys:
        if key in roof_data and roof_data[key] is not None and str(roof_data[key]).strip() != "":
            return roof_data[key]
    purlins = roof_data.get("Purlins") or roof_data.get("purlins")
    if isinstance(purlins, dict):
        for key in keys:
            if key in purlins and purlins[key] is not None and str(purlins[key]).strip() != "":
                return purlins[key]
    return default


def _truthy(val) -> bool:
    if val is True:
        return True
    if val is False or val is None:
        return False
    if isinstance(val, (int, float)):
        return val != 0
    return str(val).strip().lower() in ("true", "yes", "1", "y")


def parse_length_ft(value) -> float:
    """Parse span lengths from feet, feet'inches strings, or numeric feet."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return 0.0
    if re.fullmatch(r"-?\d+(\.\d+)?", text):
        return float(text)
    # 4' 6" / 4'6" / 4 ft 6 in
    m = re.match(
        r"(?P<ft>-?\d+(?:\.\d+)?)\s*(?:'|ft|feet)?\s*(?P<in>-?\d+(?:\.\d+)?)?\s*(?:\"|in|inches)?",
        text,
        re.IGNORECASE,
    )
    if m:
        feet = float(m.group("ft"))
        inches = float(m.group("in") or 0)
        return feet + inches / 12.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def _parse_purlin_dims(roof_data: dict) -> Tuple[Optional[float], Optional[float]]:
    breadth = _first(roof_data, "purlin_breadth", "purlinBreadth")
    depth = _first(roof_data, "purlin_depth", "purlinDepth")
    if breadth is not None and depth is not None:
        return float(parse_length_ft(breadth) if "'" in str(breadth) else breadth), float(
            parse_length_ft(depth) if "'" in str(depth) else depth
        )
    size = _first(roof_data, "purlin_size", "purlinSize")
    if size and "x" in str(size).lower():
        parts = str(size).lower().split("x")
        try:
            nom_b = float(parts[0])
            nom_d = float(parts[1])
        except ValueError:
            return None, None
        cut = str(_first(roof_data, "purlin_cut", "purlinCut", "purlin_size_type", "purlinSizeType") or "Nominal")
        if cut.lower() == "nominal":
            return 1.5 if nom_b <= 2.5 else nom_b, 3.5 if nom_d <= 4 else nom_d
        return nom_b, nom_d
    return None, None


def _purlin_spacing_in(roof_data: dict) -> Optional[float]:
    raw = _first(
        roof_data,
        "purlin_spacing",
        "purlinSpacing",
        "purlin_strut_spacing",
        "purlinStrutSpacing",
        "oc",
    )
    if raw is None:
        return None
    try:
        spacing = float(raw)
    except (TypeError, ValueError):
        return None
    return spacing if spacing > 0 else None


def purlin_configuration(roof_data: dict) -> Dict[str, Any]:
    """Return normalized purlin inputs and whether a sub-analysis was requested."""
    attach = _truthy(_first(roof_data, "attachToPurlins", "attach_to_purlins"))
    spacing = _purlin_spacing_in(roof_data)
    breadth, depth = _parse_purlin_dims(roof_data)
    axis_raw = _first(roof_data, "purlin_axis", "purlinAxis", "purlin_strong_axis", "purlinStrongAxis")

    span1 = parse_length_ft(_first(roof_data, "purlin_span_1", "purlinSpan1", "purlin_span1"))
    span2 = parse_length_ft(_first(roof_data, "purlin_span_2", "purlinSpan2", "purlin_span2"))
    spans_ft = [span1, span2, 0.0, 0.0]
    # Same layout as the rafter span_locations: [overhang, span1, span2, span3].
    explicit = _first(roof_data, "purlin_span_locations", "purlinSpanLocations")
    explicit = isinstance(explicit, (list, tuple)) and len(explicit) > 0 and explicit
    if explicit:
        spans_ft = ([parse_length_ft(s) for s in explicit] + [0.0, 0.0, 0.0, 0.0])[:4]

    has_size = breadth is not None and depth is not None
    axis_label = ""
    has_axis = False
    if axis_raw is True or axis_raw is False:
        has_axis = True
        axis_label = "Strong" if axis_raw else "Flat"
    elif axis_raw is not None and str(axis_raw).strip():
        token = str(axis_raw).strip().lower()
        if token in ("strong", "flat", "yes", "no", "y", "n"):
            has_axis = True
            axis_label = "Flat" if token in ("flat", "no", "n") else "Strong"
        elif _truthy(axis_raw):
            has_axis = True
            axis_label = "Strong"

    configured = attach and spacing is not None and has_size and has_axis
    has_spans = any(s > 0 for s in spans_ft[1:]) if explicit else (span1 > 0 or span2 > 0)

    return {
        "attach_to_purlins": attach,
        "purlin_spacing_in": spacing,
        "purlin_breadth_in": breadth,
        "purlin_depth_in": depth,
        "purlin_axis": axis_label,
        "span_locations_ft": spans_ft,
        "configured": configured,
        "has_spans": has_spans,
    }


def build_purlin_roof_overlay(roof_data: dict, config: Dict[str, Any]) -> dict:
    """Copy roof payload and override member inputs for the purlin pass."""
    overlay = copy.deepcopy(roof_data)
    spacing = config["purlin_spacing_in"]
    breadth = float(config["purlin_breadth_in"])
    depth = float(config["purlin_depth_in"])
    axis = config["purlin_axis"]
    spans = list(config["span_locations_ft"])

    if axis == "Flat":
        breadth, depth = depth, breadth

    overlay["memberspacing"] = spacing
    overlay["membertype"] = "Purlin"
    overlay["framing_breadth"] = breadth
    overlay["framing_depth"] = depth
    overlay["span_locations"] = spans

    # Section properties (rectangular); optional overrides from payload
    ib = _first(roof_data, "purlin_member_I", "purlinMemberI")
    ab = _first(roof_data, "purlin_member_A", "purlinMemberA")
    if ib is not None:
        overlay["member_I"] = float(ib)
    else:
        overlay["member_I"] = breadth * (depth ** 3) / 12.0
    if ab is not None:
        overlay["member_A"] = float(ab)
    else:
        overlay["member_A"] = breadth * depth

    # Flat-use and strong-axis size factors both come from CF_B on the payload (S-tab ref row).
    cf_b = _first(roof_data, "purlin_CF_B", "purlin_cf_b", "CF_B")
    if cf_b is not None and str(cf_b).strip() != "":
        overlay["CF_B"] = float(cf_b)

    overlay["_purlin_subanalysis"] = True
    return overlay


def run_purlin_subanalysis(
    roof_data: dict,
    top_level: dict,
    analyze_roof: Callable[[dict, dict], dict],
) -> Optional[Dict[str, Any]]:
    """
    Run nested purlin analysis. Does not change the primary roof pass/fail.
    Returns None when purlin sub-analysis does not apply.
    """
    config = purlin_configuration(roof_data)

    if not config["attach_to_purlins"]:
        return None

    meta = {
        "performed": False,
        "inputs": {k: v for k, v in config.items() if k not in ("configured", "has_spans")},
    }

    if not config["configured"]:
        meta["error"] = "Incomplete purlin inputs (spacing, size, or axis missing)."
        return meta

    if not config["has_spans"]:
        meta["error"] = "Purlin spans are required when other purlin attributes are provided."
        return meta

    overlay = build_purlin_roof_overlay(roof_data, config)
    try:
        result = analyze_roof(overlay, top_level)
    except Exception as exc:
        meta["error"] = f"Purlin analysis failed: {exc}"
        return meta

    meta["performed"] = True
    meta["result"] = result
    return meta
