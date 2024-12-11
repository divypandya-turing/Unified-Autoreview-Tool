"""This file contains the Streamlist app for the Unified Autoreview Tool."""

import altair as alt  # noqa: E0401
import pandas as pd  # noqa: E0401
import streamlit as st  # noqa: E0401
from streamlit.delta_generator import DeltaGenerator  # noqa: E0401

from review_services import VALIDATOR_LIST, ServicesRunner  # noqa: E0401


def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="Unified SFT AutoReviewer", layout="wide")

    # Header
    st.title("Unified SFT AutoReviewer")

    # Top Section: Folder Input, Validate Button, and Donut Chart
    top_container = st.container()
    with top_container:
        left_col, right_col = st.columns([2, 3], gap="medium")

        with left_col:
            # Folder ID Input with reduced spacing
            st.markdown("<h4 style='margin-bottom:0;'>Folder / File ID</h4>", unsafe_allow_html=True)
            folder_id = st.text_input("", placeholder="Enter Folder ID", key="folder_id")

            # Scrollable List of Validators
            st.markdown("<h4 style='margin-top:20px;'>Select Validators</h4>", unsafe_allow_html=True)
            validators = list(VALIDATOR_LIST.keys())
            selected_validators = st.multiselect(
                "",
                validators,
                default=validators,  # Select all validators by default
                key="validators",
            )
            validate_button = st.button("Validate", use_container_width=True)

        with right_col:
            # Centered "SFT Passed Rate" over the donut chart
            st.markdown(
                "<h4 style='text-align:center; margin-bottom:0;'>SFT Pass Rate</h4>",
                unsafe_allow_html=True,
            )
            pass_rate_placeholder = st.empty()

    # Donut chart initial state
    pass_rate = 0  # Default pass rate

    # Bottom Section: Validation Results Table
    st.markdown("### Validation Results")
    results_container = st.container()
    with results_container:
        results_table_placeholder = st.empty()

    # Perform Validation on Button Click
    if validate_button:
        if folder_id:  # Assume a valid folder ID is entered
            if not selected_validators:
                st.error("Please select at least one validator.")

            else:
                results_df, pass_rate = ServicesRunner(folder_id, selected_validators).run_services(
                    services_progress_bar=st.progress(0),
                    services_eta_placeholder=st.empty(),
                )
                draw_donut_chart(pass_rate, pass_rate_placeholder)
                display_results(results_table_placeholder, results_df)

        else:
            st.error("Please enter a valid Folder ID.")


def draw_donut_chart(pass_rate: float, placeholder: DeltaGenerator):
    """Draw a donut chart for SFT Passed Rate using Altair and render it in a placeholder.

    Parameters
    ----------
    pass_rate : float
        Percentage of SFTs passed.

    placeholder : DeltaGenerator
        Placeholder to display the donut chart.
    """
    data = pd.DataFrame({"Status": ["Pass", "Fail"], "Value": [pass_rate, 100 - pass_rate]})

    donut_chart = (
        alt.Chart(data)
        .mark_arc(innerRadius=50, outerRadius=100)
        .encode(
            theta=alt.Theta(field="Value", type="quantitative"),
            color=alt.Color(
                field="Status",
                type="nominal",
                scale=alt.Scale(domain=["Pass", "Fail"], range=["#4CAF50", "#FF5252"]),  # Green for Pass, Red for Fail
            ),
            tooltip=[alt.Tooltip("Value:Q", format=".1f", title="%")],  # Show only percentage on hover
        )
        .properties(width=300, height=300)
    )

    placeholder.altair_chart(donut_chart, use_container_width=True)


def display_results(placeholder: DeltaGenerator, results_df: pd.DataFrame):
    """Display validation results in a table.

    Parameters
    ----------
    placeholder : DeltaGenerator
        Placeholder to display the results.

    results : list[dict[str, str]]
        List of dictionaries containing validation results.
    """
    if len(results_df) > 0:

        # Calculate dynamic height: base height + additional height per row
        base_height = 100  # Minimum height
        row_height = 35  # Approximate height per row
        dynamic_height = min(400, base_height + (len(results_df) * row_height))

        # Display the DataFrame as a table
        placeholder.dataframe(
            results_df.style.set_properties(**{"text-align": "center"}),
            use_container_width=True,
            height=dynamic_height,
        )
    else:
        placeholder.info("No results to display.")


if __name__ == "__main__":
    main()
