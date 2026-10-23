
import os
import time

import pandas as pd
import requests
import streamlit as st


# ------------------------------------
# CONFIGURATION
# ------------------------------------

API_URL = os.getenv(
    "AGENT_API_URL",
    "http://127.0.0.1:8000"
)

st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="📊",
    layout="wide"
)


# ------------------------------------
# HELPERS
# ------------------------------------

def create_chart_data(df):
    """
    Detect a suitable categorical + numerical
    column pair for an automatic bar chart.
    """

    if df.empty or len(df.columns) < 2:
        return None

    plot_df = df.copy()

    # Convert numeric-looking strings from API
    for col in plot_df.columns:
        converted = pd.to_numeric(
            plot_df[col], errors="coerce"
        )

        if converted.notna().all():
            plot_df[col] = converted

    numeric_cols = plot_df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_cols = [
        col for col in plot_df.columns
        if col not in numeric_cols
    ]

    if not numeric_cols or not categorical_cols:
        return None

    x_col = categorical_cols[0]

    # Prefer useful business measures
    preferred = [
        "rejection_rate",
        "total_order_amount",
        "average_order_value",
        "rejected_orders_count",
        "total_orders",
    ]

    y_col = next(
        (col for col in preferred if col in numeric_cols),
        numeric_cols[0]
    )

    if plot_df[x_col].duplicated().any():
        return None

    return plot_df, x_col, y_col


def format_dataframe(df):
    """Convert numeric-looking API values."""
    output = df.copy()

    for col in output.columns:
        if col.lower().endswith("_id"):
            continue

        converted = pd.to_numeric(
            output[col], errors="coerce"
        )

        if converted.notna().all() and not output.empty:
            output[col] = converted

    return output


# ------------------------------------
# SIDEBAR
# ------------------------------------

with st.sidebar:
    st.title("🤖 AI Analyst")

    st.caption("GenAI + Agentic AI Portfolio Project")

    st.divider()

    st.subheader("Technology Stack")

    st.write("• Google Gemini")
    st.write("• LangGraph")
    st.write("• Python + FastAPI")
    st.write("• PostgreSQL")
    st.write("• SQLGlot")
    st.write("• Streamlit")

    st.divider()

    st.info(
        "Demo uses synthetic business data. "
        "The database connection is restricted "
        "to read-only access."
    )


# ------------------------------------
# MAIN PAGE
# ------------------------------------

st.title("📊 AI SQL Data Analyst Agent")

st.caption(
    "Ask business questions in natural language. "
    "Explore validated SQL results and AI insights."
)

st.divider()

examples = [
    "Which 3 stores have the highest rejection rate?",
    "What is the total order amount for each city?",
    "Which store has the most rejected orders?",
    "Show the average order value for each store.",
    "What percentage of orders were rejected in each city?"
]

selected = st.selectbox(
    "Try an example",
    ["Custom question"] + examples
)

question = st.text_area(
    "Ask your business question",
    value="" if selected == "Custom question" else selected,
    placeholder="E.g. Which city has the highest order amount?",
    height=100
)

analyze = st.button(
    "🚀 Analyze Data",
    type="primary"
)

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if analyze:

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        with st.spinner("Agent is analyzing the data..."):

            started = time.perf_counter()

            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question.strip()},
                    timeout=90
                )

                latency = round(
                    time.perf_counter() - started, 2
                )

                data = response.json()

                if not response.ok or not data.get(
                    "success", False
                ):
                    st.session_state.analysis = None
                    st.error(
                        data.get(
                            "error",
                            "Analysis could not be completed."
                        )
                    )

                else:
                    st.session_state.analysis = {
                        "data": data,
                        "latency": latency
                    }

            except requests.RequestException:
                st.session_state.analysis = None
                st.error(
                    "Cannot connect to FastAPI. "
                    "Check that the backend is running."
                )

            except ValueError:
                st.session_state.analysis = None
                st.error("Invalid API response.")


# ------------------------------------
# SHOW RESULTS
# ------------------------------------

if st.session_state.analysis:

    analysis = st.session_state.analysis
    data = analysis["data"]

    df = pd.DataFrame(
        data.get("rows", []),
        columns=data.get("columns", [])
    )

    df = format_dataframe(df)

    st.success("Analysis completed successfully!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Rows returned",
            data.get("row_count", len(df))
        )

    with col2:
        st.metric(
            "SQL attempts",
            data.get("attempts", 0)
        )

    with col3:
        st.metric(
            "Response time",
            f"{analysis['latency']:.2f}s"
        )

    st.divider()

    tab1, tab2, tab3 = st.tabs([
        "📈 Visualization",
        "📋 Data Results",
        "🧠 AI Insights"
    ])

    # ---------------------------
    # TAB 1: VISUALIZATION
    # ---------------------------

    with tab1:
        st.subheader("Automatic Data Visualization")

        chart_info = create_chart_data(df)

        if chart_info is not None:

            chart_df, x_col, y_col = chart_info

            st.bar_chart(
                chart_df,
                x=x_col,
                y=y_col
            )

            st.caption(
                f"Chart: {y_col} by {x_col}. "
                "Interpret percentages alongside sample sizes."
            )

        else:
            st.info(
                "No suitable categorical-numeric "
                "column pair found for a bar chart."
            )

    # ---------------------------
    # TAB 2: RESULTS
    # ---------------------------

    with tab2:
        st.subheader("Database Results")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        csv_data = df.to_csv(index=False)

        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="ai_agent_results.csv",
            mime="text/csv"
        )

        with st.expander("Generated SQL"):
            st.code(
                data.get("sql", ""),
                language="sql"
            )

    # ---------------------------
    # TAB 3: INSIGHTS
    # ---------------------------

    with tab3:
        st.subheader("AI Business Analysis")

        insight = data.get("insight", "")

        if insight:
            st.write(insight)
        else:
            st.info(
                "AI insights were skipped or unavailable."
            )

        st.caption(
            "AI-generated interpretations should "
            "be verified against the source results."
        )
