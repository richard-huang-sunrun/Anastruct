from flask import Flask, request, jsonify

import anastruct

from anastruct import SystemElements, LoadCase

import numpy as np

import math


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


def calculate_capacity(spans, spacing, depth, breadth, pitch, overhang, E, Emin, Fb, Fv, G, CF_B, Cr, CD_D, CD_L, CD_S, CD_W):

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

    CF_Fb = CF_B

    CF_Ft = CF_B

    CF_Fc = 1.15

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


    if depth / breadth <= 5:

        CL_neg_D = 1

    else:

        CL_neg_D = (1 + (FbE / Fb_star_D)) / 1.9 - (((1 + (FbE / Fb_star_D)) / 1.9) ** 2 - (FbE / Fb_star_D / 0.95)) ** 0.5

    Fb_prime_neg_D = Fb * CD_D * CL_neg_D * CF_Fb * Cr

    print(f"Fb_prime_pos_D: {Fb_prime_pos_D}, Fb_prime_neg_D: {Fb_prime_neg_D}")


    # Calculate Fb'(+) and Fb*(-) for D + Lr

    Fb_prime_pos_Lr = Fb * CF_Fb * Cr * CD_L

    Fb_star_Lr = Fb * CF_Fb * Cr * CD_L


    if depth / breadth <= 5:

        CL_neg_Lr = 1

    else:

        CL_neg_Lr = (1 + (FbE / Fb_star_Lr)) / 1.9 - (((1 + (FbE / Fb_star_Lr)) / 1.9) ** 2 - (FbE / Fb_star_Lr / 0.95)) ** 0.5

    Fb_prime_neg_Lr = Fb * CL_neg_Lr * CF_Fb * Cr * CD_L

    print(f"Fb_prime_pos_Lr: {Fb_prime_pos_Lr}, Fb_prime_neg_Lr: {Fb_prime_neg_Lr}")


    # Calculate Fb'(+) and Fb*(-) for D + S

    Fb_prime_pos_S = Fb * CF_Fb * Cr * CD_S

    Fb_star_S = Fb * CF_Fb * Cr * CD_S


    if depth / breadth <= 5:

        CL_neg_S = 1

    else:

        CL_neg_S = (1 + (FbE / Fb_star_S)) / 1.9 - (((1 + (FbE / Fb_star_S)) / 1.9) ** 2 - (FbE / Fb_star_S / 0.95)) ** 0.5

    Fb_prime_neg_S = Fb * CL_neg_S * CF_Fb * Cr * CD_S

    print(f"Fb_prime_pos_S: {Fb_prime_pos_S}, Fb_prime_neg_S: {Fb_prime_neg_S}")


    # Calculate Fb'(+) and Fb*(-) for wind load cases

    Fb_prime_pos_W = Fb * CF_Fb * Cr * CD_W

    Fb_star_W = Fb * CF_Fb * Cr * CD_W


    if depth / breadth <= 5:

        CL_neg_W = 1

    else:

        CL_neg_W = (1 + (FbE / Fb_star_W)) / 1.9 - (((1 + (FbE / Fb_star_W)) / 1.9) ** 2 - (FbE / Fb_star_W / 0.95)) ** 0.5

    Fb_prime_neg_W = Fb * CL_neg_W * CF_Fb * Cr * CD_W

    print(f"Fb_prime_pos_W: {Fb_prime_pos_W}, Fb_prime_neg_W: {Fb_prime_neg_W}")


    # Convert lu from feet to inches

    lu_inches = lu * 12

    print(f"lu_inches: {lu_inches}")


    # Calculate the section modulus (S) and moment of inertia (I)

    S = (breadth * (depth ** 2)) / 6

    I = (breadth * (depth ** 3)) / 12

    A = breadth * depth  # Cross-sectional area

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

    V_allowable_D = (2 / 3) * breadth * Fv_prime_D * depth

    V_allowable_Lr = (2 / 3) * breadth * Fv_prime_Lr * depth

    V_allowable_S = (2 / 3) * breadth * Fv_prime_S * depth

    V_allowable_W = (2 / 3) * breadth * Fv_prime_W * depth

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




@app.route('/', methods=['POST'])

def process_roofs():

    data = request.get_json()

    outcome = []


    for roof_data in data['roofs']:

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


        eave_to_ridge = float(roof_data.get('etor', 10))

        mod_locations = roof_data.get('mod_locations', [0.001, 10.001])

        spans= roof_data.get('span_locations', [2, 8, 0, 0])

        spanscap = spans.copy()

        deg_pitch = float(roof_data.get('pitch', 18))

        wind_pressure_down = float(roof_data.get('wind_pressure_down', 16))

        wind_pressure_up = float(roof_data.get('wind_pressure_up', -16))

        wind_pressures = [wind_pressure_down, wind_pressure_up]

        snow_pre_pv = float(roof_data.get('snow_pre_pv', 0))

        snow_post_pv = float(roof_data.get('snow_post_pv', 0))

        snow_string = [snow_post_pv, snow_pre_pv]

        snow = snow_string

        overhang = float(roof_data.get('overhang', 0))

        dead_load_roofing = float(roof_data.get('dead_load_roofing', 10))

        dead_load_pv = float(roof_data.get('dead_load_pv', 3))

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

        CF_C = float(roof_data.get('CF_C', 1.1))  # Default value of 1.1 if not provided


        if member_spacing <= 24:

            Cr = 1.15

        else:

            Cr = 1.0


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

        for i in range(len(mod_locations)):

            mod_locations[i] = float(mod_locations[i]) * 0.3048

        mod_locations.sort()

        for i in range(len(spans)):

            spans[i] = float(spans[i]) * 0.3048

        eave_to_ridge *= 0.3048

        member_spacing = (member_spacing / 12) * 0.3048


        for i in range(2):

            snow[i] = float(snow[i])


        pitch = np.deg2rad(deg_pitch)

        wind_load = float(wind_pressures[0])

        wind_up = float(wind_pressures[1])*0.6

        print(wind_load)

        print(wind_up)


        support_locations = []

        for i in range(len(spans)):

            if i == 0:

                support_locations.append(spans[i])

            else:

                support_locations.append(spans[i] + support_locations[i - 1])


        rafter_array = support_locations + mod_locations

        rafter_array.sort()


        final_node_count = len(rafter_array) + (len(rafter_array) - 1)

        for i in range(len(rafter_array) - 1):

            rafter_array.insert(i + (i + 1), (rafter_array[i + i] + rafter_array[i + i + 1]) / 2)


        tmp_member_coordinates = [[i * np.cos(pitch), i * np.sin(pitch)] for i in rafter_array]

        support_coordinates = [[i * np.cos(pitch), i * np.sin(pitch)] for i in support_locations]

        mod_coordinates = [[i * np.cos(pitch), i * np.sin(pitch)] for i in mod_locations]


        tmp_member_coordinates.insert(0, [0, 0])


        member_coordinates = []

        for i in tmp_member_coordinates:

            if i not in member_coordinates:

                member_coordinates.append(i)


        E = float(list_EAI[0]) * 6894.7572931783

        A = float(list_EAI[1]) * 0.00064516

        I = float(list_EAI[2]) * 0.000000416231426


        ss = SystemElements(EA=E * A, EI=E * I)

        for i in range(len(member_coordinates) - 1):

            ss.add_element(location=[member_coordinates[i], member_coordinates[i + 1]])


        for i in support_coordinates:

            support_node_id = ss.find_node_id(i)

            ss.add_support_hinged(node_id=support_node_id)


        PV_start = []

        PV_stop = []

        ndx = 0

        for i in mod_coordinates:

            mod_node_id = ss.find_node_id(i)

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


        load_combinations = [

            ("D", [lc_DL_nonPV, lc_DL_PV]),

            ("D + Lr", [lc_DL_LL_nonPV, lc_DL_LL_PV]),

            ("D + 0.75(Lr + 0.6W)", [lc_DL_LL_075_wind_045_live_075_nonPV, lc_DL_LL_075_wind_045_live_075_PV]),

            ("D + S", [lc_DL_snow_nonPV, lc_DL_snow_PV]),

            ("D + 0.75(S + 0.6W)", [lc_DL_LL_075_wind_045_snow_075_nonPV, lc_DL_LL_075_wind_045_snow_075_PV]),

            ("0.6D + 0.6W (Up)", [lc_DL_06_wind_06_nonPV, lc_DL_06_wind_06_PV]),

            ("D + 0.6W (Down)", [lc_DL_wind_06_nonPV, lc_DL_wind_06_PV])

        ]


        support_node_ids = []


        for i in support_coordinates:

            support_node_id = ss.find_node_id(i)

            ss.add_support_hinged(node_id=support_node_id)

            support_node_ids.append(support_node_id)  # Track the support node IDs


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


            rxn_forces = []

            for node_id in support_node_ids:

                node_results = ss.get_node_results_system(node_id=node_id)


                if load_combination == "0.6D + 0.6W (Up)":

                    rxn_forces.append(node_results['Fy'] / np.cos(pitch))

                else:

                    rxn_forces.append(node_results['Fx'] / np.cos(pitch))


            shear_results = ss.get_element_result_range("shear")

            positive_shear_array = [data for data in shear_results]


            # rxn_array = []

            # print(data)

            # for data in rxn_forces:

            #     # Use the correct key to access the vertical force (Fy)

            #     rxn_array.append(data['Fy'] / np.cos(pitch))


            print(f"Length of positive_shear_array: {len(positive_shear_array)}")

            print(f"Length of rxn_forces: {len(rxn_forces)}")


            # Ensure the loop only runs for the minimum length of the two arrays

            min_length = min(len(positive_shear_array), len(rxn_forces))

            print(f"Using min_length: {min_length}")


            negative_shear_array = []

            for i in range(min_length):

                negative_shear_array.append(positive_shear_array[i] - rxn_forces[i])

            total_shear = positive_shear_array + negative_shear_array

            max_shear = max(map(abs, total_shear))



            max_moment_positive = -np.ceil(max_moment_positive * 0.737562149)

            max_moment_negative = -np.ceil(max_moment_negative * 0.737562149)

            max_shear = np.ceil(max_shear * 0.22480894244319)

            max_axial = np.ceil(max_axial * 0.22480894244319)

            max_displacement = max_displacement * 39.3700787


            final_result["load_cases"][load_combination] = {

                "Max Moment (+)": max_moment_negative,

                "Max Moment (-)": max_moment_positive,

                "Max Shear (lb)": max_shear,

                "Max Axial Compression (lb)": max_axial,

                "Max Displacement (in)": max_displacement

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

                                      specific_gravity_G,CF_B, Cr, CD_D, CD_L, CD_S, CD_W)


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


        outcome.append(final_result)


    return jsonify(outcome)


if __name__ == '__main__':

    app.run(debug=True)

