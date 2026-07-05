import streamlit as st
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from datetime import datetime
import plotly.io as pio

# =====================================================
# CONFIG
# =====================================================

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Bandwidth Management AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

pio.templates.default = "plotly_dark"

# =====================================================
# DARK ENTERPRISE THEME
# =====================================================

st.markdown("""
<style>

/* App Background */
.stApp {
    background-color: #0b1120;
    color: #f8fafc;
}

/* Main Container */
.block-container {
    max-width: 1600px;
    padding-top: 1rem;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #111827 0%,
        #0f172a 100%
    );
    border-right: 1px solid #1f2937;
}

[data-testid="stSidebar"] * {
    color: white;
}

/* Metrics */
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.25);
}

/* Buttons */
.stButton > button {
    width: 100%;
    height: 48px;
    border-radius: 12px;
    border: none;
    color: white;
    font-weight: 600;
    background: linear-gradient(
        135deg,
        #2563eb,
        #7c3aed
    );
}

.stButton > button:hover {
    transform: translateY(-2px);
}

/* Inputs */
.stTextInput input,
.stTextArea textarea,
.stDateInput input {
    background-color: #111827 !important;
    color: white !important;
}

/* File Upload */
[data-testid="stFileUploader"] {
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 10px;
    background: #111827;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    background: #111827;
    border-radius: 10px;
    margin-right: 8px;
}

.stTabs [aria-selected="true"] {
    background: #2563eb !important;
}

hr {
    border-color: #334155;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.markdown("""
# 📊 Bandwidth AI

### Workforce Intelligence Platform
""")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Volume Upload",
        "Performance Upload",
        "Model Training",
        "Predictions",
        "Performance Agent"
    ]
)

st.sidebar.divider()
st.sidebar.success("System Online")

# =====================================================
# DASHBOARD
# =====================================================

if page == "Dashboard":

    st.markdown("""
    <div style="
        padding:30px;
        border-radius:20px;
        background:linear-gradient(
            135deg,
            #2563eb,
            #7c3aed
        );
        margin-bottom:25px;
    ">
        <h1 style="color:white;">
            📊 Bandwidth Management AI
        </h1>
        <p style="
            color:white;
            font-size:18px;
        ">
            Forecasting • Workforce Planning • Performance Intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Volume Service",
            "🟢 Active"
        )

    with col2:
        st.metric(
            "Performance Service",
            "🟢 Active"
        )

    with col3:
        st.metric(
            "Prediction Engine",
            "⚡ Ready"
        )

    with col4:
        st.metric(
            "Training Status",
            "✅ Available"
        )

    st.divider()

    left, right = st.columns([2, 1])

    with left:
        st.info("""
### Platform Capabilities

- XGBoost Volume Forecasting
- Workforce Capacity Planning
- Future Order Predictions
- Employee Performance Analytics
- AI-Powered Workforce Insights
        """)

    with right:
        st.success("""
### System Health

✅ API Connected

✅ Database Online

✅ Model Available

✅ Agent Ready
        """)

# =====================================================
# VOLUME UPLOAD
# =====================================================

elif page == "Volume Upload":

    st.markdown("## 📈 Volume Data Upload")
    st.caption("Upload historical volume data for forecasting.")

    file = st.file_uploader(
        "Upload CSV File",
        type=["csv"]
    )

    if file:

        df = pd.read_csv(file)

        st.subheader("Data Preview")
        st.dataframe(
            df.head(),
            use_container_width=True
        )

        if st.button(
            "Upload Volume Data"
        ):

            files = {
                "file": (
                    file.name,
                    file.getvalue(),
                    "text/csv"
                )
            }

            with st.spinner(
                "Uploading volume data..."
            ):

                response = requests.post(
                    f"{API_URL}/volume/",
                    files=files
                )

            if response.ok:

                st.success(
                    "Volume data uploaded successfully."
                )

                st.json(
                    response.json()
                )

            else:
                st.error(
                    response.text
                )

# =====================================================
# PERFORMANCE UPLOAD
# =====================================================

elif page == "Performance Upload":

    st.markdown("## 👥 Performance Upload")
    st.caption(
        "Upload employee performance metrics."
    )

    file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx"]
    )

    if file:

        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        st.subheader("Data Preview")

        st.dataframe(
            df.head(),
            use_container_width=True
        )

        if st.button(
            "Upload Performance Data"
        ):

            files = {
                "file": (
                    file.name,
                    file.getvalue()
                )
            }

            with st.spinner(
                "Processing performance data..."
            ):

                response = requests.post(
                    f"{API_URL}/performance/",
                    files=files
                )

            if response.ok:

                st.success(
                    "Performance data uploaded."
                )

                st.json(
                    response.json()
                )

            else:
                st.error(
                    response.text
                )

# =====================================================
# MODEL TRAINING
# =====================================================

elif page == "Model Training":

    st.markdown("## 🤖 Model Training")
    st.caption(
        "Train the forecasting model using historical volume."
    )

    if st.button(
        "Train Model"
    ):

        with st.spinner(
            "Training XGBoost model..."
        ):

            response = requests.post(
                f"{API_URL}/train/"
            )

        if response.ok:

            result = response.json()

            st.success(
                "Training completed."
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "MAE",
                    round(
                        result.get(
                            "mae",
                            0
                        ),
                        2
                    )
                )

            with col2:
                st.metric(
                    "RMSE",
                    round(
                        result.get(
                            "rmse",
                            0
                        ),
                        2
                    )
                )

            with col3:
                st.metric(
                    "MAPE",
                    round(
                        result.get(
                            "mape",
                            0
                        ),
                        2
                    )
                )

            st.json(result)

        else:

            st.error(
                response.text
            )

# =====================================================
# PREDICTIONS
# =====================================================

elif page == "Predictions":

    st.markdown("## 🔮 Order Predictions")
    st.caption("Generate order forecasts using the trained model.")

    tab1, tab2 = st.tabs(
        [
            "Single Prediction",
            "Future Forecast"
        ]
    )

    # ==================================
    # SINGLE PREDICTION
    # ==================================

    with tab1:

        nyc_now = datetime.now(ZoneInfo("America/New_York"))

        st.info(
            f"Current NYC Time: {nyc_now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )

        timestamp = st.datetime_input(
            "New York Time (EST/EDT)",
            value=nyc_now.replace(tzinfo=None)
        )

        if st.button(
            "Predict Orders",
            key="predict_single"
            ):

            nyc_timestamp = timestamp.replace(
                tzinfo=ZoneInfo("America/New_York")
            )

            response = requests.get(
                f"{API_URL}/predict/",
                params={
                    "timestamp": nyc_timestamp.isoformat()
                }
            )

            if response.ok:

                result = response.json()

                predicted = result.get("predicted", 0)
                lower = result.get("lower_bound", 0)
                upper = result.get("upper_bound", 0)

                st.success("Prediction completed successfully")

                st.subheader("Forecasted Orders")
                st.caption(f"Expected Range: {lower} - {upper}")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Predicted", predicted)

                with col2:
                    st.metric("Lower Bound", lower)

                with col3:
                    st.metric("Upper Bound", upper)

            else:
                st.error(response.text)

    # ==================================
    # FUTURE FORECAST
    # ==================================

        
    with tab2:

        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown("### 7-Day Forecast")

        with col2:
            view_mode = st.radio(
                "View Mode",
                ["Day", "Week"],
                horizontal=True,
                label_visibility="collapsed"
            )

        if st.button(
            "Generate Forecast",
            key="predict_future"
        ):

            response = requests.get(
                f"{API_URL}/predict/future"
            )

            if response.ok:
                st.session_state["forecast"] = response.json()
            else:
                st.error(response.text)
        if "forecast" not in st.session_state:
            st.info("Generate a forecast to begin.")
            st.stop()

        df = pd.DataFrame(
                st.session_state["forecast"]
                )

        df["timestamp"] = pd.to_datetime(
                    df["timestamp"]
                )

        df["date"] = df["timestamp"].dt.date

                # ==========================
                # KPI CARDS
                # ==========================

        total_orders = int(df["predicted"].sum())
        avg_orders = round(df["predicted"].mean(), 1)

        peak_row = df.loc[
                    df["predicted"].idxmax()
                ]

        low_row = df.loc[
                    df["predicted"].idxmin()
                ]

        col1, col2, col3, col4 = st.columns(4)

        col1.markdown(
                    f"""
                    <div style="
                        background:#111827;
                        padding:20px;
                        border-radius:15px;
                   text-align:center;
                    ">
                    <h3>Total Orders</h3>
                    <h1>{total_orders:,}</h1>
                    </div>
                    """,
                    unsafe_allow_html=True
                )     

        col2.markdown(
                    f"""
                    <div style="
                        background:#111827;
                        padding:20px;
                        border-radius:15px;
                        text-align:center;
                    ">
                    <h3>Average</h3>
                    <h1>{avg_orders}</h1>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        col3.markdown(
                    f"""
                    <div style="
                        background:#111827;
                        padding:20px;
                        border-radius:15px;
                        text-align:center;
                    ">
                    <h3>Peak</h3>
                    <h1>{peak_row['predicted']}</h1>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        col4.markdown(
                    f"""
                    <div style="
                        background:#111827;
                        padding:20px;
                        border-radius:15px;
                        text-align:center;
                    ">
                    <h3>Lowest</h3>
                    <h1>{low_row['predicted']}</h1>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.divider()

                # ==========================
                # DAY VIEW
                # ==========================

        if view_mode == "Day":

            selected_day = st.selectbox(
                "Select Day",
                sorted(df["date"].unique())
            )

            day_df = df[df["date"] == selected_day]

            import plotly.graph_objects as go

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=day_df["timestamp"],
                y=day_df["predicted"],
                mode="lines+markers",
                name="Predicted"
            ))

            fig.add_trace(go.Scatter(
                x=day_df["timestamp"],
                y=day_df["upper_bound"],
                mode="lines",
                name="Upper Bound",
                line=dict(dash="dash")
            ))

            fig.add_trace(go.Scatter(
                x=day_df["timestamp"],
                y=day_df["lower_bound"],
                mode="lines",
                name="Lower Bound",
                line=dict(dash="dash")
            ))

            fig.update_layout(
                title=f"Forecast for {selected_day}",
                height=500,
                template="plotly_dark"
            )

            st.plotly_chart(fig, use_container_width=True)

        else:

            weekly = (
                df.groupby("date")
                .agg({
                    "predicted": "sum",
                    "upper_bound": "sum",
                    "lower_bound": "sum"
                })
                .reset_index()
            )

            import plotly.graph_objects as go

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=weekly["date"],
                y=weekly["predicted"],
                mode="lines+markers",
                name="Predicted Orders"
            ))

            fig.add_trace(go.Scatter(
                x=weekly["date"],
                y=weekly["upper_bound"],
                mode="lines+markers",
                name="Upper Bound",
                line=dict(dash="dash")
            ))

            fig.add_trace(go.Scatter(
                x=weekly["date"],
                y=weekly["lower_bound"],
                mode="lines+markers",
                name="Lower Bound",
                line=dict(dash="dash")
            ))

            fig.update_layout(
                title="Weekly Forecast Overview",
                height=600,
                template="plotly_dark"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Daily Forecast Breakdown")

            cols = st.columns(4)

            for i, row in weekly.iterrows():
                with cols[i % 4]:
                    st.metric(str(row["date"]), int(row["predicted"]))
