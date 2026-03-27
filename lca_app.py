import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Sustainability Analysis Tool", layout="wide")

# ---------------------------
# LOAD LOGO
# ---------------------------
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo = get_base64_image("logo.png")

# ---------------------------
# HEADER
# ---------------------------
st.markdown(
    f"""
    <div style="text-align: center;">
        <img src="data:image/png;base64,{logo}" width="90">
        <h1>Sustainability Analysis Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ---------------------------
# NAVIGATION (DROPDOWN)
# ---------------------------
st.markdown("### Select Analysis Type")
page = st.selectbox(
    "",
    ["Product Comparison (LCA)", "Vehicle Comparison (EV vs Petrol)"]
)

# =====================================================
# PRODUCT LCA SECTION
# =====================================================
if page == "Product Comparison (LCA)":

    st.header("Product Life Cycle Comparison")

    st.markdown("""
    This tool compares emissions across lifecycle stages:
    Material → Manufacturing → Transport → End of Life
    """)

    category = st.radio("Select category", ["Bottles", "Bags"])

    data = {
        "Bottles": {
            "Plastic Bottle (500ml, ~25g)": {"Material": 2.0, "Manufacturing": 1.5, "Transport": 0.5, "End of Life": 0.8},
            "Glass Bottle (500ml, ~350g)": {"Material": 3.0, "Manufacturing": 2.0, "Transport": 1.0, "End of Life": 1.2}
        },
        "Bags": {
            "Plastic Bag (~10g)": {"Material": 0.5, "Manufacturing": 0.3, "Transport": 0.1, "End of Life": 0.2},
            "Paper Bag (~50g)": {"Material": 0.8, "Manufacturing": 0.6, "Transport": 0.2, "End of Life": 0.3}
        }
    }

    p1, p2 = list(data[category].keys())

    col1, col2 = st.columns(2)
    with col1:
        q1 = st.slider(f"{p1} quantity", 0, 100, 1)
    with col2:
        q2 = st.slider(f"{p2} quantity", 0, 100, 1)

    def calc(product, qty):
        df = pd.DataFrame(list(data[category][product].items()), columns=["Stage", "CO2"])
        df["CO2"] *= qty
        order = ["Material", "Manufacturing", "Transport", "End of Life"]
        df["Stage"] = pd.Categorical(df["Stage"], categories=order, ordered=True)
        return df.sort_values("Stage")

    df1 = calc(p1, q1)
    df2 = calc(p2, q2)

    # ---------------------------
    # BAR CHART
    # ---------------------------
    st.subheader("Emission Breakdown")

    chart_df = pd.DataFrame({
        p1: df1.set_index("Stage")["CO2"],
        p2: df2.set_index("Stage")["CO2"]
    })

    st.bar_chart(chart_df)
    st.caption("X-axis: Lifecycle stages | Y-axis: CO2 emissions (kg)")

    # ---------------------------
    # PIE CHART (DARK MODE)
    # ---------------------------
    st.subheader("Lifecycle Contribution")

    def dark_pie(df):
        fig, ax = plt.subplots(facecolor='black')
        ax.set_facecolor('black')
        ax.pie(
            df["CO2"],
            labels=df["Stage"],
            autopct='%1.1f%%',
            textprops={'color': 'white'}
        )
        return fig

    if q1 > 0 and q2 > 0:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{p1}**")
            st.pyplot(dark_pie(df1))

        with col2:
            st.markdown(f"**{p2}**")
            st.pyplot(dark_pie(df2))

    elif q1 > 0:
        st.markdown(f"**{p1}**")
        st.pyplot(dark_pie(df1))

    elif q2 > 0:
        st.markdown(f"**{p2}**")
        st.pyplot(dark_pie(df2))

    # ---------------------------
    # TOTAL
    # ---------------------------
    t1 = df1["CO2"].sum()
    t2 = df2["CO2"].sum()

    st.subheader("Total Emissions")

    if q1 > 0:
        st.write(f"{p1}: {t1:.2f} kg CO2")

    if q2 > 0:
        st.write(f"{p2}: {t2:.2f} kg CO2")

    # ---------------------------
    # FINAL INSIGHT
    # ---------------------------
    st.subheader("Final Insight")

    if q1 == 0 and q2 == 0:
        st.info("No products selected.")

    elif q1 > 0 and q2 > 0:
        diff = abs(t1 - t2)
        if t1 < t2:
            st.success(f"Choosing {p1} reduces emissions by {diff:.2f} kg CO2.")
        else:
            st.success(f"Choosing {p2} reduces emissions by {diff:.2f} kg CO2.")

    elif q1 > 0:
        st.write(f"{p1} emits {t1:.2f} kg CO2.")

    elif q2 > 0:
        st.write(f"{p2} emits {t2:.2f} kg CO2.")

# =====================================================
# EV vs PETROL SECTION
# =====================================================
elif page == "Vehicle Comparison (EV vs Petrol)":

    st.header("EV vs Petrol Car Emissions")

    st.markdown("""
    Compare emissions from petrol and electric vehicles based on yearly driving distance.
    """)

    # INPUT
    km = st.slider("Distance per year (km)", 0, 30000, 10000)

    # CALCULATIONS
    petrol = km * 0.19
    ev = km * 0.10
    diff = petrol - ev

    # ---------------------------
    # 1. CHART
    # ---------------------------
    df = pd.DataFrame({
        "Vehicle": ["Petrol", "EV"],
        "CO2": [petrol, ev]
    })

    st.subheader("Emission Comparison")
    st.bar_chart(df.set_index("Vehicle"))

    # ---------------------------
    # 2. RESULTS
    # ---------------------------
    st.subheader("Results")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Petrol Car", f"{petrol:.2f} kg CO2/year")

    with col2:
        st.metric("Electric Vehicle", f"{ev:.2f} kg CO2/year")

    # ---------------------------
    # 3. INSIGHT
    # ---------------------------
    st.subheader("Insight")

    if diff > 0:
        st.success(f"Switching to EV reduces emissions by {diff:.2f} kg CO2/year")
    else:
        st.warning("Emission difference is minimal.")

    # ---------------------------
    # 4. FINAL INSIGHT
    # ---------------------------
    st.subheader("Final Insight")

    st.write(
        "Electric vehicles generally produce lower emissions over time, "
        "especially when powered by cleaner electricity sources."
    )

# ---------------------------
# FINAL LINE
# ---------------------------
st.markdown("---")
st.markdown(
    "<p style='text-align:center; font-weight:bold;'>"
    "Small changes in daily choices can lead to significant environmental impact over time."
    "</p>",
    unsafe_allow_html=True
)

# DISCLAIMER
st.caption("This model uses simplified emission factors and average values to estimate lifecycle emissions for representative products.")
st.caption("Developed by Abhay Borse")