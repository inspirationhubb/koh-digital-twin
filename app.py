import streamlit as st

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="KOH Prediction Twin",
    layout="centered"
)

# ======================================================
# TITLE
# ======================================================

st.title("Physics-Based KOH Prediction Twin")

st.markdown("""
Predicts the total KOH quantity required
for one-shot addition during batch manufacturing.
""")

# ======================================================
# INPUTS
# ======================================================

st.sidebar.header("Operator Inputs")

batch_size = st.sidebar.number_input(
    "Batch Size (KL)",
    min_value=1.0,
    value=12.0
)

acid_value = st.sidebar.number_input(
    "Soya DFA Acid Value",
    min_value=0.0,
    value=25.0
)

koh_strength = st.sidebar.number_input(
    "Strength of KOH (%)",
    min_value=1.0,
    max_value=100.0,
    value=45.0
)

intermediate_ph = st.sidebar.number_input(
    "Intermediate pH",
    min_value=0.0,
    max_value=14.0,
    value=6.5
)

# ======================================================
# DFA CALCULATION
# ======================================================

# Fixed ratio:
# 60 kg DFA per KL

dfa_quantity = batch_size * 60

# ======================================================
# BASE PHYSICS EQUATION
# ======================================================

base_koh = (
    acid_value
    * dfa_quantity
    * 0.1
) / koh_strength

# ======================================================
# pH CORRECTION FACTOR
# ======================================================

if intermediate_ph < 5:
    correction_factor = 0.15

elif intermediate_ph < 6:
    correction_factor = 0.10

elif intermediate_ph < 7:
    correction_factor = 0.05

elif intermediate_ph < 8:
    correction_factor = 0.02

else:
    correction_factor = 0.00

# ======================================================
# FINAL KOH PREDICTION
# ======================================================

final_koh_prediction = (
    base_koh
    * (1 + correction_factor)
)

# ======================================================
# OUTPUT
# ======================================================

st.markdown("---")

st.subheader("Predicted Total KOH Requirement")

st.metric(
    "Recommended KOH Addition",
    f"{final_koh_prediction:.2f} kg"
)

st.markdown("---")

st.subheader("Calculation Basis")

st.write(f"DFA Quantity = {dfa_quantity:.2f} kg")

st.write(f"Base Physics KOH = {base_koh:.2f} kg")

st.write(
    f"Applied pH Correction = {correction_factor*100:.1f}%"
)

# ======================================================
# ENGINEERING NOTES
# ======================================================

st.markdown("---")

st.info("""
This calculator uses:

• Physics-based stoichiometric neutralization  
• Fixed DFA loading ratio  
• Intermediate pH correction logic  
• One-shot KOH recommendation philosophy  

Objective:
Reduce manufacturing cycle time by minimizing
trial-and-error incremental additions.
""")
