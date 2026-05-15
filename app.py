import streamlit as st
import math

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="KOH Digital Twin",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("Physics-Based Incremental KOH Digital Twin")

st.markdown("""
Semi-first-principles neutralization twin for predicting
safe incremental KOH addition during herbal batch processing.
""")

# =========================================================
# SIDEBAR INPUTS
# =========================================================

st.sidebar.header("Operator Inputs")

batch_size = st.sidebar.number_input(
    "Batch Size (KL)",
    min_value=1.0,
    value=12.0
)

acid_value = st.sidebar.number_input(
    "Soya DFA Acid Value (mg KOH/g)",
    min_value=0.0,
    value=25.0
)

current_ph = st.sidebar.number_input(
    "Intermediate pH",
    min_value=0.0,
    max_value=14.0,
    value=6.5
)

target_ph = st.sidebar.number_input(
    "Target Final pH",
    min_value=8.0,
    max_value=11.0,
    value=9.0
)

koh_strength = st.sidebar.number_input(
    "Strength of Caustic (%)",
    min_value=1.0,
    max_value=100.0,
    value=45.0
)

temperature = st.sidebar.number_input(
    "Mixer Temperature at FCA Check (°C)",
    value=50.0
)

current_total_koh = st.sidebar.number_input(
    "Current Total KOH Added (kg)",
    min_value=0.0,
    value=350.0
)

mixing_time = st.sidebar.number_input(
    "Mixing Time Before pH Check (min)",
    min_value=1.0,
    value=4.0
)

# =========================================================
# INTERNAL PROCESS CONSTANTS
# =========================================================

# DFA loading ratio:
# 60 kg DFA per KL batch

DFA_RATIO = 60

# Physics tuning parameters

ALPHA = 0.025
BETA = 0.45
TEMP_COEFF = 0.015
SAFETY_FACTOR = 0.35

# =========================================================
# STEP 1 — DFA INVENTORY
# =========================================================

dfa_quantity = batch_size * DFA_RATIO

# =========================================================
# STEP 2 — THEORETICAL KOH REQUIREMENT
# =========================================================

koh_theoretical = (
    acid_value
    * dfa_quantity
    * 56.1
) / (
    1000 * koh_strength
)

# =========================================================
# STEP 3 — REMAINING NEUTRALIZATION GAP
# =========================================================

koh_gap = max(
    koh_theoretical - current_total_koh,
    0
)

# =========================================================
# STEP 4 — TEMPERATURE CORRECTION
# =========================================================

temp_correction = (
    1
    + TEMP_COEFF * (temperature - 50)
)

# =========================================================
# STEP 5 — MIXING CORRECTION
# =========================================================

mixing_correction = min(
    max(mixing_time / 4, 0.85),
    1.15
)

# =========================================================
# STEP 6 — NONLINEAR pH GAIN MODEL
# =========================================================

ph_mid = 8

gain_ph = (
    ALPHA
    * math.exp(
        -BETA * ((current_ph - ph_mid) ** 2)
    )
    * temp_correction
    * mixing_correction
)

# =========================================================
# STEP 7 — INCREMENTAL KOH SOLVER
# =========================================================

ph_gap = max(
    target_ph - current_ph,
    0
)

incremental_koh = (
    SAFETY_FACTOR
    * ph_gap
    * koh_gap
) / max(gain_ph * 100, 0.01)

# =========================================================
# STEP 8 — ENDPOINT DAMPING
# =========================================================

if current_ph >= 9:
    damping = 0.10
elif current_ph >= 8:
    damping = 0.20
elif current_ph >= 7:
    damping = 0.45
elif current_ph >= 6:
    damping = 0.70
else:
    damping = 1.00

incremental_koh *= damping

# =========================================================
# STEP 9 — MAX SAFE LIMITER
# =========================================================

max_increment = koh_gap * 0.35

incremental_koh = min(
    incremental_koh,
    max_increment
)

incremental_koh = max(
    incremental_koh,
    0
)

# =========================================================
# STEP 10 — PREDICTED NEXT pH
# =========================================================

predicted_next_ph = (
    current_ph
    + gain_ph * incremental_koh
)

predicted_next_ph = min(
    predicted_next_ph,
    11
)

# =========================================================
# STEP 11 — OVERSHOOT RISK
# =========================================================

if predicted_next_ph > target_ph + 0.5:
    overshoot_risk = "HIGH"
elif predicted_next_ph > target_ph:
    overshoot_risk = "MEDIUM"
else:
    overshoot_risk = "LOW"

# =========================================================
# STEP 12 — REMAINING NEUTRALIZATION
# =========================================================

neutralization_remaining = (
    koh_gap
    / max(koh_theoretical, 1)
) * 100

# =========================================================
# OUTPUTS
# =========================================================

st.markdown("---")

st.subheader("Digital Twin Recommendations")

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
        overshoot_risk
    )

st.markdown("---")

col4, col5, col6 = st.columns(3)

with col4:
    st.metric(
        "DFA Quantity",
        f"{dfa_quantity:.2f} kg"
    )

with col5:
    st.metric(
        "Theoretical KOH Requirement",
        f"{koh_theoretical:.2f} kg"
    )

with col6:
    st.metric(
        "Remaining Neutralization",
        f"{neutralization_remaining:.1f}%"
    )

st.markdown("---")

col7, col8 = st.columns(2)

with col7:
    st.metric(
        "pH Gain Sensitivity",
        f"{gain_ph:.4f}"
    )

with col8:
    st.metric(
        "Remaining KOH Gap",
        f"{koh_gap:.2f} kg"
    )

# =========================================================
# ENGINEERING LOGIC
# =========================================================

st.markdown("---")

st.subheader("Embedded Physics Logic")

st.markdown("""
- Stoichiometric neutralization engine
- DFA inventory-based acid loading
- Temperature-corrected pH sensitivity
- Mixing stabilization correction
- Nonlinear endpoint damping
- Safe incremental dosing logic
- Overshoot prevention constraints
""")

# =========================================================
# ENGINEERING NOTES
# =========================================================

st.markdown("---")

st.subheader("Engineering Notes")

st.info("""
This digital twin is based on:

• Acid-base neutralization stoichiometry  
• Semi-first-principles reactor behavior  
• Nonlinear pH response modeling  
• Temperature sensitivity correction  
• Stepwise dosing stabilization logic  

This is NOT a machine-learning black-box model.

The model should be calibrated further using
actual incremental pH-response trajectories
from plant batches for APC-grade accuracy.
""")
