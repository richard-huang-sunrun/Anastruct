from flask import Flask, request, jsonify

import anastruct

from anastruct import SystemElements, LoadCase

import numpy as np

import math

from tji_properties import apply_tji_to_roof_inputs
from seismic_calc import calculate_seismic_effects
from purlin_analysis import run_purlin_subanalysis


app = Flask(__name__)


# Constants

SPECIES = "DFL"

GRADE = "#2"

  # Bending stress (psi)

  # Modulus of Elasticity (psi)

 # Minimum Modulus of Elasticity (psi)

 # Shear stress (psi)

  # Specific gravity


# Load duration factors

# CD_D = 0.9

# CD_L = 1.25

# CD_S = 1.15

# CD_W = 1.6


# Adjustment factors


# Cr = 1.15


def _lateral_stability_cl_neg(depth, breadth, fb_star, fbe, is_tji=False):
    if is_tji or depth / breadth <= 5:
        return 1.0
    return (1 + (fbe / fb_star)) / 1.9 - (
        ((1 + (fbe / fb_star)) / 1.9) ** 2 - (fbe / fb_star / 0.95)
    ) ** 0.5


def calculate_capacity(spans, spacing, depth, breadth, pitch, overhang, E, Emin, Fb, Fv, G, CF_B, CF_C, Cr, CD_D, CD_L, CD_S, CD_W,
                       capacity_I_in4=None, capacity_S_in3=None, is_tji=False):

    """

    Calculate the capacity of a wood member based on its spans, spacing, depth, breadth, pitch, and overhang.


    Parameters:

    spans (list of float): List of span lengths in feet.

    spacing (float): Spacing between members in inches.

    depth (float): Depth of the member in inches.

    breadth (float): Breadth of the member in inches.

    pitch (float): Roof pitch in degrees.

    overhang (float): Overhang length in feet.

    E (float): Modulus of elasticity.

    Emin (float): Minimum modulus of elasticity.

    Fb (float): Bending stress.

    Fv (float): Shear stress.

    G (float): Specific gravity.

    CF_Fb (float): Load duration factor.

    Cr (float): Repetitive member factor.

    CD_D (float): Duration of load factor for dead load.

    CD_L (float): Duration of load factor for live load.

    CD_S (float): Duration of load factor for snow load.

    CD_W (float): Duration of load factor for wind load.


    Returns:

    dict: Calculated capacities including moment, shear, and deflection.

    """

    print(

        f"Inputs - spans: {spans}, spacing: {spacing}, depth: {depth}, breadth: {breadth}, pitch: {pitch}, overhang: {overhang}, E: {E}, Emin: {Emin}, Fb: {Fb}, Fv: {Fv}, G: {G}")

    # Calculate lu as the maximum span length

    if is_tji:
        CF_B = 1.0
        Cr = 1.0

    CF_Fb = CF_B

    CF_Ft = CF_B

    CF_Fc = CF_C

    lu = max(spans) * 12

    print(f"lu (max span length in inches): {lu}")


    # Calculate lu/d

    lu_d = lu / depth

    print(f"lu_d (lu/depth): {lu_d}")


    # Compute le based on the provided formula

    if overhang != 0:

        if lu_d < 7:

            le = 1.87 * lu

        else:

            le = 1.44 * lu + (3 * depth)

    else:

        if lu_d < 7:

            le = 2.06 * lu

        elif lu_d <= 14.3:

            le = (1.63 * lu) + (3 * depth)

        else:

            le = 1.84 * lu

    print(f"le: {le}")


    # Calculate RB

    RB = ((le * depth) / (breadth ** 2)) ** 0.5

    print(f"RB: {RB}")


    # Calculate FbE

    FbE = 1.2 * Emin / (RB ** 2)

    print(f"FbE: {FbE}")


    # Calculate Fv' for different load cases

    Fv_prime_D = Fv * CD_D

    Fv_prime_Lr = Fv * CD_L

    Fv_prime_S = Fv * CD_S

    Fv_prime_W = Fv * CD_W

    print(f"Fv_prime_D: {Fv_prime_D}, Fv_prime_Lr: {Fv_prime_Lr}, Fv_prime_S: {Fv_prime_S}, Fv_prime_W: {Fv_prime_W}")


    # Calculate Fb'(+) and Fb*(-) for D

    Fb_prime_pos_D = Fb * CD_D * CF_Fb * Cr

    Fb_star_D = Fb * CD_D * CF_Fb * Cr


    CL_neg_D = _lateral_stability_cl_neg(depth, breadth, Fb_star_D, FbE, is_tji=is_tji)

    Fb_prime_neg_D = Fb * CD_D * CL_neg_D * CF_Fb * Cr

    print(f"Fb_prime_pos_D: {Fb_prime_pos_D}, Fb_prime_neg_D: {Fb_prime_neg_D}")


    # Calculate Fb'(+) and Fb*(-) for D + Lr

    Fb_prime_pos_Lr = Fb * CF_Fb * Cr * CD_L

    Fb_star_Lr = Fb * CF_Fb * Cr * CD_L


    CL_neg_Lr = _lateral_stability_cl_neg(depth, breadth, Fb_star_Lr, FbE, is_tji=is_tji)

    Fb_prime_neg_Lr = Fb * CL_neg_Lr * CF_Fb * Cr * CD_L

    print(f"Fb_prime_pos_Lr: {Fb_prime_pos_Lr}, Fb_prime_neg_Lr: {Fb_prime_neg_Lr}")


    # Calculate Fb'(+) and Fb*(-) for D + S

    Fb_prime_pos_S = Fb * CF_Fb * Cr * CD_S

    Fb_star_S = Fb * CF_Fb * Cr * CD_S


    CL_neg_S = _lateral_stability_cl_neg(depth, breadth, Fb_star_S, FbE, is_tji=is_tji)

    Fb_prime_neg_S = Fb * CL_neg_S * CF_Fb * Cr * CD_S

    print(f"Fb_prime_pos_S: {Fb_prime_pos_S}, Fb_prime_neg_S: {Fb_prime_neg_S}")


    # Calculate Fb'(+) and Fb*(-) for wind load cases

    Fb_prime_pos_W = Fb * CF_Fb * Cr * CD_W

    Fb_star_W = Fb * CF_Fb * Cr * CD_W


    CL_neg_W = _lateral_stability_cl_neg(depth, breadth, Fb_star_W, FbE, is_tji=is_tji)

    Fb_prime_neg_W = Fb * CL_neg_W * CF_Fb * Cr * CD_W

    print(f"Fb_prime_pos_W: {Fb_prime_pos_W}, Fb_prime_neg_W: {Fb_prime_neg_W}")


    # Convert lu from feet to inches

    lu_inches = lu * 12

    print(f"lu_inches: {lu_inches}")


    # Calculate the section modulus (S) and moment of inertia (I)

    S = (breadth * (depth ** 2)) / 6

    I = (breadth * (depth ** 3)) / 12

    A = breadth * depth  # Cross-sectional area

    if capacity_I_in4 is not None and capacity_S_in3 is not None:

        I = float(capacity_I_in4)

        S = float(capacity_S_in3)

        print(f"TJI section: using table I={I} in^4, S={S} in^3; A={A} in^2 (breadth x depth)")

    print(f"S (section modulus): {S}, I (moment of inertia): {I}, A (cross-sectional area): {A}")


    # Calculate allowable bending moment (M) for different load duration factors

    M_allowable_D = Fb_prime_neg_D * S / 12

    M_allowable_L = Fb_prime_pos_D * S / 12  # Assuming same positive and negative for demonstration; adjust as necessary

    print(f"M_allowable_D: {M_allowable_D}, M_allowable_L: {M_allowable_L}")


    # Calculate allowable bending moment (M) for D + Lr

    M_allowable_Lr_pos = Fb_prime_pos_Lr * S / 12

    M_allowable_Lr_neg = Fb_prime_neg_Lr * S / 12

    print(f"M_allowable_Lr_pos: {M_allowable_Lr_pos}, M_allowable_Lr_neg: {M_allowable_Lr_neg}")


    # Calculate allowable bending moment (M) for D + S

    M_allowable_S_pos = Fb_prime_pos_S * S / 12

    M_allowable_S_neg = Fb_prime_neg_S * S / 12

    print(f"M_allowable_S_pos: {M_allowable_S_pos}, M_allowable_S_neg: {M_allowable_S_neg}")


    # Calculate allowable bending moment (M) for wind load cases

    M_allowable_W_pos = Fb_prime_pos_W * S / 12

    M_allowable_W_neg = Fb_prime_neg_W * S / 12

    print(f"M_allowable_W_pos: {M_allowable_W_pos}, M_allowable_W_neg: {M_allowable_W_neg}")


    # Calculate maximum shear force (V) for different load duration factors

    # Rectangular beam: V = (2/3) Fv' b d = (2/3) Fv' A for solid section

    V_allowable_D = (2 / 3) * A * Fv_prime_D

    V_allowable_Lr = (2 / 3) * A * Fv_prime_Lr

    V_allowable_S = (2 / 3) * A * Fv_prime_S

    V_allowable_W = (2 / 3) * A * Fv_prime_W

    print(f"V_allowable_D: {V_allowable_D}, V_allowable_Lr: {V_allowable_Lr}, V_allowable_S: {V_allowable_S}, V_allowable_W: {V_allowable_W}")


    # Calculate deflection (Δ)

    load_uniform = 30 * (spacing / 12)  # Uniform load per unit length (psf), for example 30 psf live load

    Δ = (5 * load_uniform * (lu_inches ** 4)) / (384 * E * I)

    print(f"Deflection (Δ): {Δ}")


    # Convert pitch to radians

    pitch_rad = np.deg2rad(pitch)

    print(f"Pitch (radians): {pitch_rad}")


    # Adjust capacities based on pitch

    # M_allowable_D *= np.cos(pitch_rad)

    # M_allowable_L *= np.cos(pitch_rad)

    # M_allowable_Lr_pos *= np.cos(pitch_rad)

    # M_allowable_Lr_neg *= np.cos(pitch_rad)

    # M_allowable_S_pos *= np.cos(pitch_rad)

    # M_allowable_S_neg *= np.cos(pitch_rad)

    # M_allowable_W_pos *= np.cos(pitch_rad)

    # M_allowable_W_neg *= np.cos(pitch_rad)

    # V_allowable_D *= np.cos(pitch_rad)

    # V_allowable_Lr *= np.cos(pitch_rad)

    # V_allowable_S *= np.cos(pitch_rad)

    # V_allowable_W *= np.cos(pitch_rad)

    # Δ *= np.cos(pitch_rad)

    print(f"Adjusted capacities based on pitch - M_allowable_D: {M_allowable_D}, M_allowable_L: {M_allowable_L}, M_allowable_Lr_pos: {M_allowable_Lr_pos}, M_allowable_Lr_neg: {M_allowable_Lr_neg}, M_allowable_S_pos: {M_allowable_S_pos}, M_allowable_S_neg: {M_allowable_S_neg}, M_allowable_W_pos: {M_allowable_W_pos}, M_allowable_W_neg: {M_allowable_W_neg}, V_allowable_D: {V_allowable_D}, V_allowable_Lr: {V_allowable_Lr}, V_allowable_S: {V_allowable_S}, V_allowable_W: {V_allowable_W}, Deflection (Δ): {Δ}")


    return {

        "M_allowable_D": M_allowable_D,

        "M_allowable_L": M_allowable_L,

        "V_allowable_D": V_allowable_D,

        "M_allowable_Lr_pos": M_allowable_Lr_pos,

        "M_allowable_Lr_neg": M_allowable_Lr_neg,

        "V_allowable_Lr": V_allowable_Lr,

        "M_allowable_S_pos": M_allowable_S_pos,

        "M_allowable_S_neg": M_allowable_S_neg,

        "V_allowable_S": V_allowable_S,

        "M_allowable_W_pos": M_allowable_W_pos,

        "M_allowable_W_neg": M_allowable_W_neg,

        "V_allowable_W": V_allowable_W,

        "deflection": Δ,

        "lu": lu,

        "lu_d": lu_d,

        "le": le,

        "Fb_prime_pos_D": Fb_prime_pos_D,

        "Fb_prime_neg_D": Fb_prime_neg_D,

        "Fb_prime_pos_Lr": Fb_prime_pos_Lr,

        "Fb_prime_neg_Lr": Fb_prime_neg_Lr,

        "Fb_prime_pos_S": Fb_prime_pos_S,

        "Fb_prime_neg_S": Fb_prime_neg_S,

        "Fb_prime_pos_W": Fb_prime_pos_W,

        "Fb_prime_neg_W": Fb_prime_neg_W,

        "V_allowable_D": V_allowable_D,

        "V_allowable_Lr": V_allowable_Lr,

        "V_allowable_S": V_allowable_S,

        "V_allowable_W": V_allowable_W

    }




def build_stations(spans_ft, mods_ft, ndigits=6):

    """Unique, sorted beam stations (ft) plus the support and module stations on them.

    Positions are rounded so a module edge that lands on a support (or trailing zero
    spans) shares one station instead of creating a near-zero-length element.
    """

    supports = []

    total = 0.0

    for s in spans_ft:

        total += float(s)

        supports.append(round(total, ndigits))

    mods = sorted(round(float(m), ndigits) for m in mods_ft)

    stations = sorted({0.0, *supports, *mods})

    return stations, sorted(set(supports)), mods


def station_node_id(stations, x):

    """Node id of station x: the origin is node 1 and each station gap has a midpoint node."""

    return 2 * stations.index(x) + 1


def default_roofing_dead_load(roof_type, roof_weight=0):

    """Roofing dead load (psf): roof weight when given, else by roof type."""

    try:

        roof_weight = float(roof_weight or 0)

    except (TypeError, ValueError):

        roof_weight = 0.0

    if roof_weight != 0:

        return roof_weight

    return {"shingle": 10.0, "tile": 14.0, "metal": 9.0}.get(str(roof_type).strip().lower(), 10.0)


def default_pv_dead_load(racking):

    """PV dead load (psf) added on top of roofing: tilt kit 4, flush mount / other 3."""

    return 4.0 if str(racking).strip().upper() == "TK" else 3.0


def _truthy_slippery(val):

    """Parse DETDB slippery surface: Yes/True/1 -> True, No/False/0 -> False."""

    if val is None:

        return None

    s = str(val).strip().lower()

    if s in ("yes", "y", "true", "1", "slippery"):

        return True

    if s in ("no", "n", "false", "0", "non-slippery", "nonslippery"):

        return False

    return None


def _roof_index_from_payload(roof_entry, roofs_list):

    """Resolve RX/RY index from dict {index: n} or {'id': 'roof_1'} style."""

    if "index" in roof_entry:

        try:

            return int(roof_entry["index"])

        except (TypeError, ValueError):

            return None

    rid = roof_entry.get("id") or roof_entry.get("roof_id")

    if rid is None:

        return None

    for i, r in enumerate(roofs_list):

        if r.get("id") == rid or r.get("roof_id") == rid:

            return i

    return None


def apply_slippery_surface_snow_balance(snow_post, snow_pre, slippery_flag):

    """

    If slippery surface is No, PV snow uses the same balanced load as non-PV zone.

    DETDB supplies slippery_surface (Yes/No).

    """

    meta = {"slippery_surface": slippery_flag, "adjusted": False}

    tri = _truthy_slippery(slippery_flag)

    if tri is False:

        meta["adjusted"] = True

        return snow_pre, snow_pre, meta

    return snow_post, snow_pre, meta


def compute_sliding_snow_p_add(rx, ry, Pf_psf):

    """

    Snow sliding from upper roof RX onto lower roof RY (ASCE-style surcharge strip).

    Wx = (eave-to-ridge RX, ft) * cos(pitch_rx); Wy = (eave-to-ridge RY, ft) * cos(pitch_ry)

    P_sliding = 0.4 * Pf * Wx  (Pf = flat/balanced snow psf on RX)

    P_add = P_sliding / min(Wy, 15)

    """

    sliding = rx.get("sliding_snow") if rx.get("sliding_snow") is not None else rx.get("Sliding_Snow")

    if sliding is None or str(sliding).strip() == "":

        return None

    s = str(sliding).strip().lower()

    if s not in ("true", "1", "yes", "y"):

        return None

    try:

        etor_rx_ft = float(rx.get("etor", 0))

        etor_ry_ft = float(ry.get("etor", 0))

        pitch_rx_deg = float(rx.get("pitch", 0))

        pitch_ry_deg = float(ry.get("pitch", 0))

    except (TypeError, ValueError):

        return None

    prx = math.radians(pitch_rx_deg)

    pry = math.radians(pitch_ry_deg)

    Wx = etor_rx_ft * math.cos(prx)

    Wy = etor_ry_ft * math.cos(pry)

    if Wx <= 0 or Wy <= 0 or Pf_psf <= 0:

        return None

    P_sliding = 0.4 * Pf_psf * Wx

    denom = Wy if Wy < 15.0 else 15.0

    P_add = P_sliding / denom

    return {

        "P_sliding_lb_per_ft_horizontal": P_sliding,

        "P_add_psf": P_add,

        "strip_horizontal_ft": denom,

        "Wx_ft": Wx,

        "Wy_ft": Wy,

        "Pf_psf": Pf_psf,

        "rx_id": rx.get("id", ""),

        "ry_id": ry.get("id", ""),

    }


def _element_ids_in_horizontal_strip(member_coordinates, strip_horizontal_m):

    """Element ids (1-based) whose midpoint lies within horizontal strip from eave."""

    n_elems = len(member_coordinates) - 1

    ids = []

    for elem_id in range(1, n_elems + 1):

        h0 = float(member_coordinates[elem_id - 1][0])

        h1 = float(member_coordinates[elem_id][0])

        mid = 0.5 * (h0 + h1)

        if mid <= strip_horizontal_m + 1e-9:

            ids.append(elem_id)

    return ids


def _intersect_element_ids(left, right):

    right_set = set(right)

    return [x for x in left if x in right_set]


def accumulate_sliding_snow_pairs(roofs_list):

    """Mutate roofs_list with P_add from sliding snow pairs."""

    pairs = []

    for rx in roofs_list:

        raw = rx.get("sliding_snow_pairs") or rx.get("sliding_snow_pair")

        if not raw:

            continue

        if isinstance(raw, dict):

            pairs.append(raw)

        elif isinstance(raw, list):

            pairs.extend(raw)

    for p in pairs:

        if not isinstance(p, dict):

            continue

        i_rx = _roof_index_from_payload({"index": p.get("RX")}, roofs_list)

        i_ry = _roof_index_from_payload({"index": p.get("RY")}, roofs_list)

        if i_rx is None:

            i_rx = _roof_index_from_payload({"id": p.get("rx") or p.get("RX_id")}, roofs_list)

        if i_ry is None:

            i_ry = _roof_index_from_payload({"id": p.get("ry") or p.get("RY_id")}, roofs_list)

        if i_rx is None or i_ry is None:

            continue

        rx = roofs_list[i_rx]

        ry = roofs_list[i_ry]

        raw_pre = float(rx.get("_raw_snow_pre_pv", rx.get("snow_pre_pv", 0)))

        raw_post = float(rx.get("_raw_snow_post_pv", rx.get("snow_post_pv", 0)))

        Pf = max(raw_pre, raw_post)

        detail = compute_sliding_snow_p_add(rx, ry, Pf)

        if not detail:

            continue

        p_add = float(detail["P_add_psf"])

        strip_ft = float(detail.get("strip_horizontal_ft", min(float(detail["Wy_ft"]), 15.0)))

        ry["_sliding_snow_surcharge_psf"] = float(ry.get("_sliding_snow_surcharge_psf", 0)) + p_add

        ry["_sliding_snow_strip_horizontal_ft"] = max(

            float(ry.get("_sliding_snow_strip_horizontal_ft", 0)), strip_ft

        )

        ry.setdefault("_sliding_snow_received", []).append(detail)


def analyze_roof(roof_data, top_level):


    slippery_meta = {}

    tji_application = {}

    cap_I_in4 = None

    cap_S_in3 = None

    # Extracting roof parameters

    racking = roof_data.get('racking', '')

    comp_beneath_PV_import = roof_data.get('compPV', '')

    roof_type = roof_data.get('rooftype', '')

    member_type = roof_data.get('membertype', '')

    member_spacing = float(roof_data.get('memberspacing', 24))  # Provide a default value if not found

    roof_height = float(roof_data.get('roofheight', 1))

    modulus_E = float(roof_data.get('modulus_E', 1600000))

    member_A = float(roof_data.get('member_A', 5.25))

    member_I = float(roof_data.get('member_I', 5.359375))

    # Constructing list_EAI

    list_EAI = [modulus_E, member_A, member_I]


    modulus_E_minimum = float(roof_data.get('modulus_E_minimum', 580000))

    shear_stress_Fv = float(roof_data.get('shear_stress_Fv', 180))

    specific_gravity_G = float(roof_data.get('specific_gravity_G', 0.5))

    bending_stress_Fb = float(roof_data.get('bending_stress_Fb', 900))

    framing_breadth = float(roof_data.get('framing_breadth', 1.5))

    framing_depth = float(roof_data.get('framing_depth', 3.5))


    tji_patch = apply_tji_to_roof_inputs(roof_data, member_type=str(member_type))

    if tji_patch:

        modulus_E = float(tji_patch["modulus_E"])

        member_A = float(tji_patch["member_A"])

        member_I = float(tji_patch["member_I"])

        bending_stress_Fb = float(tji_patch["bending_stress_Fb"])

        shear_stress_Fv = float(tji_patch["shear_stress_Fv"])

        framing_depth = float(tji_patch["framing_depth"])

        list_EAI = [modulus_E, member_A, member_I]

        cap_I_in4 = tji_patch.get("_capacity_I_in4")

        cap_S_in3 = tji_patch.get("_capacity_S_in3")

        tji_application = {

            "tji_model": roof_data.get("tji_model") or roof_data.get("TJI_model"),

            "tji_depth": roof_data.get("tji_depth") or roof_data.get("TJI_depth"),

            "tji_name": tji_patch.get("_tji_name"),

            "table_row": tji_patch.get("_tji_properties_row"),

        }


    eave_to_ridge = float(roof_data.get('etor', 10))

    mod_locations = roof_data.get('mod_locations', [0.001, 10.001])

    spans= roof_data.get('span_locations', [2, 8, 0, 0])

    spanscap = spans.copy()

    deg_pitch = float(roof_data.get('pitch', 18))

    wind_pressure_down = float(roof_data.get('wind_pressure_down', 16))

    wind_pressure_up = float(roof_data.get('wind_pressure_up', -16))

    wind_pressures = [wind_pressure_down, wind_pressure_up]

    slippery_flag = roof_data.get("slippery_surface")

    if slippery_flag is None:

        slippery_flag = roof_data.get("Slippery_Surface")

    snow_pre_pv = float(roof_data.get('snow_pre_pv', 0))

    snow_post_pv = float(roof_data.get('snow_post_pv', 0))

    roof_data["_raw_snow_pre_pv"] = snow_pre_pv

    roof_data["_raw_snow_post_pv"] = snow_post_pv

    asce_version = str(roof_data.get('ASCE', top_level.get('ASCE', ''))).strip()

    if asce_version == '7-22':

        snow_pre_pv *= 0.7

        snow_post_pv *= 0.7

    snow_post_pv, snow_pre_pv, slippery_meta = apply_slippery_surface_snow_balance(

        snow_post_pv, snow_pre_pv, slippery_flag

    )

    snow_string = [snow_post_pv, snow_pre_pv]

    snow = snow_string

    overhang = float(roof_data.get('overhang', 0))

    dead_load_roofing = roof_data.get('dead_load_roofing')

    if dead_load_roofing is None or str(dead_load_roofing).strip() == '':

        dead_load_roofing = default_roofing_dead_load(roof_type, roof_data.get('roofweight', 0))

    dead_load_roofing = float(dead_load_roofing)

    dead_load_pv = roof_data.get('dead_load_pv')

    if dead_load_pv is None or str(dead_load_pv).strip() == '':

        dead_load_pv = default_pv_dead_load(racking)

    dead_load_pv = float(dead_load_pv)

    live_load_post_pv = float(roof_data.get('live_load_post_pv', 0))

    nonPV_LL = float(roof_data.get('live_load_pre_pv', 20))

    nonPV_DL=dead_load_roofing

    PV_DL= nonPV_DL+dead_load_pv


    CD_D = float(roof_data.get('CD_D', 0.9))

    CD_L = float(roof_data.get('CD_L', 1.25))

    CD_S = float(roof_data.get('CD_S', 1.15))

    CD_W = float(roof_data.get('CD_W', 1.6))


    CF_B = float(roof_data.get('CF_B', 1.3))  # Default value of 1.3 if not provided

    CF_T = float(roof_data.get('CF_T', 1.3))  # Default value of 1.3 if not provided

    cf_c_raw = roof_data.get('CF_C')

    if cf_c_raw is not None and str(cf_c_raw).strip() != '':

        CF_C = float(cf_c_raw)

    elif asce_version == '7-22':

        CF_C = 1.2

    else:

        CF_C = 1.1


    if member_spacing <= 24:

        Cr = 1.15

    else:

        Cr = 1.0

    is_tji_member = str(member_type).strip().upper() == "TJI"

    if is_tji_member:

        CF_B = 1.0

        Cr = 1.0

        tji_application.setdefault("capacity_factors", {})

        tji_application["capacity_factors"].update({"CL_neg": 1.0, "Cr": 1.0, "CF_B": 1.0})


    # print(f"racking: {racking}")

    # print(f"comp_beneath_PV_import: {comp_beneath_PV_import}")

    # print(f"roof_type: {roof_type}")

    # print(f"member_type: {member_type}")

    # print(f"member_spacing: {member_spacing}")

    # print(f"roof_height: {roof_height}")

    # print(f"modulus_E: {modulus_E}")

    # print(f"member_A: {member_A}")

    # print(f"member_I: {member_I}")

    # print(f"list_EAI: {list_EAI}")

    # print(f"modulus_E_minimum: {modulus_E_minimum}")

    # print(f"shear_stress_Fv: {shear_stress_Fv}")

    # print(f"specific_gravity_G: {specific_gravity_G}")

    # print(f"bending_stress_Fb: {bending_stress_Fb}")

    # print(f"framing_breadth: {framing_breadth}")

    print(f"framing_depth: {framing_depth}")

    # print(f"eave_to_ridge: {eave_to_ridge}")

    # print(f"mod_locations: {mod_locations}")

    # print(f"spans: {spans}")

    # print(f"deg_pitch: {deg_pitch}")

    # print(f"wind_pressure_down: {wind_pressure_down}")

    # print(f"wind_pressure_up: {wind_pressure_up}")

    # print(f"wind_pressures: {wind_pressures}")

    # print(f"snow_pre_pv: {snow_pre_pv}")

    # print(f"snow_post_pv: {snow_post_pv}")

    # print(f"snow: {snow}")

    # print(f"overhang: {overhang}")

    # print(f"dead_load_roofing: {dead_load_roofing}")

    # print(f"dead_load_pv: {dead_load_pv}")

    # print(f"live_load_post_pv: {live_load_post_pv}")

    # print(f"nonPV_LL: {nonPV_LL}")

    # print(f"nonPV_DL: {nonPV_DL}")

    # print(f"PV_DL: {PV_DL}")

    # Convert units

    eave_to_ridge *= 0.3048

    member_spacing = (member_spacing / 12) * 0.3048


    for i in range(2):

        snow[i] = float(snow[i])


    pitch = np.deg2rad(deg_pitch)

    wind_load = float(wind_pressures[0])

    wind_up = float(wind_pressures[1])*0.6

    print(wind_load)

    print(wind_up)


    stations, support_stations, mod_stations = build_stations(spans, mod_locations)

    # Split each station gap in half for a more accurate deflection value.
    rafter_array = [stations[0]]

    for a, b in zip(stations, stations[1:]):

        rafter_array.extend([(a + b) / 2, b])

    member_coordinates = [[x * 0.3048 * np.cos(pitch), x * 0.3048 * np.sin(pitch)] for x in rafter_array]


    E = float(list_EAI[0]) * 6894.7572931783

    A = float(list_EAI[1]) * 0.00064516

    I = float(list_EAI[2]) * 0.000000416231426


    ss = SystemElements(EA=E * A, EI=E * I)

    for i in range(len(member_coordinates) - 1):

        ss.add_element(location=[member_coordinates[i], member_coordinates[i + 1]])


    is_truss = str(member_type).strip().lower() == "truss"

    support_node_ids = []

    for x in support_stations:

        support_node_id = station_node_id(stations, x)

        if is_truss:

            ss.add_support_fixed(node_id=support_node_id)

        else:

            ss.add_support_hinged(node_id=support_node_id)

        support_node_ids.append(support_node_id)


    PV_start = []

    PV_stop = []

    ndx = 0

    for x in mod_stations:

        mod_node_id = station_node_id(stations, x)

        if (ndx % 2) == 0:

            PV_start.append(mod_node_id)

            ndx += 1

        else:

            PV_stop.append(mod_node_id)

            ndx += 1


    PV_elements = []

    nonPV_elements = []

    PVi = 0

    for i in range(len(ss.node_map)):

        if i != 0:

            if i >= PV_start[PVi] and i < PV_stop[PVi]:

                PV_elements.append(i)

            else:

                nonPV_elements.append(i)

            if i == PV_stop[PVi] and PVi < len(PV_start) - 1:

                PVi += 1


    # if roof_type == "shingle":

    #     nonPV_DL = float(10)

    # elif roof_type == "tile":

    #     nonPV_DL = float(14)

    # else:

    #     nonPV_DL = float(8)


    PV_snow = snow[0]

    nonPV_snow = snow[1]


    # if racking == "FM":

    #     PV_DL = float(nonPV_DL + 3)

    # elif racking == "TK":

    #     PV_DL = float(nonPV_DL + 4)

    # else:

    #     PV_DL = float(nonPV_DL + 3)


    IEBC_nonPV_DL = nonPV_DL

    IEBC_nonPV_DL_LL = nonPV_DL + nonPV_LL

    IEBC_nonPV_DL_S = nonPV_DL + nonPV_snow

    IEBC_nonPV_DL_075LL_075S = nonPV_DL + (0.75 * nonPV_LL) + (0.75 * nonPV_snow)

    IEBC_PV_DL = PV_DL

    IEBC_PV_DL_S = PV_DL + PV_snow


    nonPV_DL *= 47.880258888889

    nonPV_LL *= 47.880258888889

    PV_DL *= 47.880258888889

    nonPV_snow *= 47.880258888889

    PV_snow *= 47.880258888889

    wind_load *= 47.880258888889

    wind_up *= 47.880258888889


    nonPV_DL *= member_spacing

    nonPV_LL *= member_spacing

    PV_DL *= member_spacing

    nonPV_snow *= member_spacing

    PV_snow *= member_spacing

    wind_load *= member_spacing

    wind_up *= member_spacing


    nonPV_DL *= np.cos(pitch)

    nonPV_LL *= np.cos(pitch) * np.cos(pitch)

    PV_DL *= np.cos(pitch)

    nonPV_snow *= np.cos(pitch) * np.cos(pitch)

    PV_snow *= np.cos(pitch) * np.cos(pitch)


    nonPV_DL_1 = nonPV_DL

    nonPV_DL_06 = nonPV_DL * 0.6

    PV_DL_1 = PV_DL

    PV_DL_06 = PV_DL * 0.6


    nonPV_LL_1 = nonPV_LL

    nonPV_LL_075 = nonPV_LL * 0.75


    nonPV_snow_1 = nonPV_snow

    nonPV_snow_075 = nonPV_snow * 0.75

    PV_snow_1 = PV_snow

    PV_snow_075 = PV_snow * 0.75


    wind_1 = wind_load

    wind_06 = wind_load * 0.6

    wind_045 = wind_load * 0.45


    lc_DL_nonPV = LoadCase("DL_nonPV")

    lc_DL_nonPV.q_load(q=-(nonPV_DL), element_id=nonPV_elements, direction="element")

    lc_DL_PV = LoadCase("DL_PV")

    lc_DL_PV.q_load(q=-(PV_DL), element_id=PV_elements, direction="element")


    lc_DL_LL_nonPV = LoadCase("DL_LL_nonPV")

    lc_DL_LL_nonPV.q_load(q=-(nonPV_DL + nonPV_LL), element_id=nonPV_elements, direction="element")

    lc_DL_LL_PV = LoadCase("DL_LL_PV")

    lc_DL_LL_PV.q_load(q=-(PV_DL), element_id=PV_elements, direction="element")


    lc_DL_LL_075_wind_045_live_075_nonPV = LoadCase("DL_LL_075_wind_045_live_075_nonPV")

    lc_DL_LL_075_wind_045_live_075_nonPV.q_load(q=-(nonPV_DL + wind_045 + nonPV_LL_075), element_id=nonPV_elements,

                                                direction="element")

    lc_DL_LL_075_wind_045_live_075_PV = LoadCase("DL_LL_075_wind_045_live_075_PV")

    lc_DL_LL_075_wind_045_live_075_PV.q_load(q=-(PV_DL + wind_045), element_id=PV_elements, direction="element")


    lc_DL_snow_nonPV = LoadCase("DL_snow_nonPV")

    lc_DL_snow_nonPV.q_load(q=-(nonPV_DL + nonPV_snow), element_id=nonPV_elements, direction="element")

    lc_DL_snow_PV = LoadCase("DL_snow_PV")

    lc_DL_snow_PV.q_load(q=-(PV_DL + PV_snow), element_id=PV_elements, direction="element")


    lc_DL_LL_075_wind_045_snow_075_nonPV = LoadCase("DL_LL_075_wind_045_snow_075_nonPV")

    lc_DL_LL_075_wind_045_snow_075_nonPV.q_load(q=-(nonPV_DL + wind_045 + nonPV_snow_075),

                                                element_id=nonPV_elements, direction="element")

    lc_DL_LL_075_wind_045_snow_075_PV = LoadCase("DL_LL_075_wind_045_snow_075_PV")

    lc_DL_LL_075_wind_045_snow_075_PV.q_load(q=-(PV_DL + wind_045 + PV_snow_075), element_id=PV_elements,

                                             direction="element")


    sliding_snow_psf = float(roof_data.get("_sliding_snow_surcharge_psf", 0) or 0)

    sliding_strip_ft = float(roof_data.get("_sliding_snow_strip_horizontal_ft", 0) or 0)

    sliding_line_snow = 0.0

    sliding_line_snow_075 = 0.0

    if sliding_snow_psf > 0 and sliding_strip_ft > 0:

        strip_m = sliding_strip_ft * 0.3048

        strip_elem_ids = _element_ids_in_horizontal_strip(member_coordinates, strip_m)

        sliding_line_snow = (

            sliding_snow_psf

            * 47.880258888889

            * member_spacing

            * np.cos(pitch)

            * np.cos(pitch)

        )

        sliding_line_snow_075 = sliding_line_snow * 0.75

        nonpv_strip = _intersect_element_ids(nonPV_elements, strip_elem_ids)

        pv_strip = _intersect_element_ids(PV_elements, strip_elem_ids)

        if nonpv_strip:

            lc_DL_snow_nonPV.q_load(q=-sliding_line_snow, element_id=nonpv_strip, direction="element")

            lc_DL_LL_075_wind_045_snow_075_nonPV.q_load(

                q=-sliding_line_snow_075, element_id=nonpv_strip, direction="element"

            )

        if pv_strip:

            lc_DL_snow_PV.q_load(q=-sliding_line_snow, element_id=pv_strip, direction="element")

            lc_DL_LL_075_wind_045_snow_075_PV.q_load(

                q=-sliding_line_snow_075, element_id=pv_strip, direction="element"

            )


    lc_DL_06_wind_06_nonPV = LoadCase("DL_06_wind_06_nonPV")

    lc_DL_06_wind_06_nonPV.q_load(q=-(nonPV_DL_06 + wind_up), element_id=nonPV_elements, direction="element")

    lc_DL_06_wind_06_PV = LoadCase("DL_06_wind_06_PV")

    lc_DL_06_wind_06_PV.q_load(q=-(PV_DL_06 + wind_up), element_id=PV_elements, direction="element")


    lc_DL_wind_06_nonPV = LoadCase("DL_wind_06_nonPV")

    lc_DL_wind_06_nonPV.q_load(q=-(nonPV_DL + wind_06), element_id=nonPV_elements, direction="element")

    lc_DL_wind_06_PV = LoadCase("DL_wind_06_PV")

    lc_DL_wind_06_PV.q_load(q=-(PV_DL + wind_06), element_id=PV_elements, direction="element")




    final_result = {

        "roof_id": roof_data.get("id", ""),

        "load_cases": {}

    }

    final_result["detdb_flags"] = {

        "slippery_surface": slippery_meta,

        "tji": tji_application,

        "sliding_snow_received": roof_data.get("_sliding_snow_received") or [],

        "sliding_snow_surcharge_psf": sliding_snow_psf,

        "sliding_snow_strip_horizontal_ft": sliding_strip_ft,

        "sliding_snow_applied_on_strip_only": bool(sliding_snow_psf > 0 and sliding_strip_ft > 0),

    }

    final_result["seismic"] = calculate_seismic_effects(roof_data, top_level)


    load_combinations = [

        ("D", [lc_DL_nonPV, lc_DL_PV]),

        ("D + Lr", [lc_DL_LL_nonPV, lc_DL_LL_PV]),

        ("D + 0.75(Lr + 0.6W)", [lc_DL_LL_075_wind_045_live_075_nonPV, lc_DL_LL_075_wind_045_live_075_PV]),

        ("D + S", [lc_DL_snow_nonPV, lc_DL_snow_PV]),

        ("D + 0.75(S + 0.6W)", [lc_DL_LL_075_wind_045_snow_075_nonPV, lc_DL_LL_075_wind_045_snow_075_PV]),

        ("0.6D + 0.6W (Up)", [lc_DL_06_wind_06_nonPV, lc_DL_06_wind_06_PV]),

        ("D + 0.6W (Down)", [lc_DL_wind_06_nonPV, lc_DL_wind_06_PV])

    ]


    first_support = support_node_ids[0]


    for load_combination, load_cases in load_combinations:

        for lc in load_cases:

            ss.apply_load_case(lc)


        ss.solve()

        max_moment_positive = 0

        max_moment_negative = 0

        max_shear = 0

        max_axial = 0

        max_displacement = 0


        # Debugging: print structure of results

        results = ss.get_element_results(element_id=0, verbose=True)

        # print(f"Debugging: results: {results}")

        for result in results:


            tmp_Mmax = result["Mmax"]

            if tmp_Mmax > max_moment_positive:

                max_moment_positive = tmp_Mmax

            tmp_Mmin = result["Mmin"]

            if tmp_Mmin < max_moment_negative:

                max_moment_negative = tmp_Mmin


            tmp_N = np.max(np.abs(result["N"]))

            if tmp_N > max_axial:

                max_axial = tmp_N


            tmp_w = (np.max(np.abs(result["w"])) / np.cos(pitch))

            if tmp_w > max_displacement:

                max_displacement = tmp_w


        # Shear at the start of each element (V+), with 0 at the free end so it lines up
        # with the node list; V- at each node is V+ minus that node's vertical reaction.
        positive_shear_array = [el.shear_force[0] for el in ss.element_map.values()]

        positive_shear_array.append(0)

        rxn_array = [node["Fy"] / np.cos(pitch) for node in ss.get_node_results_system(node_id=0)]

        negative_shear_array = [v - r for v, r in zip(positive_shear_array, rxn_array)]

        total_shear = positive_shear_array + negative_shear_array

        max_shear = max(map(abs, total_shear))


        displacement_array = ss.get_node_displacements()

        for node in displacement_array:

            tmp_w = abs(node["uy"]) / np.cos(pitch)

            if tmp_w > max_displacement:

                max_displacement = tmp_w


        # Overhang = elements and nodes ahead of the first support.
        max_overhang_displacement = 0

        for oHang_element in range(1, first_support):

            ohang_result = ss.get_element_results(element_id=oHang_element, verbose=True)

            tmp_ohang_max = np.max(np.abs(ohang_result["w"])) / np.cos(pitch)

            if tmp_ohang_max > max_overhang_displacement:

                max_overhang_displacement = tmp_ohang_max

        for node in displacement_array:

            if node["id"] < first_support:

                tmp_ohang_max = abs(node["uy"]) / np.cos(pitch)

                if tmp_ohang_max > max_overhang_displacement:

                    max_overhang_displacement = tmp_ohang_max


        max_moment_positive = -np.ceil(max_moment_positive * 0.737562149)

        max_moment_negative = -np.ceil(max_moment_negative * 0.737562149)

        max_shear = np.ceil(max_shear * 0.22480894244319)

        max_axial = np.ceil(max_axial * 0.22480894244319)

        max_displacement = max_displacement * 39.3700787

        max_overhang_displacement = max_overhang_displacement * 39.3700787


        final_result["load_cases"][load_combination] = {

            "Max Moment (+)": max_moment_negative,

            "Max Moment (-)": max_moment_positive,

            "Max Shear (lb)": max_shear,

            "Max Axial Compression (lb)": max_axial,

            "Max Displacement (in)": max_displacement,

            "Max Overhang Displacement (in)": max_overhang_displacement

        }


    final_result["IEBC Load Check"] = {

        "Pre-PV D": IEBC_nonPV_DL,

        "Pre-PV D + L": IEBC_nonPV_DL_LL,

        "Pre-PV D + S": IEBC_nonPV_DL_S,

        "Pre-PV D + 0.75Lr + 0.75S": IEBC_nonPV_DL_075LL_075S,

        "Post-PV D": IEBC_PV_DL,

        "Post-PV D + S": IEBC_PV_DL_S

    }


    # Capacity calculation and DCR computation


    # Ensure 'load_cases' key exists in final_result and print debug information

    print (spanscap)

    capacity = calculate_capacity(spanscap, member_spacing,  framing_depth,framing_breadth, deg_pitch, overhang,

                                  modulus_E, modulus_E_minimum, bending_stress_Fb, shear_stress_Fv,

                                  specific_gravity_G, CF_B, CF_C, Cr, CD_D, CD_L, CD_S, CD_W,

                                  capacity_I_in4=cap_I_in4, capacity_S_in3=cap_S_in3, is_tji=is_tji_member)


    # Ensure 'load_cases' key exists in final_result and print debug information

    print(f"Debugging: Full final_result structure: {final_result}")


    if 'load_cases' in final_result:

        print("Debugging: 'load_cases' found in final_result")


        # Calculate DCR for D load case

        if 'D' in final_result['load_cases']:

            print("Debugging: 'D' load case found in 'load_cases'")

            D_load_case = final_result['load_cases']['D']


            # Extracting values for DCR calculation

            max_moment_neg = abs(D_load_case.get('Max Moment (-)', 0))

            max_moment_pos = abs(D_load_case.get('Max Moment (+)', 0))

            max_shear = abs(D_load_case.get('Max Shear (lb)', 0))


            # Calculating DCR values

            DCR_M_neg = max_moment_neg / capacity['M_allowable_D']

            DCR_M_pos = max_moment_pos / capacity['M_allowable_L']

            DCR_Shear = max_shear / capacity['V_allowable_D']


            # Storing DCR results

            final_result['DCR_D'] = {

                'Moment (-)': DCR_M_neg,

                'Moment (+)': DCR_M_pos,

                'Shear': DCR_Shear

            }


            final_result['Max_DCR_D'] = max(DCR_M_neg, DCR_M_pos, DCR_Shear)

            final_result['load_cases']['D']['Fb_prime_pos'] = capacity['Fb_prime_pos_D']

            final_result['load_cases']['D']['Fb_prime_neg'] = capacity['Fb_prime_neg_D']

            final_result['load_cases']['D']['V_allowable'] = capacity['V_allowable_D']

        else:

            print("Debugging: 'D' load case NOT found in 'load_cases'")

            final_result['DCR_D'] = 'Load case D not found within load_cases'


        # Calculate DCR for D + Lr load case

        if 'D + Lr' in final_result['load_cases']:

            print("Debugging: 'D + Lr' load case found in 'load_cases'")

            DLr_load_case = final_result['load_cases']['D + Lr']


            # Extracting values for DCR calculation

            max_moment_neg = abs(DLr_load_case.get('Max Moment (-)', 0))

            max_moment_pos = abs(DLr_load_case.get('Max Moment (+)', 0))

            max_shear = abs(DLr_load_case.get('Max Shear (lb)', 0))


            # Calculating DCR values

            print(max_moment_neg)

            print(capacity['M_allowable_Lr_neg'])

            DCR_M_neg = max_moment_neg / capacity['M_allowable_Lr_neg']

            DCR_M_pos = max_moment_pos / capacity['M_allowable_Lr_pos']

            DCR_Shear = max_shear / capacity['V_allowable_Lr']


            # Storing DCR results

            final_result['DCR_D_Lr'] = {

                'Moment (-)': DCR_M_neg,

                'Moment (+)': DCR_M_pos,

                'Shear': DCR_Shear

            }


            final_result['Max_DCR_D_Lr'] = max(DCR_M_neg, DCR_M_pos, DCR_Shear)

            final_result['load_cases']['D + Lr']['Fb_prime_pos'] = capacity['Fb_prime_pos_Lr']

            final_result['load_cases']['D + Lr']['Fb_prime_neg'] = capacity['Fb_prime_neg_Lr']

            final_result['load_cases']['D + Lr']['V_allowable'] = capacity['V_allowable_Lr']

        else:

            print("Debugging: 'D + Lr' load case NOT found in 'load_cases'")

            final_result['DCR_D_Lr'] = 'Load case D + Lr not found within load_cases'


        # Calculate DCR for D + S load case

        if 'D + S' in final_result['load_cases']:

            print("Debugging: 'D + S' load case found in 'load_cases'")

            DS_load_case = final_result['load_cases']['D + S']


            # Extracting values for DCR calculation

            max_moment_neg = abs(DS_load_case.get('Max Moment (-)', 0))

            max_moment_pos = abs(DS_load_case.get('Max Moment (+)', 0))

            max_shear = abs(DS_load_case.get('Max Shear (lb)', 0))


            # Calculating DCR values

            DCR_M_neg = max_moment_neg / capacity['M_allowable_S_neg']

            DCR_M_pos = max_moment_pos / capacity['M_allowable_S_pos']

            DCR_Shear = max_shear / capacity['V_allowable_S']


            # Storing DCR results

            final_result['DCR_D_S'] = {

                'Moment (-)': DCR_M_neg,

                'Moment (+)': DCR_M_pos,

                'Shear': DCR_Shear

            }


            final_result['Max_DCR_D_S'] = max(DCR_M_neg, DCR_M_pos, DCR_Shear)

            final_result['load_cases']['D + S']['Fb_prime_pos'] = capacity['Fb_prime_pos_S']

            final_result['load_cases']['D + S']['Fb_prime_neg'] = capacity['Fb_prime_neg_S']

            final_result['load_cases']['D + S']['V_allowable'] = capacity['V_allowable_S']

        else:

            print("Debugging: 'D + S' load case NOT found in 'load_cases'")

            final_result['DCR_D_S'] = 'Load case D + S not found within load_cases'


        # Calculate DCR for D + LR + W load case

        if 'D + 0.75(Lr + 0.6W)' in final_result['load_cases']:

            print("Debugging: 'D + 0.75(Lr + 0.6W)' load case found in 'load_cases'")

            DLRW_load_case = final_result['load_cases']['D + 0.75(Lr + 0.6W)']


            # Extracting values for DCR calculation

            max_moment_neg = abs(DLRW_load_case.get('Max Moment (-)', 0))

            max_moment_pos = abs(DLRW_load_case.get('Max Moment (+)', 0))

            max_shear = abs(DLRW_load_case.get('Max Shear (lb)', 0))


            # Calculating DCR values

            DCR_M_neg = max_moment_neg / capacity['M_allowable_W_neg']

            DCR_M_pos = max_moment_pos / capacity['M_allowable_W_pos']

            DCR_Shear = max_shear / capacity['V_allowable_W']


            # Storing DCR results

            final_result['DCR_D_LR_W'] = {

                'Moment (-)': DCR_M_neg,

                'Moment (+)': DCR_M_pos,

                'Shear': DCR_Shear

            }


            final_result['Max_DCR_D_LR_W'] = max(DCR_M_neg, DCR_M_pos, DCR_Shear)

            final_result['load_cases']['D + 0.75(Lr + 0.6W)']['Fb_prime_pos'] = capacity['Fb_prime_pos_W']

            final_result['load_cases']['D + 0.75(Lr + 0.6W)']['Fb_prime_neg'] = capacity['Fb_prime_neg_W']

            final_result['load_cases']['D + 0.75(Lr + 0.6W)']['V_allowable'] = capacity['V_allowable_W']

        else:

            print("Debugging: 'D + LR + W' load case NOT found in 'load_cases'")

            final_result['DCR_D_LR_W'] = 'Load case D + LR + W not found within load_cases'


        # Calculate DCR for D + S + W load case

        if 'D + 0.75(S + 0.6W)' in final_result['load_cases']:

            print("Debugging: 'D + S + W' load case found in 'load_cases'")

            DSW_load_case = final_result['load_cases']['D + 0.75(S + 0.6W)']


            # Extracting values for DCR calculation

            max_moment_neg = abs(DSW_load_case.get('Max Moment (-)', 0))

            max_moment_pos = abs(DSW_load_case.get('Max Moment (+)', 0))

            max_shear = abs(DSW_load_case.get('Max Shear (lb)', 0))


            # Calculating DCR values

            DCR_M_neg = max_moment_neg / capacity['M_allowable_W_neg']

            DCR_M_pos = max_moment_pos / capacity['M_allowable_W_pos']

            DCR_Shear = max_shear / capacity['V_allowable_W']


            # Storing DCR results

            final_result['DCR_D_S_W'] = {

                'Moment (-)': DCR_M_neg,

                'Moment (+)': DCR_M_pos,

                'Shear': DCR_Shear

            }


            final_result['Max_DCR_D_S_W'] = max(DCR_M_neg, DCR_M_pos, DCR_Shear)

            final_result['load_cases']['D + 0.75(S + 0.6W)']['Fb_prime_pos'] = capacity['Fb_prime_pos_W']

            final_result['load_cases']['D + 0.75(S + 0.6W)']['Fb_prime_neg'] = capacity['Fb_prime_neg_W']

            final_result['load_cases']['D + 0.75(S + 0.6W)']['V_allowable'] = capacity['V_allowable_W']

        else:

            print("Debugging: 'D + S + W' load case NOT found in 'load_cases'")

            final_result['DCR_D_S_W'] = 'Load case D + S + W not found within load_cases'


        # Calculate DCR for 0.6D + 0.6W (Up) load case

        if '0.6D + 0.6W (Up)' in final_result['load_cases']:

            print("Debugging: '0.6D + 0.6W (Up)' load case found in 'load_cases'")

            D06WUp_load_case = final_result['load_cases']['0.6D + 0.6W (Up)']


            # Extracting values for DCR calculation

            max_moment_neg = abs(D06WUp_load_case.get('Max Moment (-)', 0))

            max_moment_pos = abs(D06WUp_load_case.get('Max Moment (+)', 0))

            max_shear = abs(D06WUp_load_case.get('Max Shear (lb)', 0))


            # Calculating DCR values

            DCR_M_neg = max_moment_neg / capacity['M_allowable_W_neg']

            DCR_M_pos = max_moment_pos / capacity['M_allowable_W_pos']

            DCR_Shear = max_shear / capacity['V_allowable_W']


            # Storing DCR results

            final_result['DCR_0.6D_0.6W_Up'] = {

                'Moment (-)': DCR_M_neg,

                'Moment (+)': DCR_M_pos,

                'Shear': DCR_Shear

            }


            final_result['Max_DCR_0.6D_0.6W_Up'] = max(DCR_M_neg, DCR_M_pos, DCR_Shear)

            final_result['load_cases']['0.6D + 0.6W (Up)']['Fb_prime_pos'] = capacity['Fb_prime_pos_W']

            final_result['load_cases']['0.6D + 0.6W (Up)']['Fb_prime_neg'] = capacity['Fb_prime_neg_W']

            final_result['load_cases']['0.6D + 0.6W (Up)']['V_allowable'] = capacity['V_allowable_W']

        else:

            print("Debugging: '0.6D + 0.6W (Up)' load case NOT found in 'load_cases'")

            final_result['DCR_0.6D_0.6W_Up'] = 'Load case 0.6D + 0.6W (Up) not found within load_cases'


        # Calculate DCR for D + 0.6W (Down) load case

        if 'D + 0.6W (Down)' in final_result['load_cases']:

            print("Debugging: 'D + 0.6W (Down)' load case found in 'load_cases'")

            DWDown_load_case = final_result['load_cases']['D + 0.6W (Down)']


            # Extracting values for DCR calculation

            max_moment_neg = abs(DWDown_load_case.get('Max Moment (-)', 0))

            max_moment_pos = abs(DWDown_load_case.get('Max Moment (+)', 0))

            max_shear = abs(DWDown_load_case.get('Max Shear (lb)', 0))


            # Calculating DCR values

            DCR_M_neg = max_moment_neg / capacity['M_allowable_W_neg']

            DCR_M_pos = max_moment_pos / capacity['M_allowable_W_pos']

            DCR_Shear = max_shear / capacity['V_allowable_W']


            # Storing DCR results

            final_result['DCR_D_0.6W_Down'] = {

                'Moment (-)': DCR_M_neg,

                'Moment (+)': DCR_M_pos,

                'Shear': DCR_Shear

            }


            final_result['Max_DCR_D_0.6W_Down'] = max(DCR_M_neg, DCR_M_pos, DCR_Shear)

            final_result['load_cases']['D + 0.6W (Down)']['Fb_prime_pos'] = capacity['Fb_prime_pos_W']

            final_result['load_cases']['D + 0.6W (Down)']['Fb_prime_neg'] = capacity['Fb_prime_neg_W']

            final_result['load_cases']['D + 0.6W (Down)']['V_allowable'] = capacity['V_allowable_W']

        else:

            print("Debugging: 'D + 0.6W (Down)' load case NOT found in 'load_cases'")

            final_result['DCR_D_0.6W_Down'] = 'Load case D + 0.6W (Down) not found within load_cases'

    else:

        print("Debugging: 'load_cases' NOT found in final_result")

        final_result['DCR'] = 'No load_cases key found in final_result'



    return final_result


@app.route('/', methods=['POST'])
def process_roofs():

    data = request.get_json()

    if not data:

        data = {}

    top_level = data

    roofs_in = data.get("roofs") or []

    accumulate_sliding_snow_pairs(roofs_in)

    outcome = []


    for roof_data in roofs_in:

        final_result = analyze_roof(roof_data, top_level)

        purlin_block = run_purlin_subanalysis(roof_data, top_level, analyze_roof)

        if purlin_block is not None:

            final_result["purlin_analysis"] = purlin_block

        outcome.append(final_result)


    return jsonify(outcome)


if __name__ == '__main__':

    app.run(debug=True)

