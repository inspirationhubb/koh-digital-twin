
import streamlit as st
import math

st.set_page_config(
    page_title="KOH Digital Twin",
    layout="wide"
)

st.title("Physics-Based Incremental KOH Digital Twin")

st.markdown(
    """
    Real-time numerical neutralization calculator for predicting
    safe incremental caustic addition.
    """
)

st.sidebar.header("Operator Inputs")

acid_value = st.sidebar.number_input(
    "Soya DFA Acid Value",
    value=25.0
)

batch_mass = st.sidebar.number_input(
    "Batch Mass (kg)",
    value=10000.0
)

koh_strength = st.sidebar.number_input(
    "Strength of Caustic (%)",
    value=45.0
)

current_ph = st.sidebar.number_input(
    "Intermediate pH",
    value=6.5
)

target_ph = st.sidebar.number_input(
    "Target Final pH",
    value=9.0
)

temperature = st.sidebar.number_input(
    "Mixer Temperature (°C)",
    value=50.0
)

cumulative_koh = st.sidebar.number_input(
    "Current Total KOH Added (kg)",
    value=450.0
)

mixing_time = st.sidebar.number_input(
    "Mixing Time Before pH Check (min)",
    value=4.0
)

st.sidebar.markdown("---")
st.sidebar.subheader("Model Parameters")

alpha = st.sidebar.number_input(
    "Alpha Gain Constant",
    value=0.08
)

beta = st.sidebar.number_input(
    "Beta Damping Constant",
    value=0.35
)

gamma = st.sidebar.number_input(
    "Gamma Safety Factor",
    value=0.45
)

temp_coeff = st.sidebar.number_input(
    "Temperature Coefficient",
    value=0.02
)

# =====================================================
# PHYSICS-BASED DIGITAL TWIN SOLVER
# =====================================================

koh_theoretical = (
    acid_value * batch_mass * 56.1
) / (1000 * koh_strength)

koh_gap = max(
    koh_theoretical - cumulative_koh,
    0
)

ph_mid = 8

# Temperature correction

temp_correction = (
    1 + temp_coeff * (temperature - 50)
)

# Mixing stabilization correction

mixing_correction = min(
    max(mixing_time / 4, 0.8),
    1.2
)

# Nonlinear pH gain model

gain_ph = (
    alpha
    * math.exp(
        -beta * ((current_ph - ph_mid) ** 2)
    )
    * temp_correction
    * mixing_correction
)

incremental_koh = (
    gamma
    * ((target_ph - current_ph)
    / max(gain_ph, 0.0001))
    * (koh_gap / max(koh_theoretical, 1))
)

# Endpoint damping logic

damping_factor = 1

if current_ph >= 9:
    damping_factor = 0.1
elif current_ph >= 8:
    damping_factor = 0.2
elif current_ph >= 7:
    damping_factor = 0.4
elif current_ph >= 6:
    damping_factor = 0.7

incremental_koh *= damping_factor

incremental_koh = max(incremental_koh, 0)

predicted_next_ph = (
    current_ph + gain_ph * incremental_koh
)

neutralization_remaining = (
    koh_gap / max(koh_theoretical, 1)
) * 100

# Overshoot risk logic

overhoot_risk = "LOW"

if predicted_next_ph > target_ph + 1:
    overhoot_risk = "HIGH"
elif predicted_next_ph > target_ph:
    overhoot_risk = "MEDIUM"

# =====================================================
# OUTPUTS
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Recommended Incremental KOH",
        f"{incremental_koh:.2f} kg"
    )

with col2:
    st.metric(
        "Predicted Next pH",
        f"{predicted_next_ph:.2f}"
    )

with col3:
    st.metric(
        "Overshoot Risk",
        overhoot_risk
    )

st.markdown("---")

col4, col5, col6 = st.columns(3)

with col4:
    st.metric(
        "Theoretical KOH",
        f"{koh_theoretical:.2f} kg"
    )

with col5:
    st.metric(
        "Remaining Neutralization",
        f"{neutralization_remaining:.2f}%"
    )

with col6:
    st.metric(
        "pH Gain",
        f"{gain_ph:.4f}"
    )

st.markdown("---")

st.subheader("Embedded Physics Logic")

st.markdown(
    """
- Stoichiometric neutralization engine
- Temperature-corrected pH sensitivity
- Nonlinear endpoint damping
- Mixing stabilization correction
- Overshoot prevention logic
- Real-time incremental KOH recommendation
    """
)

st.subheader("Engineering Notes")

st.info(
    """
This is a semi-first-principles digital twin.

The solver combines:
- stoichiometric neutralization,
- nonlinear pH behavior,
- temperature correction,
- and endpoint damping.

This is NOT a black-box ML model.
    """
