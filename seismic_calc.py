"""
Seismic lateral equivalents for roof/mass — standalone helper for API payloads.

DETDB typically carries Ss, S1, R, Cd, Ie, etc.; this function maps common keys
and returns horizontal equivalent values suitable for reporting or downstream use.

Not wired into the FEA line model unless loads are applied explicitly later.
"""

from __future__ import annotations

import math
from typing import Any, Mapping


def _f(mapping: Mapping[str, Any], *keys: str, default: float = 0.0) -> float:
    for k in keys:
        v = mapping.get(k)
        if v is None or v == "":
            continue
        try:
            return float(v)
        except (TypeError, ValueError):
            continue
    return default


def calculate_seismic_effects(
    roof_data: Mapping[str, Any],
    global_data: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Compute simplified seismic parameters from roof + optional top-level DETDB payload.

    Returns a dict safe to attach to JSON output (e.g. final_result['seismic']).

    Uses ASCE 7-style notation where present:
      - Ss, S1 site coefficients (or from global_data / DesignCriteria)
      - R, Cd response modification and deflection amplification
      - Ie importance factor
    """
    g = global_data or {}
    dc = g.get("DesignCriteria") if isinstance(g.get("DesignCriteria"), Mapping) else {}

    Ss = _f(roof_data, "Ss", "ss", "spectral_Ss", default=_f(dc, "Ss", "ss", default=0.0))
    S1 = _f(roof_data, "S1", "s1", "spectral_S1", default=_f(dc, "S1", "s1", default=0.0))
    R = _f(roof_data, "R", "response_modification_R", default=_f(dc, "R", default=1.0))
    if R <= 0:
        R = 1.0
    Cd = _f(roof_data, "Cd", "cd", "deflection_amplification_Cd", default=_f(dc, "Cd", "cd", default=1.0))
    Ie = _f(roof_data, "Ie", "ie", "importance_Ie", default=_f(dc, "Ie", "ie", default=1.0))

    # Approximate short-period design spectral acceleration SDS = 2/3 * Fa * Ss (Fa=1 if omitted)
    Fa = _f(roof_data, "Fa", "fa", default=_f(dc, "Fa", "fa", default=1.0))
    SDS = (2.0 / 3.0) * Fa * Ss

    # Horizontal acceleration coefficient (strength-level) for use with weight
    kh = SDS / R if R else SDS

    dead_total_psf = _f(
        roof_data,
        "dead_load_roofing",
        default=0.0,
    ) + _f(roof_data, "dead_load_pv", default=0.0)

    roof_area_sf = _f(roof_data, "roof_area_sf", "footprint_area_sf", default=0.0)

    equiv_base_shear_lb = kh * Ie * dead_total_psf * roof_area_sf if roof_area_sf > 0 else math.nan

    return {
        "Ss": Ss,
        "S1": S1,
        "SDS_approx": SDS,
        "R": R,
        "Cd": Cd,
        "Ie": Ie,
        "Fa": Fa,
        "horizontal_coeff_kh": kh,
        "dead_load_psf_for_seismic": dead_total_psf,
        "roof_area_sf": roof_area_sf,
        "equivalent_base_shear_lb": equiv_base_shear_lb,
    }
