import streamlit as st
import pandas as pd

from assignment_optimizer import run_assignment_optimizer
from set_covering_optimizer import run_set_covering_optimizer
from facility_location_optimizer import run_facility_location_optimizer
from transportation_optimizer import run_transportation_optimizer
from scheduling_optimizer import run_scheduling_optimizer

from hidden_profit_engine import (
    analyze_business,
    validate_financial_data,
    optimize_profit_improvement,
)

from report_generator import (
    create_profit_opportunity_chart,
    create_scenario_cost_chart,
    create_pdf_report,
)
if "analysis_ready" not in st.session_state:
    st.session_state.analysis_ready = False

st.set_page_config(
    page_title="Hidden Profit Analytics",
    layout="wide",
)

tool = st.sidebar.selectbox(
    "Choose a tool",
    [
        "Profit Analyzer",
        "Assignment Optimizer",
        "Set Covering Optimizer",
        "Facility Location Optimizer",
        "Transportation Optimizer",
        "Scheduling Optimizer",
        "Resource Allocation Optimizer",
    ]
)

st.info(
    "Private Beta: Hidden Profit Analytics is currently being tested with a limited group of users. "
    "Please upload only business data you are authorized to use. "
    "Results are provided for decision-support purposes and should not be considered accounting, legal, tax, or financial advice."
)

st.caption(
    "Data handling: Uploaded CSV data is used within the active app session to perform the analysis. "
    "Hidden Profit Analytics does not intentionally save uploaded CSV files to the application repository. "
    "Generated PDF reports are created temporarily for download."
)

if tool == "Assignment Optimizer":
    st.header("Assignment Optimizer")

    st.write(
        "Find the lowest-cost assignment of employees, resources, "
        "or teams to tasks while comparing the optimized solution "
        "to the current assignment."
    )

    assignment_file = st.file_uploader(
        "Upload Assignment Data CSV",
        type=["csv"],
        key="assignment_upload"
    )

    if assignment_file is not None:
        try:
            results = run_assignment_optimizer(assignment_file)

            st.success("Optimization completed successfully.")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Current Cost",
                f"${results['current_cost']:,.2f}"
            )

            col2.metric(
                "Optimized Cost",
                f"${results['optimized_cost']:,.2f}"
            )

            col3.metric(
                "Potential Savings",
                f"${results['savings']:,.2f}"
            )

            col4.metric(
                "Savings %",
                f"{results['savings_percent']:.2f}%"
            )

            st.subheader("Recommended Assignments")

            st.dataframe(
                results["assignments"],
                use_container_width=True
            )

            st.subheader("Assignment Changes")

            st.dataframe(
                results["comparison"],
                use_container_width=True
            )

        except Exception as error:
            st.error(str(error))

if tool == "Set Covering Optimizer":
    st.header("Set Covering Optimizer")

    st.write(
        "Choose the minimum-cost set of locations, options, or resources "
        "needed to cover every required area at least once."
    )

    set_covering_file = st.file_uploader(
        "Upload Set Covering Data CSV",
        type=["csv"],
        key="set_covering_upload"
    )

    if set_covering_file is not None:
        try:
            results = run_set_covering_optimizer(set_covering_file)

            st.success("Optimization completed successfully.")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Current Cost",
                f"${results['current_cost']:,.2f}"
            )

            col2.metric(
                "Optimized Cost",
                f"${results['optimized_cost']:,.2f}"
            )

            col3.metric(
                "Potential Savings",
                f"${results['savings']:,.2f}"
            )

            col4.metric(
                "Savings %",
                f"{results['savings_percent']:.2f}%"
            )

            st.subheader("Recommended Options")

            st.dataframe(
                results["selected_options"],
                use_container_width=True
            )

            st.subheader("Configuration Changes")

            st.dataframe(
                results["comparison"],
                use_container_width=True
            )

        except Exception as error:
            st.error(str(error))

if tool == "Facility Location Optimizer":
    st.header("Facility Location Optimizer")

    st.write(
        "Determine which facilities should remain open, close, or open, "
        "and how customers should be assigned to minimize total cost."
    )

    facility_file = st.file_uploader(
        "Upload Facility Cost Data CSV",
        type=["csv"],
        key="facility_location_upload"
    )

    demand_file = st.file_uploader(
        "Upload Customer Demand Data CSV",
        type=["csv"],
        key="facility_demand_upload"
    )

    if facility_file is not None and demand_file is not None:
        try:
            results = run_facility_location_optimizer(
                facility_file,
                demand_file
            )

            st.success("Optimization completed successfully.")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Current Cost",
                f"${results['current_total_cost']:,.2f}"
            )

            col2.metric(
                "Optimized Cost",
                f"${results['optimized_total_cost']:,.2f}"
            )

            col3.metric(
                "Potential Savings",
                f"${results['savings']:,.2f}"
            )

            col4.metric(
                "Savings %",
                f"{results['savings_percent']:.2f}%"
            )

            st.subheader("Facility Recommendations")

            st.dataframe(
                results["facility_comparison"],
                use_container_width=True
            )

            st.subheader("Customer Assignment Changes")

            st.dataframe(
                results["assignment_comparison"],
                use_container_width=True
            )

        except Exception as error:
            st.error(str(error))

if tool == "Transportation Optimizer":
    st.header("Transportation Optimizer")

    st.write(
        "Determine how much should be shipped from each source to each "
        "destination to satisfy demand at the lowest total transportation cost."
    )

    cost_file = st.file_uploader(
        "Upload Transportation Cost Data CSV",
        type=["csv"],
        key="transportation_cost_upload"
    )

    supply_file = st.file_uploader(
        "Upload Supply Data CSV",
        type=["csv"],
        key="transportation_supply_upload"
    )

    demand_file = st.file_uploader(
        "Upload Demand Data CSV",
        type=["csv"],
        key="transportation_demand_upload"
    )

    current_file = st.file_uploader(
        "Upload Current Shipping Plan CSV",
        type=["csv"],
        key="transportation_current_upload"
    )

    if (
        cost_file is not None
        and supply_file is not None
        and demand_file is not None
        and current_file is not None
    ):
        try:
            results = run_transportation_optimizer(
                cost_file,
                supply_file,
                demand_file,
                current_file
            )

            st.success("Optimization completed successfully.")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Current Cost",
                f"${results['current_total_cost']:,.2f}"
            )

            col2.metric(
                "Optimized Cost",
                f"${results['optimized_total_cost']:,.2f}"
            )

            col3.metric(
                "Potential Savings",
                f"${results['savings']:,.2f}"
            )

            col4.metric(
                "Savings %",
                f"{results['savings_percent']:.2f}%"
            )

            st.subheader("Shipment Changes")

            st.dataframe(
                results["shipment_comparison"],
                use_container_width=True
            )

        except Exception as error:
            st.error(str(error))

if tool == "Scheduling Optimizer":
    st.header("Scheduling Optimizer")

    st.write(
        "Build a minimum-cost employee schedule while meeting staffing "
        "requirements and respecting employee availability."
    )

    cost_file = st.file_uploader(
        "Upload Scheduling Cost Data CSV",
        type=["csv"],
        key="scheduling_cost_upload"
    )

    requirements_file = st.file_uploader(
        "Upload Staffing Requirements CSV",
        type=["csv"],
        key="scheduling_requirements_upload"
    )

    availability_file = st.file_uploader(
        "Upload Employee Availability CSV",
        type=["csv"],
        key="scheduling_availability_upload"
    )

    current_file = st.file_uploader(
        "Upload Current Schedule CSV",
        type=["csv"],
        key="scheduling_current_upload"
    )

    if (
        cost_file is not None
        and requirements_file is not None
        and availability_file is not None
        and current_file is not None
    ):
        try:
            results = run_scheduling_optimizer(
                cost_file,
                requirements_file,
                availability_file,
                current_file
            )

            st.success("Optimization completed successfully.")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Current Cost",
                f"${results['current_total_cost']:,.2f}"
            )

            col2.metric(
                "Optimized Cost",
                f"${results['optimized_total_cost']:,.2f}"
            )

            col3.metric(
                "Potential Savings",
                f"${results['savings']:,.2f}"
            )

            col4.metric(
                "Savings %",
                f"{results['savings_percent']:.2f}%"
            )

            st.subheader("Schedule Changes")

            st.dataframe(
                results["schedule_comparison"],
                use_container_width=True
            )

        except Exception as error:
            st.error(str(error))            

if tool == "Profit Analyzer":
    st.title("Hidden Profit Analytics")
    st.subheader("Business Optimization Dashboard")

    with st.expander("How to Use Hidden Profit Analytics", expanded=False):
        st.markdown(
            """
    1. **Enter the business information** and select a target profit margin.
    2. **Upload your financial data** using a CSV with Month, Revenue, and Expenses. If needed, download the CSV template in the Financial Data section.
    3. **Set the improvement assumptions** based on what is realistic for the business.
    4. Click **Run Analysis** to identify potential hidden profit opportunities.
    5. **Review the optimization recommendation, scenarios, and sensitivity analysis.**
    6. **Generate and download the Client Report** for a summary of the findings and recommended action plan.
    7. When you're finished testing, open **Help & FAQs** and click **Give Beta Feedback** to share your experience.
    """
        )

    with st.expander("Help & FAQs", expanded=False):

        st.markdown("### Getting Started")

        st.markdown(
            """
    **What does Hidden Profit Analytics do?**  
    Hidden Profit Analytics analyzes monthly revenue and expenses to identify
    potential profit improvement opportunities. It then uses optimization modeling
    to recommend a cost-effective combination of revenue improvement and expense
    reduction based on the assumptions and limits you provide.

    **What information do I need?**  
    Upload a CSV file containing these three columns:

    - `Month`
    - `Revenue`
    - `Expenses`

    If you do not already have a correctly formatted CSV, use the
    **Download CSV Template** button in the Financial Data section.

    **What is the Target Profit Margin?**  
    This is the percentage of revenue you would like the business to retain as
    profit. Hidden Profit Analytics compares current performance with this target
    to estimate the potential profit opportunity.
    """
        )

        st.markdown("### Understanding the Analysis")

        st.markdown(
            """
    **What is Hidden Profit Opportunity?**  
    This is the estimated difference between current profit and the profit needed
    to achieve the selected target margin. It represents a potential opportunity,
    not a guaranteed financial result.

    **What does the optimization recommendation mean?**  
    The optimization model evaluates possible revenue improvement and expense
    reduction and recommends a combination designed to close the identified profit
    gap at the lowest estimated implementation cost, subject to the assumptions
    and limits you enter.

    **What are Revenue Cost and Expense Cost?**  
    These estimate how much it costs to achieve $1 of improvement. For example,
    a Revenue Cost of $0.30 means the model assumes approximately $0.30 must be
    spent to generate $1 of additional revenue.

    **What are Maximum Revenue Increase and Maximum Expense Reduction?**  
    These limits help prevent the model from recommending changes that you believe
    would be unrealistic for the business.
    """
        )

        st.markdown("### Results & Reports")

        st.markdown(
            """
    **What is sensitivity analysis?**  
    Sensitivity analysis tests whether the recommended strategy changes when
    implementation-cost assumptions change. This helps you evaluate how robust
    the recommendation may be.

    **What is the Client Report?**  
    The downloadable PDF summarizes the analysis, optimization recommendation,
    scenario comparisons, estimated costs and benefits, sensitivity results, and
    management action plan.

    **Are the results guaranteed?**  
    No. Results depend on the financial data and assumptions entered. Hidden
    Profit Analytics is a business decision-support tool and does not replace
    professional accounting, tax, legal, or financial advice.
    """
        )

        st.link_button(
            "Give Beta Feedback",
            "https://forms.gle/Q8Ey4TB6jYM3Yo6a6",
            use_container_width=True
        )   

    # ==========================================
    # STEP 1: BUSINESS INFORMATION
    # ==========================================

    st.sidebar.header("Client Setup")

    with st.sidebar.expander(
        "1. Business Information",
        expanded=True
    ):

        company_name = st.text_input(
            "Company Name",
            value="Sample Business",
            help=(
                "Enter the business name that should appear "
                "in the analysis and client report."
            )
        )

        target_percent = st.number_input(
            "Target Profit Margin (%)",
            min_value=0.0,
            max_value=100.0,
            value=22.0,
            step=1.0,
            help=(
                "Enter the profit margin the business would "
                "like to achieve. The value must be greater "
                "than 0% and less than 100%."
            )
        )

    target_margin = target_percent / 100

    # ==========================================
    # STEP 2: FINANCIAL DATA
    # ==========================================

    with st.sidebar.expander(
        "2. Financial Data",
        expanded=True
    ):
        csv_template = (
            "Month,Revenue,Expenses\n"
            "January,30000,26000\n"
            "February,34000,28000\n"
            "March,38000,30000\n"
        )

        st.caption(
            "Need a file to get started? Download the CSV template, "
            "replace the sample values with your monthly financial data, "
            "save it, and upload it below."
        )

        st.download_button(
            label="Download CSV Template",
            data=csv_template,
            file_name="Hidden_Profit_Analytics_Template.csv",
            mime="text/csv",
            use_container_width=True
        )
        uploaded_file = st.file_uploader(
            "Upload financial data CSV",
            type=["csv"],
            help=(
                "Upload a CSV containing Month, Revenue, and Expenses."
            )
        ) 

    # ==========================================
    # STEP 3: IMPROVEMENT ASSUMPTIONS
    # ==========================================

    with st.sidebar.expander(
        "3. Improvement Assumptions",
        expanded=False
    ):

        st.caption(
            "Estimate what improvements are realistically achievable for "
            "this business. Hidden Profit Analytics will use these "
            "assumptions to build the optimization model."
        )

        # ------------------------------------------
        # Estimate Improvement Costs
        # ------------------------------------------

        with st.expander(
            "Estimate Improvement Costs",
            expanded=False
        ):

            revenue_improvement_example = st.number_input(
                "Expected monthly revenue improvement ($)",
                min_value=1.0,
                value=5000.0,
                step=500.0,
                help=(
                    "Estimate the additional monthly revenue that a realistic "
                    "sales, pricing, marketing, or customer-retention initiative "
                    "could generate."
                )
            )

            revenue_implementation_cost = st.number_input(
                "Cost to achieve that revenue improvement ($)",
                min_value=0.0,
                value=1500.0,
                step=100.0,
                help=(
                    "Estimate the implementation cost, such as marketing, "
                    "labor, technology, training, or other resources."
                )
            )

            expense_savings_example = st.number_input(
                "Expected monthly expense savings ($)",
                min_value=1.0,
                value=2000.0,
                step=500.0,
                help=(
                    "Estimate the monthly savings from a realistic process, "
                    "purchasing, staffing, technology, or operating improvement."
                )
            )

            expense_implementation_cost = st.number_input(
                "Cost to achieve those expense savings ($)",
                min_value=0.0,
                value=200.0,
                step=100.0,
                help=(
                    "Estimate the implementation cost required to achieve "
                    "the expected monthly expense savings."
                )
            )

        # Calculate optimization cost coefficients
        revenue_cost = (
            revenue_implementation_cost
            / revenue_improvement_example
        )

        expense_cost = (
            expense_implementation_cost
            / expense_savings_example
        )

        # ------------------------------------------
        # Model Details
        # ------------------------------------------

        with st.expander(
            "Model Details",
            expanded=False
        ):

            st.caption(
                f"Calculated optimization costs: "
                f"\\${revenue_cost:.2f} per \\$1 of additional revenue and "
                f"\\${expense_cost:.2f} per \\$1 of expense reduction."
            )

            sensitivity_percent = st.selectbox(
                "Sensitivity testing range",
                options=[10, 20, 30],
                index=1,
                format_func=lambda x: f"±{x}%",
                help=(
                    "Choose how far implementation-cost assumptions should vary "
                    "above and below the current estimates during sensitivity analysis."
                )
            )

        # ------------------------------------------
        # Set Realistic Limits
        # ------------------------------------------

        with st.expander(
            "Set Realistic Limits",
            expanded=False
        ):

            max_revenue_increase = st.number_input(
                "Maximum additional monthly revenue ($)",
                min_value=0.0,
                value=3000.0,
                step=500.0,
                help=(
                    "How much additional monthly revenue could realistically "
                    "be generated by this business?"
                )
            )

            max_expense_reduction = st.number_input(
                "Maximum monthly expense reduction ($)",
                min_value=0.0,
                value=2500.0,
                step=500.0,
                help=(
                    "How much could monthly expenses realistically be reduced "
                    "without harming essential operations?"
                )
            )   

    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)
        except Exception:
            st.error(
                "The uploaded file could not be read as a valid CSV. "
                "Please upload a properly formatted CSV file with Month, Revenue, and Expenses columns."
            )
            st.stop()

        is_valid, validation_message = validate_financial_data(data)

        if not is_valid:
            st.error(validation_message)
            st.stop()
        st.markdown("#### Uploaded Data")

        st.dataframe(
            data,
            use_container_width=True
        )

        st.sidebar.divider()

        st.sidebar.caption(
            "Review the client information, financial data, "
            "and improvement assumptions before running the analysis."
        )

        if st.sidebar.button(
            "4. Run Analysis",
            type="primary",
            use_container_width=True
        ):

            # Clear results from any previous analysis
            st.session_state.analysis_ready = False

            if "pdf_bytes" in st.session_state:
                del st.session_state.pdf_bytes

            if "custom_recommendation" in st.session_state:
                del st.session_state.custom_recommendation

            # Validate company name
            if not company_name.strip():
                st.error(
                    "Please enter a company name before running the analysis."
                )
                st.stop()

            # Validate target margin
            if target_percent <= 0:
                st.error(
                    "Target Profit Margin must be greater than 0%."
                )
                st.stop()

            if target_percent >= 100:
                st.error(
                    "Target Profit Margin must be less than 100%."
                )
                st.stop()

            # Validate improvement limits
            if (
                max_revenue_increase == 0
                and max_expense_reduction == 0
            ):
                st.error(
                    "At least one improvement option must be available. "
                    "Please enter a possible revenue increase, expense reduction, "
                    "or both."
                )
                st.stop()

            # ==========================================
            # ANALYSIS STARTS HERE
            # ==========================================

            analyzed_data = analyze_business(
                data,
                target_margin,
            )

            total_revenue = analyzed_data["Revenue"].sum()
            total_profit = analyzed_data["Profit"].sum()
            total_opportunity = analyzed_data["Profit Opportunity"].sum()

            largest_index = analyzed_data["Profit Opportunity"].idxmax()
            largest_opportunity = analyzed_data.loc[largest_index]
            profit_gap = largest_opportunity["Profit Opportunity"]

            optimization_result = optimize_profit_improvement(
                profit_gap,
                revenue_cost,
                expense_cost,
                max_revenue_increase,
                max_expense_reduction
            )
            st.markdown("## Executive Summary")

            st.caption(
                "A snapshot of current financial performance and the "
                "estimated opportunity to improve profitability."
                    )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Revenue",
                f"${total_revenue:,.2f}",
            )

            col2.metric(
                "Total Profit",
                f"${total_profit:,.2f}",
            )

            col3.metric(
                "Hidden Profit Opportunity",
                f"${total_opportunity:,.2f}",
            )

            st.info(
                f"**Priority Opportunity:** "
                f"{largest_opportunity['Month']} has the largest profit gap at "
                f"**${profit_gap:,.2f}**."
            )
            st.write(
                f"{largest_opportunity['Month']} has the largest "
                f"profit opportunity at "
                f"${profit_gap:,.2f}."
            )

            st.markdown("## Monthly Performance")

            st.caption(
                "Review monthly profitability, performance status, "
                "and the size of each hidden profit opportunity."
            )

            monthly_display = analyzed_data[
                [
                    "Month",
                    "Revenue",
                    "Expenses",
                    "Profit",
                    "Profit Margin",
                    "Performance",
                    "Profit Opportunity",
                ]
            ].copy()

            monthly_display["Revenue"] = monthly_display["Revenue"].map(
                lambda x: f"${x:,.0f}"
            )

            monthly_display["Expenses"] = monthly_display["Expenses"].map(
                lambda x: f"${x:,.0f}"
            )

            monthly_display["Profit"] = monthly_display["Profit"].map(
                lambda x: f"${x:,.0f}"
            )

            monthly_display["Profit Margin"] = monthly_display[
                "Profit Margin"
            ].map(
                lambda x: f"{x:.2f}%"
            )

            monthly_display["Profit Opportunity"] = monthly_display[
                "Profit Opportunity"
            ].map(
                lambda x: f"${x:,.0f}"
            )

            st.dataframe(
                monthly_display,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("### Profit Opportunity by Month")
            create_profit_opportunity_chart(
                analyzed_data,
                largest_opportunity
            )

            st.image(
                "profit_opportunity.png",
                use_container_width=True
            )
            st.markdown("## Optimization Assumptions")

            st.caption(
                "These client-specific assumptions define the practical limits "
                "and estimated implementation costs used by the optimization model."
            )

            assumption_col1, assumption_col2, assumption_col3, assumption_col4 = st.columns(4)

            with assumption_col1:
                st.metric(
                    "Revenue Cost / $1",
                    f"${revenue_cost:.2f}"
                )

            with assumption_col2:
                st.metric(
                    "Expense Cost / $1",
                    f"${expense_cost:.2f}"
                )

            with assumption_col3:
                st.metric(
                    "Max Revenue Increase",
                    f"${max_revenue_increase:,.0f}"
                )

            with assumption_col4:
                st.metric(
                    "Max Expense Reduction",
                    f"${max_expense_reduction:,.0f}"
                )
            st.markdown("## Custom Optimization Recommendation")

            st.caption(
                "Based on the client-specific assumptions, the optimizer identifies "
                "the lowest-cost feasible way to close the priority profit gap."
            )

            if optimization_result.success:
                additional_revenue = optimization_result.x[0]
                expense_reduction = optimization_result.x[1]
                implementation_cost = optimization_result.fun

                custom_recommendation = {
                    "Scenario": "Custom",
                    "Revenue Increase": additional_revenue,
                    "Expense Reduction": expense_reduction,
                    "Implementation Cost": implementation_cost
                }

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Revenue Increase",
                    f"${additional_revenue:,.2f}"
                )

                col2.metric(
                    "Expense Reduction",
                    f"${expense_reduction:,.2f}"
                )

                col3.metric(
                    "Implementation Cost",
                    f"${implementation_cost:,.2f}"
                )

                st.success(
                    f"Recommended plan for {largest_opportunity['Month']}: "
                    f"reduce monthly expenses by \\${expense_reduction:,.2f} "
                    f"and generate \\${additional_revenue:,.2f} "
                    f"in additional revenue."
                )

                # Explain why the optimizer selected this mix
                if expense_cost < revenue_cost:
                    recommendation_reason = (
                        f"Expense reduction is prioritized because it is estimated to cost "
                        f"${expense_cost:.2f} for each $1 of profit improvement, compared with "
                        f"${revenue_cost:.2f} for each $1 generated through additional revenue. "
                        f"The optimizer therefore uses the lower-cost opportunity first, "
                        f"subject to the realistic limits entered for this business."
                    )

                elif revenue_cost < expense_cost:
                    recommendation_reason = (
                        f"Revenue growth is prioritized because it is estimated to cost "
                        f"${revenue_cost:.2f} for each $1 of profit improvement, compared with "
                        f"${expense_cost:.2f} for each $1 achieved through expense reduction. "
                        f"The optimizer therefore uses the lower-cost opportunity first, "
                        f"subject to the realistic limits entered for this business."
                    )

                else:
                    recommendation_reason = (
                        f"Revenue growth and expense reduction have the same estimated "
                        f"implementation cost of ${revenue_cost:.2f} per $1 of profit "
                        f"improvement. The recommended mix therefore depends primarily on "
                        f"the realistic improvement limits entered for this business."
                    )

                st.info(
                    f"**Why this recommendation?** {recommendation_reason}"
                )

                # ==========================================
                # ROI AND PAYBACK ANALYSIS
                # ==========================================

                monthly_profit_improvement = (
                    additional_revenue + expense_reduction
                )

                first_month_net_benefit = (
                    monthly_profit_improvement - implementation_cost
                )

                if implementation_cost > 0:
                    benefit_cost_ratio = (
                        monthly_profit_improvement / implementation_cost
                    )

                    first_month_roi = (
                        first_month_net_benefit / implementation_cost
                    ) * 100

                    payback_months = (
                        implementation_cost / monthly_profit_improvement
                    )

                else:
                    benefit_cost_ratio = float("inf")
                    first_month_roi = float("inf")
                    payback_months = 0


                st.markdown("### ROI & Payback Analysis")

                st.caption(
                    "Estimate the financial return from implementing the "
                    "recommended optimization strategy."
                )

                roi_col1, roi_col2, roi_col3, roi_col4 = st.columns(4)

                roi_col1.metric(
                    "Monthly Profit Improvement",
                    f"${monthly_profit_improvement:,.2f}"
                )

                roi_col2.metric(
                    "First-Month Net Benefit",
                    f"${first_month_net_benefit:,.2f}"
                )

                if implementation_cost > 0:
                    roi_col3.metric(
                        "Benefit-Cost Ratio",
                        f"{benefit_cost_ratio:.2f}x"
                    )

                    roi_col4.metric(
                        "Estimated Payback",
                        f"{payback_months:.2f} months"
                    )

                else:
                    roi_col3.metric(
                        "Benefit-Cost Ratio",
                        "No Cost"
                    )

                    roi_col4.metric(
                        "Estimated Payback",
                        "Immediate"
                    )

                if implementation_cost > 0:
                    st.success(
                        f"The recommended strategy is expected to generate "
                        f"\\${monthly_profit_improvement:,.2f} in monthly profit improvement "
                        f"for an estimated implementation cost of "
                        f"\\${implementation_cost:,.2f}. "
                        f"That represents a {benefit_cost_ratio:.2f}x benefit-cost ratio "
                        f"and an estimated payback period of "
                        f"{payback_months:.2f} months."
                    )
                else:
                    st.success(
                        f"The recommended strategy is expected to generate "
                        f"\\${monthly_profit_improvement:,.2f} in monthly profit improvement "
                        f"with no estimated implementation cost."
                    )
            else:
                max_possible_improvement = (
                    max_revenue_increase + max_expense_reduction
                )

                remaining_gap = (
                    profit_gap - max_possible_improvement
                )

                st.warning(
                    f"No feasible plan was found. "
                    f"The remaining unresolved gap is "
                    f"\\${remaining_gap:,.2f}."
                )

            st.markdown("## Predefined Scenario Comparison")

            st.caption(
                "These scenarios use the assumptions stored in scenarios.csv."
            )

            scenarios = pd.read_csv("scenarios.csv")

            scenario_results = []

            for _, row in scenarios.iterrows():
                scenario_name = row["Scenario"]
                scenario_max_revenue = row["Max Revenue Increase"]
                scenario_max_expense = row["Max Expense Reduction"]
                scenario_revenue_cost = row["Revenue Cost"]
                scenario_expense_cost = row["Expense Cost"]

                scenario_result = optimize_profit_improvement(
                    profit_gap,
                    scenario_revenue_cost,
                    scenario_expense_cost,
                    scenario_max_revenue,
                    scenario_max_expense
                )

                if scenario_result.success:
                    scenario_results.append({
                        "Scenario": scenario_name,
                        "Status": "Feasible",
                        "Revenue Increase": scenario_result.x[0],
                        "Expense Reduction": scenario_result.x[1],
                        "Implementation Cost": scenario_result.fun,
                        "Remaining Gap": 0
                    })

                else:
                    max_improvement = (
                        scenario_max_revenue
                        + scenario_max_expense
                    )

                    remaining_gap = (
                        profit_gap - max_improvement
                    )

                    scenario_results.append({
                        "Scenario": scenario_name,
                        "Status": "Infeasible",
                        "Revenue Increase": 0,
                        "Expense Reduction": 0,
                        "Implementation Cost": 0,
                        "Remaining Gap": remaining_gap
                    })

            scenario_results_df = pd.DataFrame(
                scenario_results
            )

            st.dataframe(
                scenario_results_df,
                use_container_width=True
            )

            feasible_results = scenario_results_df[
                scenario_results_df["Status"] == "Feasible"
            ]

            if not feasible_results.empty:

                best_index = feasible_results[
                    "Implementation Cost"
                ].idxmin()

                best_scenario = feasible_results.loc[
                    best_index
                ]

                st.markdown("### Lowest-Cost Predefined Scenario")

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Scenario",
                    best_scenario["Scenario"]
                )

                col2.metric(
                    "Revenue Increase",
                    f"${best_scenario['Revenue Increase']:,.2f}"
                )

                col3.metric(
                    "Expense Reduction",
                    f"${best_scenario['Expense Reduction']:,.2f}"
                )

                col4.metric(
                    "Implementation Cost",
                    f"${best_scenario['Implementation Cost']:,.2f}"
                )

                st.info(
                    f"Lowest-cost predefined scenario: "
                    f"{best_scenario['Scenario']} with an "
                    f"estimated implementation cost of "
                    f"\\${best_scenario['Implementation Cost']:,.2f}. "
                    f"This is shown for comparison; the custom optimization above "
                    f"is the primary client recommendation."
                )

                st.markdown("### Predefined Scenario Cost Comparison")

                create_scenario_cost_chart(
                    scenario_results_df,
                    best_scenario
                )

                st.image(
                    "scenario_cost_comparison.png",
                    use_container_width=True
                )
            else:
                st.warning(
                    "None of the predefined scenarios are "
                    "feasible for the current profit gap."
                )

            # Save successful analysis for later Streamlit reruns
            if optimization_result.success and not feasible_results.empty:
                st.session_state.analysis_ready = True
                st.session_state.analyzed_data = analyzed_data
                st.session_state.total_revenue = total_revenue
                st.session_state.total_profit = total_profit
                st.session_state.total_opportunity = total_opportunity
                st.session_state.largest_opportunity = largest_opportunity
                st.session_state.best_scenario = best_scenario
                st.session_state.custom_recommendation = custom_recommendation        

            # ==========================================
            # SENSITIVITY ANALYSIS
            # ==========================================
        
            st.markdown("## Sensitivity Analysis")
        
            st.caption(
                "Test how the recommended strategy changes when estimated "
                "implementation costs are higher or lower than expected."
            )
        
            sensitivity_factor = sensitivity_percent / 100

            revenue_cost_scenarios = {
                f"-{sensitivity_percent}%": revenue_cost * (1 - sensitivity_factor),
                "Current": revenue_cost,
                f"+{sensitivity_percent}%": revenue_cost * (1 + sensitivity_factor)
            }

            expense_cost_scenarios = {
                f"-{sensitivity_percent}%": expense_cost * (1 - sensitivity_factor),
                "Current": expense_cost,
                f"+{sensitivity_percent}%": expense_cost * (1 + sensitivity_factor)
            }
        
            sensitivity_results = []
        
            for revenue_label, test_revenue_cost in revenue_cost_scenarios.items():
        
                for expense_label, test_expense_cost in expense_cost_scenarios.items():
        
                    sensitivity_result = optimize_profit_improvement(
                        profit_gap,
                        test_revenue_cost,
                        test_expense_cost,
                        max_revenue_increase,
                        max_expense_reduction
                    )
        
                    if sensitivity_result.success:
        
                        sensitivity_results.append({
                            "Revenue Cost Change": revenue_label,
                            "Expense Cost Change": expense_label,
                            "Revenue Increase": sensitivity_result.x[0],
                            "Expense Reduction": sensitivity_result.x[1],
                            "Implementation Cost": sensitivity_result.fun,
                            "Status": "Feasible"
                        })
        
                    else:
        
                        sensitivity_results.append({
                            "Revenue Cost Change": revenue_label,
                            "Expense Cost Change": expense_label,
                            "Revenue Increase": None,
                            "Expense Reduction": None,
                            "Implementation Cost": None,
                            "Status": "Infeasible"
                        })
        
            sensitivity_df = pd.DataFrame(sensitivity_results)

            # Save sensitivity results
            st.session_state.sensitivity_df = sensitivity_df
            st.session_state.sensitivity_percent = sensitivity_percent
        
            sensitivity_display = sensitivity_df.copy()

            sensitivity_display = sensitivity_display.rename(
                columns={
                    "Revenue Cost Change": "Revenue Cost",
                    "Expense Cost Change": "Expense Cost",
                    "Revenue Increase": "Revenue Increase",
                    "Expense Reduction": "Expense Reduction",
                    "Implementation Cost": "Impl. Cost"
                }
            )

            for column in [
                "Revenue Increase",
                "Expense Reduction",
                "Impl. Cost"
            ]:
                sensitivity_display[column] = sensitivity_display[column].apply(
                    lambda x: f"${x:,.2f}" if pd.notna(x) else "-"
                )

            sensitivity_display = sensitivity_display[
                [
                    "Revenue Cost",
                    "Expense Cost",
                    "Revenue Increase",
                    "Expense Reduction",
                    "Impl. Cost"
                ]
            ]

            st.dataframe(
                sensitivity_display,
                use_container_width=True,
                hide_index=True
            )
        
            feasible_sensitivity = sensitivity_df[
                sensitivity_df["Status"] == "Feasible"
            ].copy()
        
            if not feasible_sensitivity.empty:
        
                lowest_cost_case = feasible_sensitivity.loc[
                    feasible_sensitivity["Implementation Cost"].idxmin()
                ]
        
                highest_cost_case = feasible_sensitivity.loc[
                    feasible_sensitivity["Implementation Cost"].idxmax()
                ]
        
                strategy_combinations = feasible_sensitivity[
                    ["Revenue Increase", "Expense Reduction"]
                ].drop_duplicates()

                strategy_is_stable = len(strategy_combinations) == 1

                min_sensitivity_cost = feasible_sensitivity[
                    "Implementation Cost"
                ].min()

                max_sensitivity_cost = feasible_sensitivity[
                    "Implementation Cost"
                ].max()

                if strategy_is_stable:

                    stable_revenue = strategy_combinations.iloc[0][
                        "Revenue Increase"
                    ]

                    stable_expense = strategy_combinations.iloc[0][
                        "Expense Reduction"
                    ]

                    st.success(
                        f"Robust Recommendation: The optimal strategy remains unchanged "
                        f"across all tested ±{sensitivity_percent}% "
                        f"implementation-cost assumptions."
                        f"The model consistently recommends "
                        f"\\${stable_expense:,.2f} in expense reduction and "
                        f"\\${stable_revenue:,.2f} in additional revenue. "
                        f"Estimated implementation cost ranges from "
                        f"\\${min_sensitivity_cost:,.2f} to "
                        f"\\${max_sensitivity_cost:,.2f}."
                    )

                else:

                    st.warning(
                        f"Sensitivity Detected: The optimal strategy changes under some "
                        f"of the tested ±{sensitivity_percent}% implementation-cost assumptions. "
                        f"Estimated implementation cost ranges from "
                        f"\\${min_sensitivity_cost:,.2f} to "
                        f"\\${max_sensitivity_cost:,.2f}. "
                        f"Management should review the sensitivity results before "
                        f"implementing the recommendation."
                    )
        
        # ==========================================
        # FOLLOW-UP RESULTS
        # ==========================================

        if st.session_state.analysis_ready:

            st.markdown("## Follow-Up Results")

            st.caption(
                "Compare actual post-implementation results with the original "
                "optimization recommendation."
            )

            with st.expander(
                "Enter Actual Results",
                expanded=False
            ):

                with st.form("follow_up_results_form"):

                    actual_revenue_increase = st.number_input(
                        "Actual additional monthly revenue achieved ($)",
                        min_value=0.0,
                        value=0.0,
                        step=100.0
                    )

                    actual_expense_reduction = st.number_input(
                        "Actual monthly expense reduction achieved ($)",
                        min_value=0.0,
                        value=0.0,
                        step=100.0
                    )

                    actual_implementation_cost = st.number_input(
                        "Actual implementation cost ($)",
                        min_value=0.0,
                        value=0.0,
                        step=100.0
                    )

                    follow_up_submitted = st.form_submit_button(
                        "Evaluate Actual Results",
                        type="primary"
                    )

            if follow_up_submitted:

                recommended_revenue = (
                    st.session_state.custom_recommendation[
                        "Revenue Increase"
                    ]
                )

                recommended_expense = (
                    st.session_state.custom_recommendation[
                        "Expense Reduction"
                    ]
                )

                recommended_cost = (
                    st.session_state.custom_recommendation[
                        "Implementation Cost"
                    ]
                )

                actual_profit_improvement = (
                    actual_revenue_increase
                    + actual_expense_reduction
                )

                recommended_profit_improvement = (
                    recommended_revenue
                    + recommended_expense
                )

                improvement_variance = (
                    actual_profit_improvement
                    - recommended_profit_improvement
                )

                cost_variance = (
                    actual_implementation_cost
                    - recommended_cost
                )

                st.markdown("### Recommended vs. Actual")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Recommended Profit Improvement",
                    f"${recommended_profit_improvement:,.2f}"
                )

                col2.metric(
                    "Actual Profit Improvement",
                    f"${actual_profit_improvement:,.2f}"
                )

                st.caption(
                    f"Variance from recommendation: "
                    f"${improvement_variance:,.2f}"
                )

                col3.metric(
                    "Actual Implementation Cost",
                    f"${actual_implementation_cost:,.2f}",
                    delta=f"${cost_variance:,.2f}",
                    delta_color="inverse"
                )

                if actual_profit_improvement >= recommended_profit_improvement:

                    st.success(
                        "Actual improvement met or exceeded the original "
                        "optimization recommendation."
                    )

                else:

                    remaining_gap = (
                        recommended_profit_improvement
                        - actual_profit_improvement
                    )

                    st.warning(
                        f"Actual improvement is "
                        f"${remaining_gap:,.2f} below the original recommendation. "
                        f"A follow-up optimization may be useful."
                    )

                    follow_up_result = optimize_profit_improvement(
                        remaining_gap,
                        revenue_cost,
                        expense_cost,
                        max_revenue_increase,
                        max_expense_reduction
                    )

                    if follow_up_result.success:

                        follow_up_revenue = follow_up_result.x[0]
                        follow_up_expense = follow_up_result.x[1]
                        follow_up_cost = follow_up_result.fun

                        st.markdown("### Follow-Up Optimization Recommendation")

                        st.caption(
                            "Lowest-cost additional improvement needed to close "
                            "the remaining profit gap."
                        )

                        col1, col2, col3 = st.columns(3)

                        col1.metric(
                            "Additional Revenue Needed",
                            f"${follow_up_revenue:,.2f}"
                        )

                        col2.metric(
                            "Additional Expense Reduction",
                            f"${follow_up_expense:,.2f}"
                        )

                        col3.metric(
                            "Estimated Additional Cost",
                            f"${follow_up_cost:,.2f}"
                        )

                        st.success(
                            f"To close the remaining ${remaining_gap:,.2f} gap, "
                            f"the optimizer recommends approximately "
                            f"${follow_up_expense:,.2f} in additional monthly "
                            f"expense reduction and ${follow_up_revenue:,.2f} "
                            f"in additional monthly revenue."
                        )

                    else:

                        st.error(
                            "The remaining profit gap cannot be closed within the "
                            "current improvement limits. Review the assumptions and "
                            "consider increasing the allowable revenue or expense "
                            "improvement."
                        )
        
        # ==========================================
        # CLIENT REPORT
        # ==========================================

        if st.session_state.analysis_ready:

            st.markdown("## Client Report")

            st.caption(
                "Generate a client-ready PDF containing the financial analysis, "
                "custom optimization recommendation, predefined scenario comparison, "
                "optimization assumptions, and management action plan."
            )

            if st.button(
                "Generate Client Report",
                type="primary"
            ):

                pdf_path = create_pdf_report(
                    st.session_state.analyzed_data,
                    st.session_state.total_revenue,
                    st.session_state.total_profit,
                    st.session_state.total_opportunity,
                    st.session_state.largest_opportunity,
                    st.session_state.custom_recommendation,
                    company_name,
                    target_margin,
                    revenue_cost,
                    expense_cost,
                    max_revenue_increase,
                    max_expense_reduction,
                    st.session_state.sensitivity_df,
                    st.session_state.sensitivity_percent
                )

                with open(pdf_path, "rb") as pdf_file:
                    st.session_state.pdf_bytes = pdf_file.read()

                st.success(
                    "Client report generated successfully."
                )

            if "pdf_bytes" in st.session_state:

                st.download_button(
                    label="Download Client Report",
                    data=st.session_state.pdf_bytes,
                    file_name=(
                        f"{company_name}_Hidden_Profit_Report.pdf"
                    ),
                    mime="application/pdf",
                    use_container_width=True
                )

        else:
            st.info(
                "Upload a CSV containing Month, Revenue, and Expenses."
            )            
