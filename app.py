import streamlit as st
import resend

resend.api_key = st.secrets["RESEND_API_KEY"]

import pandas as pd

from assignment_optimizer import run_assignment_optimizer
from set_covering_optimizer import run_set_covering_optimizer
from facility_location_optimizer import run_facility_location_optimizer
from transportation_optimizer import run_transportation_optimizer
from scheduling_optimizer import run_scheduling_optimizer
from resource_allocation_optimizer import run_resource_allocation_optimizer

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

if "hpa_page" not in st.session_state:
    st.session_state.hpa_page = "home"

if "profit_guide_step" not in st.session_state:
    st.session_state.profit_guide_step = 1

if "assignment_guide_step" not in st.session_state:
    st.session_state.assignment_guide_step = 1

if "set_covering_guide_step" not in st.session_state:
    st.session_state.set_covering_guide_step = 1

if "facility_guide_step" not in st.session_state:
    st.session_state.facility_guide_step = 1

if "transportation_guide_step" not in st.session_state:
    st.session_state.transportation_guide_step = 1

if "scheduling_guide_step" not in st.session_state:
    st.session_state.scheduling_guide_step = 1

if "resource_allocation_guide_step" not in st.session_state:
    st.session_state.resource_allocation_guide_step = 1

st.set_page_config(
    page_title="Hidden Profit Analytics",
    layout="wide",
)

st.sidebar.title("Hidden Profit Analytics")

tool_page_map = {
    "profit_analyzer": "Profit Analyzer",
    "assignment_analyzer": "Assignment Optimizer",
    "set_covering_analyzer": "Set Covering Optimizer",
    "facility_analyzer": "Facility Location Optimizer",
    "transportation_analyzer": "Transportation Optimizer",
    "scheduling_analyzer": "Scheduling Optimizer",
    "resource_allocation_analyzer": "Resource Allocation Optimizer",
}

tool = tool_page_map.get(st.session_state.hpa_page)

guided_mode = st.sidebar.toggle(
    "Guided Mode",
    value=True,
    help="Show step-by-step guidance while using Hidden Profit Analytics."
)

if guided_mode:
    st.sidebar.caption(
        "Guided Mode is on. The app will show the next recommended step as you work."
    )

st.sidebar.divider()

st.sidebar.caption(
    "Testing Hidden Profit Analytics? Your feedback helps improve the platform."
)

st.sidebar.link_button(
    "Give Beta Feedback",
    "https://forms.gle/Q8Ey4TB6jYM3Yo6a6",
    use_container_width=True
)

st.info(
    "Private Beta: Hidden Profit Analytics is currently being tested with a limited group of users. "
    "Please upload only business data you are authorized to use. "
    "Results are provided for decision-support purposes and should not be considered accounting, legal, tax, or financial advice."
)

with st.expander("Beta Tester Quick Start", expanded=False):
    st.markdown(
        """
1. **Choose a tool** that matches the business decision you want to improve.

2. **Use Guided Mode** if you would like step-by-step help while working through the tool.

3. **Download the provided CSV template or templates** for the selected tool.

4. **Replace the sample values with your own business data** and save the completed CSV file or files.

5. **Upload the completed data files.** Hidden Profit Analytics will validate your inputs before running the optimization.

6. **Review the recommendation and results**, including potential savings, profit improvement, assignment changes, or other suggested actions.

7. When you are finished testing, click **Give Beta Feedback** in the sidebar and tell us about your experience.
        """
    )

st.caption(
    "Data handling: Uploaded CSV data is used within the active app session to perform the analysis. "
    "Hidden Profit Analytics does not intentionally save uploaded CSV files to the application repository. "
    "Generated PDF reports are created temporarily for download."
)

if st.session_state.hpa_page == "home":
    st.title("Hidden Profit Analytics")

    st.header("What are you trying to figure out?")

    st.write(
        "Tell Hidden Profit Analytics about your business challenge, "
        "and we'll guide you to your optimal decision."
    )

    st.subheader("💰 I want to improve my profit.")

    if st.button("Explore this option →", key="explore_profit"):
        st.session_state.hpa_page = "profit_guidance"
        st.rerun()

    st.subheader("👥 I want to use my people and resources more efficiently.")

    if st.button("Explore this option →", key="explore_people_resources"):
        st.session_state.hpa_page = "people_resources_guidance"
        st.rerun()

if st.session_state.hpa_page == "people_resources_guidance":
    st.header("👥 Let's use your people and resources more efficiently")

    st.subheader("What are you trying to improve?")

    people_resource_need = st.radio(
        "Choose the option that best describes your situation:",
        [
            "I need to decide who or what should be assigned to each job or task",
            "I need to build a better employee schedule",
            "I have limited people, time, money, or equipment and need to decide where to use them",
            "I'm not sure which of these best fits my situation",
        ],
        index=None,
        key="people_resource_need"
    )

    if st.button(
        "Continue →",
        disabled=people_resource_need is None,
        key="people_resource_need_continue"
    ):
        st.session_state.hpa_page = "people_resources_goal"
        st.rerun()

if st.session_state.hpa_page == "people_resources_goal":
    st.header("👥 Let's use your people and resources more efficiently")

    st.subheader("What would you like HPA to help you determine?")

    people_resource_goal = st.radio(
        "Choose the option that best matches what you want to accomplish:",
        [
            "Which person, team, or resource should handle each job or task",
            "How to create a lower-cost employee schedule while meeting staffing needs",
            "Where to allocate limited people, time, money, or equipment for the greatest value",
            "I'm not sure — help me determine the best approach",
        ],
        index=None,
        key="people_resource_goal"
    )

    if st.button(
        "Continue →",
        disabled=people_resource_goal is None,
        key="people_resource_goal_continue"
    ):
        if people_resource_goal == "I'm not sure — help me determine the best approach":
            st.session_state.hpa_page = "people_resources_clarify"
        else:
            st.session_state.hpa_page = "people_resources_recommendation"

        st.rerun()

if st.session_state.hpa_page == "people_resources_clarify":
    st.header("👥 Let's narrow this down")

    st.subheader("Which of these sounds most like the decision you're facing?")

    people_resource_clarify = st.radio(
        "Choose the option that comes closest:",
        [
            "I have several people or resources and need to decide who should handle which work",
            "I need enough employees working at the right times without spending more than necessary",
            "I have limited resources and several competing priorities",
            "None of these quite describe my situation",
        ],
        index=None,
        key="people_resource_clarify"
    )

    if st.button(
        "Continue →",
        disabled=people_resource_clarify is None,
        key="people_resource_clarify_continue"
    ):
        if people_resource_clarify == "I have several people or resources and need to decide who should handle which work":
            st.session_state.people_resource_goal = "Which person, team, or resource should handle each job or task"
            st.session_state.hpa_page = "people_resources_recommendation"

        elif people_resource_clarify == "I need enough employees working at the right times without spending more than necessary":
            st.session_state.people_resource_goal = "How to create a lower-cost employee schedule while meeting staffing needs"
            st.session_state.hpa_page = "people_resources_recommendation"

        elif people_resource_clarify == "I have limited resources and several competing priorities":
            st.session_state.people_resource_goal = "Where to allocate limited people, time, money, or equipment for the greatest value"
            st.session_state.hpa_page = "people_resources_recommendation"

        else:
            st.session_state.hpa_page = "custom_decision"

        st.rerun()

if st.session_state.hpa_page == "people_resources_recommendation":
    st.header("💡 Your Decision Guidance")

    if st.session_state.people_resource_goal == "Which person, team, or resource should handle each job or task":
        st.subheader(
            "HPA can help you determine the most cost-effective way "
            "to assign people or resources to jobs and tasks."
        )

        st.write(
            "We'll compare the available assignment options and their costs "
            "to identify which person, team, or resource should handle each job "
            "while minimizing total assignment cost."
        )

        st.info(
            "**Recommended next step:** Analyze your assignment options "
            "to identify the most efficient allocation."
        )

    elif st.session_state.people_resource_goal == "How to create a lower-cost employee schedule while meeting staffing needs":
        st.subheader(
            "HPA can help you build a lower-cost employee schedule "
            "while still meeting your staffing needs."
        )

        st.write(
            "We'll evaluate staffing requirements, employee availability, "
            "and scheduling costs to determine a schedule that provides "
            "the coverage you need at the lowest practical cost."
        )

        st.info(
            "**Recommended next step:** Analyze your staffing needs, "
            "employee availability, and scheduling costs to identify "
            "a more efficient schedule."
        )

    elif st.session_state.people_resource_goal == "Where to allocate limited people, time, money, or equipment for the greatest value":
        st.subheader(
            "HPA can help you determine where your limited resources "
            "can create the greatest business value."
        )

        st.write(
            "We'll evaluate the opportunities competing for your available "
            "people, time, budget, or equipment and determine how those resources "
            "can be allocated to produce the greatest overall value."
        )

        st.info(
            "**Recommended next step:** Analyze your available resources, "
            "constraints, and competing opportunities to identify the strongest allocation."
        )

if st.session_state.hpa_page == "custom_decision":
    st.header("💡 Your situation may need a closer look")

    st.write(
        "Not every business decision fits neatly into one category. "
        "Tell Hidden Profit Analytics a little more about the decision "
        "you're trying to make, and we'll help determine the best next step."
    )

    custom_decision_text = st.text_area(
        "What are you trying to figure out?",
        placeholder="Describe the business decision, problem, or situation in your own words.",
        key="custom_decision_text"
    )

    custom_email = st.text_input(
        "Email address *",
        placeholder="you@example.com",
        key="custom_email"
    )

    custom_phone = st.text_input(
        "Phone number (optional)",
        placeholder="(555) 123-4567",
        key="custom_phone"
    )

    preferred_contact = st.radio(
        "How would you prefer HPA to follow up?",
        [
            "Email",
            "Text message",
            "Voice call",
        ],
        index=None,
        key="preferred_contact"
    )

    contact_consent = st.checkbox(
        "I agree that Hidden Profit Analytics may contact me about this submission.",
        key="custom_contact_consent"
    )

    phone_required = preferred_contact in ["Text message", "Voice call"]

    form_ready = (
        custom_decision_text.strip()
        and custom_email.strip()
        and preferred_contact is not None
        and (not phone_required or custom_phone.strip())
        and contact_consent
    )

    if st.button(
        "Submit my decision →",
        disabled=not form_ready,
        key="custom_decision_continue"
    ):
        try:
            resend.Emails.send(
                {
                    "from": "Hidden Profit Analytics <decisions@hiddenprofitanalytics.com>",
                    "to": ["lisamariewyldhart@gmail.com"],
                    "subject": "New Hidden Profit Analytics Decision Submission",
                    "text": (
                        f"Decision submitted:\n\n"
                        f"{custom_decision_text}\n\n"
                        f"Email: {custom_email}\n"
                        f"Phone: {custom_phone if custom_phone.strip() else 'Not provided'}\n"
                        f"Preferred follow-up: {preferred_contact}\n"
                        f"Contact consent: Yes"
                    ),
                }
            )

            st.session_state.hpa_page = "custom_decision_confirmation"
            st.rerun()

        except Exception as e:
            st.error(
                "We couldn't submit your decision right now. "
                "Please try again or contact Hidden Profit Analytics directly."
            )

if st.session_state.hpa_page == "custom_decision_confirmation":
    st.header("✅ Thanks — your decision has been submitted")

    st.write(
        "Hidden Profit Analytics has received your submission. "
        "We'll review the situation you described and follow up using your preferred contact method."
    )

if st.session_state.hpa_page == "profit_guidance":
    st.header("💰 Let's improve your profit")

    st.subheader("What are you most concerned about?")

    profit_concern = st.radio(
        "Choose the option that best describes your situation:",
        [
            "My expenses are too high",
            "My revenue isn't high enough",
            "My profit margin is lower than I'd like",
            "I want to know whether increasing revenue or reducing expenses would help more",
            "I'm not sure where the problem is",
        ],
        index=None,
        key="profit_concern"
    )

    if st.button(
        "Continue →",
        disabled=profit_concern is None,
        key="profit_concern_continue"
    ):
        st.session_state.hpa_page = "profit_goal"
        st.rerun()

if st.session_state.hpa_page == "profit_goal":
    st.header("💰 Let's improve your profit")

    st.subheader("What would you like HPA to help you determine?")

    profit_goal = st.radio(
        "Choose the option that best matches what you want to accomplish:",
        [
            "Where I have the greatest opportunity to improve profit",
            "How much I would need to increase revenue",
            "How much I would need to reduce expenses",
            "What combination of revenue growth and expense reduction would work best",
            "I'm not sure — help me determine the best approach",
        ],
        index=None,
        key="profit_goal"
    )

    if st.button(
        "Continue →",
        disabled=profit_goal is None,
        key="profit_goal_continue"
    ):
        st.session_state.hpa_page = "profit_recommendation"
        st.rerun()

if st.session_state.hpa_page == "profit_recommendation":
    st.header("💡 Your Decision Guidance")

    st.subheader(
        "HPA can help you identify where your greatest "
        "profit improvement opportunity may be."
    )

    st.write(
        "We'll compare the impact of reducing expenses, increasing revenue, "
        "or using a combination of both based on your business data. "
        "Then HPA can help determine which approach provides the strongest "
        "opportunity for improving your profit."
    )

    st.info(
        "**Recommended next step:** Analyze your current revenue and expenses "
        "to identify your strongest profit improvement opportunity."
    )

    if st.button("Start My Analysis →", key="start_profit_analysis"):
        st.session_state.hpa_page = "profit_analyzer"
        st.rerun()

if tool == "Assignment Optimizer":
    st.header("Assignment Optimizer")

    st.write(
        "Find the lowest-cost assignment of employees, resources, "
        "or teams to tasks while comparing the optimized solution "
        "to the current assignment."
    )

    assignment_step1_placeholder = st.empty()

    if (
        guided_mode
        and st.session_state.assignment_guide_step == 1
    ):
        assignment_step1_placeholder.info(
            "⬇️ **Step 1 of 3 — Prepare Your Assignment Data**\n\n"
            "Download the CSV template below, replace the sample data "
            "with your own assignments and costs, then save the completed file."
        )

    assignment_template = pd.DataFrame(
    {
        "Employee": [
            "Alice", "Alice", "Alice",
            "Bob", "Bob", "Bob",
            "Carla", "Carla", "Carla"
        ],
        "Task": [
            "Task 1", "Task 2", "Task 3",
            "Task 1", "Task 2", "Task 3",
            "Task 1", "Task 2", "Task 3"
        ],
        "Cost": [
            18, 24, 16,
            20, 15, 22,
            14, 19, 17
        ],
        "CurrentAssignment": [
            1, 0, 0,
            0, 0, 1,
            0, 1, 0
        ]
    }
)

    st.download_button(
        label="Download Assignment CSV Template",
        data=assignment_template.to_csv(index=False),
        file_name="assignment_template.csv",
        mime="text/csv"
    )

    with st.expander("How to format your Assignment data"):
        st.markdown(
            """
            - **Employee**: Name of the employee, team, machine, or resource.
            - **Task**: Name of the task, job, project, or customer.
            - **Cost**: Cost of assigning that resource to that task.
            - **CurrentAssignment**: Enter `1` if this is the current assignment, otherwise `0`.

            Each employee-task combination should appear once.
            Every task must have exactly one current assignment.
            """
        )

    assignment_file = st.file_uploader(
        "Upload Assignment Data CSV",
        type=["csv"],
        key="assignment_upload"
    )

    assignment_guide_placeholder = st.empty()

    if (
        guided_mode
        and st.session_state.assignment_guide_step == 2
    ):
        assignment_guide_placeholder.info(
            "⬇️ **Step 2 of 3 — Review Your Optimization Results**\n\n"
            "Your file has been uploaded. Hidden Profit Analytics will "
            "validate the data and calculate the lowest-cost assignment below."
        )

    elif (
        guided_mode
        and st.session_state.assignment_guide_step == 3
    ):
        assignment_guide_placeholder.success(
            "✅ **Step 3 of 3 — Review the Recommendation**\n\n"
            "Your optimization is complete. Review the recommended assignments, "
            "potential savings, and assignment changes below."
        )

    if assignment_file is not None:
        try:
            results = run_assignment_optimizer(assignment_file)
            if guided_mode:
                st.session_state.assignment_guide_step = 3

                assignment_step1_placeholder.empty()

                assignment_guide_placeholder.success(
                    "✅ **Step 3 of 3 — Review the Recommendation**\n\n"
                    "Your optimization is complete. Review the recommended assignments, "
                    "potential savings, and assignment changes below."
                )
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
            changed_rows = results["comparison"][
                results["comparison"]["Changed"] == True
            ]

            if results["savings"] > 0:
                change_text = []

                for _, row in changed_rows.iterrows():
                    change_text.append(
                        f"{row['Employee']} from "
                        f"{row['CurrentTask']} to "
                        f"{row['OptimizedTask']}"
                    )

                if change_text:
                    recommendation_text = (
                        "Recommended action: Reassign "
                        + "; ".join(change_text)
                        + f". This reduces estimated assignment cost by "
                        f"${results['savings']:,.2f}, or "
                        f"{results['savings_percent']:.2f}%."
                    )
                else:
                    recommendation_text = (
                        "Recommended action: Keep the current assignments. "
                        "No assignment changes are required."
                    )

                st.info(recommendation_text)

            else:
                st.info(
                    "Recommended action: Keep the current assignments. "
                    "The optimizer did not identify a lower-cost assignment."
                )

            assignments_display = results["assignments"].rename(
            columns={
                "Employee": "Employee",
                "Task": "Recommended Task",
                "Cost": "Assignment Cost"
            }
        )

            comparison_display = results["comparison"].rename(
                columns={
                    "Employee": "Employee",
                    "CurrentTask": "Current Task",
                    "CurrentCost": "Current Cost",
                    "OptimizedTask": "Recommended Task",
                    "OptimizedCost": "Recommended Cost",
                    "Changed": "Assignment Changed"
                }
            )

            st.dataframe(
                assignments_display,
                use_container_width=True
            )

            st.subheader("Assignment Changes")

            st.dataframe(
                comparison_display,
                use_container_width=True
            )

        except Exception as error:
            if guided_mode:
                st.session_state.assignment_guide_step = 2

                assignment_step1_placeholder.empty()

                assignment_guide_placeholder.info(
                    "⬇️ **Step 2 of 3 — Correct Your Assignment Data**\n\n"
                    "The uploaded file needs to be corrected before the optimization "
                    "can continue. Review the error below, update your CSV, and upload "
                    "the corrected file."
                )

            st.error(str(error))

if tool == "Set Covering Optimizer":
    st.header("Set Covering Optimizer")

    st.write(
        "Choose the minimum-cost set of locations, options, or resources "
        "needed to cover every required area at least once."
    )

    set_covering_step1_placeholder = st.empty()

    if (
        guided_mode
        and st.session_state.set_covering_guide_step == 1
    ):
        set_covering_step1_placeholder.info(
            "⬇️ **Step 1 of 3 — Prepare Your Coverage Data**\n\n"
            "Download the CSV template below, replace the sample options, costs, "
            "and coverage values with your own data, then save the completed file."
        )

    set_covering_template = pd.DataFrame(
        {
            "Option": [
                "Location 1",
                "Location 2",
                "Location 3",
                "Location 4"
            ],
            "Cost": [
                1200,
                1500,
                1100,
                1700
            ],
            "CurrentSelected": [
                1,
                1,
                1,
                1
            ],
            "Zone A": [
                1,
                0,
                0,
                1
            ],
            "Zone B": [
                1,
                1,
                0,
                0
            ],
            "Zone C": [
                0,
                1,
                1,
                0
            ],
            "Zone D": [
                0,
                1,
                0,
                1
            ],
            "Zone E": [
                0,
                0,
                1,
                1
            ]
        }
    )

    st.download_button(
        label="Download Set Covering CSV Template",
        data=set_covering_template.to_csv(index=False),
        file_name="set_covering_template.csv",
        mime="text/csv"
    )

    with st.expander("How to format your Set Covering data"):
        st.markdown(
            """
            - **Option**: Name of the location, service option, resource, supplier, or other choice.
            - **Cost**: Cost of selecting that option.
            - **CurrentSelected**: Enter `1` if the option is currently being used, otherwise `0`.
            - **Coverage columns**: Add one column for each required location, customer group, route, time period, or item that must be covered.
            - Enter `1` when an option covers that requirement and `0` when it does not.

            Every required coverage column must be covered by at least one option.
            """
        )

    set_covering_file = st.file_uploader(
        "Upload Set Covering Data CSV",
        type=["csv"],
        key="set_covering_upload"
    )

    if (
        guided_mode
        and set_covering_file is not None
        and st.session_state.set_covering_guide_step == 1
    ):
        st.session_state.set_covering_guide_step = 2
        st.rerun()

    set_covering_guide_placeholder = st.empty()

    if (
        guided_mode
        and st.session_state.set_covering_guide_step == 2
    ):
        set_covering_guide_placeholder.info(
            "⬇️ **Step 2 of 3 — Review Your Optimization Results**\n\n"
            "Your file has been uploaded. Hidden Profit Analytics will validate "
            "the data and calculate the lowest-cost coverage plan below."
        )

    if set_covering_file is not None:
        try:
            results = run_set_covering_optimizer(set_covering_file)

            if guided_mode:
                st.session_state.set_covering_guide_step = 3

                set_covering_guide_placeholder.success(
                    "✅ **Step 3 of 3 — Review the Recommendation**\n\n"
                    "Your optimization is complete. Review the recommended options, "
                    "potential savings, and configuration changes below."
                )

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

            comparison = results["comparison"]

            to_add = comparison[
                comparison["Recommendation"] == "Add"
            ]["Option"].tolist()

            to_keep = comparison[
                comparison["Recommendation"] == "Keep"
            ]["Option"].tolist()

            to_remove = comparison[
                comparison["Recommendation"] == "Remove"
            ]["Option"].tolist()

            action_parts = []

            if to_keep:
                action_parts.append(
                    "keep " + ", ".join(to_keep)
                )

            if to_add:
                action_parts.append(
                    "add " + ", ".join(to_add)
                )

            if to_remove:
                action_parts.append(
                    "remove " + ", ".join(to_remove)
                )

            if results["savings"] > 0:
                if action_parts:
                    recommendation_text = (
                        "Recommended action: "
                        + "; ".join(action_parts)
                        + f". This reduces estimated total cost by "
                        f"${results['savings']:,.2f}, or "
                        f"{results['savings_percent']:.2f}%."
                    )
                else:
                    recommendation_text = (
                        "Recommended action: Keep the current configuration. "
                        "No changes are required."
                    )

                st.info(recommendation_text)

            else:
                st.info(
                    "Recommended action: Keep the current configuration. "
                    "The optimizer did not identify a lower-cost set of options."
                )

            selected_options_display = results["selected_options"].rename(
                columns={
                    "Option": "Option",
                    "Cost": "Selected Cost"
                }
            )

            comparison_display = results["comparison"].rename(
                columns={
                    "Option": "Option",
                    "Cost": "Cost",
                    "CurrentSelected": "Currently Selected",
                    "OptimizedSelected": "Recommended",
                    "Recommendation": "Action"
                }
            )

            st.dataframe(
                selected_options_display,
                use_container_width=True
            )

            st.subheader("Configuration Changes")

            st.dataframe(
                comparison_display,
                use_container_width=True
            )

        except Exception as error:
            if guided_mode:
                st.session_state.set_covering_guide_step = 2

                set_covering_guide_placeholder.info(
                    "⬇️ **Step 2 of 3 — Correct Your Set Covering Data**\n\n"
                    "The uploaded file needs to be corrected before the optimization "
                    "can continue. Review the error below, update your CSV, and upload "
                    "the corrected file."
                )

            st.error(str(error))

if tool == "Facility Location Optimizer":
    st.header("Facility Location Optimizer")

    st.write(
        "Determine which facilities should remain open, close, or open, "
        "and how customers should be assigned to minimize total cost."
    )

    facility_guide_placeholder = st.empty()

    if (
        guided_mode
        and st.session_state.facility_guide_step == 1
    ):
        facility_guide_placeholder.info(
            "⬇️ **Step 1 of 3 — Prepare Your Facility Location Data**\n\n"
            "Download both CSV templates below. Replace the sample values "
            "with your facility costs, customer service costs, customer demand, "
            "and current assignments, then save both completed files."
        )

    facility_location_template = pd.DataFrame(
        {
            "Facility": [
                "Facility 1",
                "Facility 2",
                "Facility 3"
            ],
            "FixedCost": [
                4000,
                5500,
                3500
            ],
            "CurrentOpen": [
                1,
                1,
                0
            ],
            "Customer A": [
                8,
                14,
                20
            ],
            "Customer B": [
                12,
                9,
                16
            ],
            "Customer C": [
                18,
                11,
                10
            ],
            "Customer D": [
                24,
                17,
                8
            ]
        }
    )

    facility_demand_template = pd.DataFrame(
        {
            "Customer": [
                "Customer A",
                "Customer B",
                "Customer C",
                "Customer D"
            ],
            "Demand": [
                1000,
                800,
                1200,
                900
            ],
            "CurrentFacility": [
                "Facility 1",
                "Facility 2",
                "Facility 2",
                "Facility 2"
            ]
        }
    )

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Download Facility Cost Template",
            data=facility_location_template.to_csv(index=False),
            file_name="facility_location_template.csv",
            mime="text/csv"
        )

    with col2:
        st.download_button(
            label="Download Customer Demand Template",
            data=facility_demand_template.to_csv(index=False),
            file_name="facility_demand_template.csv",
            mime="text/csv"
        )

    with st.expander("How to format your Facility Location data"):
        st.markdown(
            """
            **Facility Cost File**

            - **Facility**: Name of the candidate facility.
            - **FixedCost**: Fixed cost of operating that facility.
            - **CurrentOpen**: Enter `1` if the facility is currently open, otherwise `0`.
            - **Customer columns**: Enter the per-unit service or transportation cost from each facility to each customer.

            **Customer Demand File**

            - **Customer**: Customer, market, region, or demand zone name.
            - **Demand**: Required demand volume for that customer or zone.
            - **CurrentFacility**: Facility currently serving that customer.

            Customer names must match the customer column names in the Facility Cost file.
            Facility names in `CurrentFacility` must match the names in the Facility Cost file.
            """
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

    if (
        guided_mode
        and (facility_file is not None or demand_file is not None)
        and st.session_state.facility_guide_step == 1
    ):
        st.session_state.facility_guide_step = 2
        st.rerun()

    if (
        guided_mode
        and st.session_state.facility_guide_step == 2
    ):
        if facility_file is not None and demand_file is not None:
            facility_guide_placeholder.info(
                "⬇️ **Step 2 of 3 — Review Your Optimization Results**\n\n"
                "Both files have been uploaded. Hidden Profit Analytics will validate "
                "the data and calculate the lowest-cost facility configuration below."
            )
        else:
            facility_guide_placeholder.info(
                "⬇️ **Step 2 of 3 — Upload Both Data Files**\n\n"
                "Upload both your completed Facility Cost and Customer Demand CSV files "
                "to continue."
            )

    if facility_file is not None and demand_file is not None:
        try:
            results = run_facility_location_optimizer(
                facility_file,
                demand_file
            )

            if guided_mode:
                st.session_state.facility_guide_step = 3

                facility_guide_placeholder.success(
                    "✅ **Step 3 of 3 — Review the Recommendation**\n\n"
                    "Your optimization is complete. Review which facilities should "
                    "open, close, or remain open, the customer assignment changes, "
                    "and the potential savings below."
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

            facility_comparison = results["facility_comparison"]
            assignment_comparison = results["assignment_comparison"]

            keep_open = facility_comparison[
                facility_comparison["Recommendation"] == "Keep Open"
            ]["Facility"].tolist()

            to_open = facility_comparison[
                facility_comparison["Recommendation"] == "Open"
            ]["Facility"].tolist()

            to_close = facility_comparison[
                facility_comparison["Recommendation"] == "Close"
            ]["Facility"].tolist()

            changed_customers = assignment_comparison[
                assignment_comparison["Changed"] == True
            ]

            action_parts = []

            if keep_open:
                action_parts.append(
                    "keep " + ", ".join(keep_open) + " open"
                )

            if to_open:
                action_parts.append(
                    "open " + ", ".join(to_open)
                )

            if to_close:
                action_parts.append(
                    "close " + ", ".join(to_close)
                )

            customer_changes = []

            for _, row in changed_customers.iterrows():
                customer_changes.append(
                    f"{row['Customer']} from "
                    f"{row['CurrentFacility']} to "
                    f"{row['OptimizedFacility']}"
                )

            if results["savings"] > 0:
                recommendation_text = (
                    "Recommended action: "
                    + "; ".join(action_parts)
                    + "."
                )

                if customer_changes:
                    recommendation_text += (
                        " Reassign "
                        + "; ".join(customer_changes)
                        + "."
                    )

                recommendation_text += (
                    f" This reduces estimated total cost by "
                    f"${results['savings']:,.2f}, or "
                    f"{results['savings_percent']:.2f}%."
                )

                st.info(recommendation_text)

            else:
                st.info(
                    "Recommended action: Keep the current facility "
                    "configuration. The optimizer did not identify "
                    "a lower-cost facility network."
                )

            st.subheader("Facility Recommendations")

            facility_display = results["facility_comparison"].rename(
                columns={
                    "Facility": "Facility",
                    "FixedCost": "Fixed Cost",
                    "CurrentOpen": "Currently Open",
                    "OptimizedOpen": "Recommended Open",
                    "Recommendation": "Action"
                }
            )

            assignment_display = results["assignment_comparison"].rename(
                columns={
                    "Customer": "Customer",
                    "Demand": "Demand",
                    "CurrentFacility": "Current Facility",
                    "OptimizedFacility": "Recommended Facility",
                    "Changed": "Assignment Changed"
                }
            )

            st.dataframe(
                facility_display,
                use_container_width=True
            )

            st.subheader("Customer Assignment Changes")

            st.dataframe(
                assignment_display,
                use_container_width=True
            )

        except Exception as error:
            if guided_mode:
                st.session_state.facility_guide_step = 2

                facility_guide_placeholder.info(
                    "⬇️ **Step 2 of 3 — Correct Your Facility Location Data**\n\n"
                    "The uploaded files need to be corrected before the optimization "
                    "can continue. Review the error below, update the affected CSV, "
                    "and upload the corrected file."
                )

            st.error(str(error))

if tool == "Transportation Optimizer":
    st.header("Transportation Optimizer")

    st.write(
        "Determine how much should be shipped from each source to each "
        "destination to satisfy demand at the lowest total transportation cost."
    )

    transportation_guide_placeholder = st.empty()

    if (
        guided_mode
        and st.session_state.transportation_guide_step == 1
    ):
        transportation_guide_placeholder.info(
            "⬇️ **Step 1 of 3 — Prepare Your Transportation Data**\n\n"
            "Download all four CSV templates below. Replace the sample values "
            "with your transportation costs, available supply, destination demand, "
            "and current shipping plan, then save all four completed files."
        )

    transportation_costs_template = pd.DataFrame(
        {
            "Source": [
                "Warehouse 1",
                "Warehouse 2"
            ],
            "Destination A": [
                4,
                5
            ],
            "Destination B": [
                6,
                3
            ],
            "Destination C": [
                8,
                7
            ]
        }
    )

    transportation_supply_template = pd.DataFrame(
        {
            "Source": [
                "Warehouse 1",
                "Warehouse 2"
            ],
            "Supply": [
                120,
                100
            ]
        }
    )

    transportation_demand_template = pd.DataFrame(
        {
            "Destination": [
                "Destination A",
                "Destination B",
                "Destination C"
            ],
            "Demand": [
                80,
                70,
                60
            ]
        }
    )

    transportation_current_template = pd.DataFrame(
        {
            "Source": [
                "Warehouse 1",
                "Warehouse 1",
                "Warehouse 1",
                "Warehouse 2",
                "Warehouse 2",
                "Warehouse 2"
            ],
            "Destination": [
                "Destination A",
                "Destination B",
                "Destination C",
                "Destination A",
                "Destination B",
                "Destination C"
            ],
            "Quantity": [
                70,
                20,
                30,
                10,
                50,
                30
            ]
        }
    )

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.download_button(
            label="Download Transportation Cost Template",
            data=transportation_costs_template.to_csv(index=False),
            file_name="transportation_costs_template.csv",
            mime="text/csv"
        )

    with row1_col2:
        st.download_button(
            label="Download Supply Template",
            data=transportation_supply_template.to_csv(index=False),
            file_name="transportation_supply_template.csv",
            mime="text/csv"
        )

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.download_button(
            label="Download Demand Template",
            data=transportation_demand_template.to_csv(index=False),
            file_name="transportation_demand_template.csv",
            mime="text/csv"
        )

    with row2_col2:
        st.download_button(
            label="Download Current Shipping Template",
            data=transportation_current_template.to_csv(index=False),
            file_name="transportation_current_template.csv",
            mime="text/csv"
        )

    with st.expander("How to format your Transportation data"):
        st.markdown(
            """
            **Transportation Cost File**

            - **Source**: Name of the warehouse, plant, supplier, or shipping origin.
            - **Destination columns**: Enter the per-unit shipping cost from each source to each destination.

            **Supply File**

            - **Source**: Must match the source names in the Transportation Cost file.
            - **Supply**: Maximum quantity available from each source.

            **Demand File**

            - **Destination**: Must match the destination column names in the Transportation Cost file.
            - **Demand**: Quantity required at each destination.

            **Current Shipping Plan File**

            - **Source**: Shipping origin.
            - **Destination**: Shipping destination.
            - **Quantity**: Current quantity shipped on that route.

            Total available supply must be sufficient to meet total demand.
            Source and destination names must match across all files.
            """
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
        guided_mode
        and any(
            file is not None
            for file in [
                cost_file,
                supply_file,
                demand_file,
                current_file
            ]
        )
        and st.session_state.transportation_guide_step == 1
    ):
        st.session_state.transportation_guide_step = 2
        st.rerun()

    if (
        guided_mode
        and st.session_state.transportation_guide_step == 2
    ):
        all_transportation_files_uploaded = all(
            file is not None
            for file in [
                cost_file,
                supply_file,
                demand_file,
                current_file
            ]
        )

        if all_transportation_files_uploaded:
            transportation_guide_placeholder.info(
                "⬇️ **Step 2 of 3 — Review Your Optimization Results**\n\n"
                "All four files have been uploaded. Hidden Profit Analytics will "
                "validate the data and calculate the lowest-cost shipping plan below."
            )
        else:
            transportation_guide_placeholder.info(
                "⬇️ **Step 2 of 3 — Upload All Four Data Files**\n\n"
                "Upload your completed Transportation Cost, Supply, Demand, "
                "and Current Shipping Plan CSV files to continue."
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

            if guided_mode:
                st.session_state.transportation_guide_step = 3

                transportation_guide_placeholder.success(
                    "✅ **Step 3 of 3 — Review the Recommendation**\n\n"
                    "Your optimization is complete. Review the recommended shipping plan, "
                    "route changes, and potential savings below."
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

            shipment_comparison = results["shipment_comparison"]

            changed_routes = shipment_comparison[
                shipment_comparison["Change"] != 0
            ]

            route_changes = []

            for _, row in changed_routes.iterrows():
                if row["Change"] > 0:
                    route_changes.append(
                        f"increase {row['Source']} to "
                        f"{row['Destination']} by "
                        f"{row['Change']:,.0f} units"
                    )
                else:
                    route_changes.append(
                        f"decrease {row['Source']} to "
                        f"{row['Destination']} by "
                        f"{abs(row['Change']):,.0f} units"
                    )

            if results["savings"] > 0:
                recommendation_text = (
                    "Recommended action: "
                    + "; ".join(route_changes)
                    + f". This reduces estimated transportation cost by "
                    f"${results['savings']:,.2f}, or "
                    f"{results['savings_percent']:.2f}%."
                )

                st.info(recommendation_text)

            else:
                st.info(
                    "Recommended action: Keep the current shipping plan. "
                    "The optimizer did not identify a lower-cost transportation plan."
                )

            st.subheader("Shipment Changes")

            shipment_display = results["shipment_comparison"].rename(
                columns={
                    "Source": "Source",
                    "Destination": "Destination",
                    "CurrentQuantity": "Current Quantity",
                    "OptimizedQuantity": "Recommended Quantity",
                    "Change": "Quantity Change",
                    "UnitCost": "Unit Cost"
                }
            )

            st.dataframe(
                shipment_display,
                use_container_width=True
            )

        except Exception as error:
            if guided_mode:
                st.session_state.transportation_guide_step = 2

                transportation_guide_placeholder.info(
                    "⬇️ **Step 2 of 3 — Correct Your Transportation Data**\n\n"
                    "The uploaded files need to be corrected before the optimization "
                    "can continue. Review the error below, update the affected CSV, "
                    "and upload the corrected file."
                )

            st.error(str(error))

if tool == "Scheduling Optimizer":
    st.header("Scheduling Optimizer")

    st.write(
        "Build a minimum-cost employee schedule while meeting staffing "
        "requirements and respecting employee availability."
    )

    scheduling_guide_placeholder = st.empty()

    if (
        guided_mode
        and st.session_state.scheduling_guide_step == 1
    ):
        scheduling_guide_placeholder.info(
            "⬇️ **Step 1 of 3 — Prepare Your Scheduling Data**\n\n"
            "Download all four CSV templates below. Replace the sample values "
            "with your employee scheduling costs, staffing requirements, "
            "availability, and current schedule, then save all four completed files."
        )

    scheduling_costs_template = pd.DataFrame(
        {
            "Employee": [
                "Alice",
                "Bob",
                "Carla",
                "David"
            ],
            "Shift 1": [
                120,
                110,
                135,
                100
            ],
            "Shift 2": [
                140,
                150,
                125,
                155
            ],
            "Shift 3": [
                160,
                130,
                145,
                150
            ]
        }
    )

    scheduling_requirements_template = pd.DataFrame(
        {
            "Shift": [
                "Shift 1",
                "Shift 2",
                "Shift 3"
            ],
            "RequiredEmployees": [
                2,
                1,
                1
            ]
        }
    )

    scheduling_availability_template = pd.DataFrame(
        {
            "Employee": [
                "Alice",
                "Bob",
                "Carla",
                "David"
            ],
            "Shift 1": [
                1,
                1,
                0,
                1
            ],
            "Shift 2": [
                1,
                0,
                1,
                1
            ],
            "Shift 3": [
                1,
                1,
                1,
                0
            ]
        }
    )

    scheduling_current_template = pd.DataFrame(
        {
            "Employee": [
                "Alice",
                "Bob",
                "Carla",
                "David"
            ],
            "Shift": [
                "Shift 2",
                "Shift 1",
                "Shift 3",
                "Shift 1"
            ]
        }
    )

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.download_button(
            label="Download Scheduling Cost Template",
            data=scheduling_costs_template.to_csv(index=False),
            file_name="scheduling_costs_template.csv",
            mime="text/csv"
        )

    with row1_col2:
        st.download_button(
            label="Download Staffing Requirements Template",
            data=scheduling_requirements_template.to_csv(index=False),
            file_name="scheduling_requirements_template.csv",
            mime="text/csv"
        )

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.download_button(
            label="Download Availability Template",
            data=scheduling_availability_template.to_csv(index=False),
            file_name="scheduling_availability_template.csv",
            mime="text/csv"
        )

    with row2_col2:
        st.download_button(
            label="Download Current Schedule Template",
            data=scheduling_current_template.to_csv(index=False),
            file_name="scheduling_current_template.csv",
            mime="text/csv"
        )

    with st.expander("How to format your Scheduling data"):
        st.markdown(
            """
            **Scheduling Cost File**

            - **Employee**: Name of the employee or resource.
            - **Shift columns**: Enter the labor cost of assigning that employee to each shift.

            **Staffing Requirements File**

            - **Shift**: Must match the shift column names in the Scheduling Cost file.
            - **RequiredEmployees**: Minimum number of employees needed for that shift.

            **Availability File**

            - **Employee**: Must match the employee names in the Scheduling Cost file.
            - **Shift columns**: Enter `1` if the employee is available for that shift and `0` if unavailable.

            **Current Schedule File**

            - **Employee**: Employee name.
            - **Shift**: Shift currently assigned to that employee.

            Employee and shift names must match across all files.
            """
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
        guided_mode
        and any(
            file is not None
            for file in [
                cost_file,
                requirements_file,
                availability_file,
                current_file
            ]
        )
        and st.session_state.scheduling_guide_step == 1
    ):
        st.session_state.scheduling_guide_step = 2
        st.rerun()

    if (
        guided_mode
        and st.session_state.scheduling_guide_step == 2
    ):
        all_scheduling_files_uploaded = all(
            file is not None
            for file in [
                cost_file,
                requirements_file,
                availability_file,
                current_file
            ]
        )

        if all_scheduling_files_uploaded:
            scheduling_guide_placeholder.info(
                "⬇️ **Step 2 of 3 — Review Your Optimization Results**\n\n"
                "All four files have been uploaded. Hidden Profit Analytics will "
                "validate the data and calculate the lowest-cost employee schedule below."
            )
        else:
            scheduling_guide_placeholder.info(
                "⬇️ **Step 2 of 3 — Upload All Four Data Files**\n\n"
                "Upload your completed Scheduling Cost, Staffing Requirements, "
                "Availability, and Current Schedule CSV files to continue."
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

            if guided_mode:
                st.session_state.scheduling_guide_step = 3

                scheduling_guide_placeholder.success(
                    "✅ **Step 3 of 3 — Review the Recommendation**\n\n"
                    "Your optimization is complete. Review the recommended employee schedule, "
                    "assignment changes, and potential savings below."
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

            schedule_comparison = results["schedule_comparison"]

            changed_rows = schedule_comparison[
                schedule_comparison["Changed"] == True
            ]

            unchanged_rows = schedule_comparison[
                schedule_comparison["Changed"] == False
            ]

            change_text = []

            for _, row in changed_rows.iterrows():
                change_text.append(
                    f"reassign {row['Employee']} from "
                    f"{row['CurrentShift']} to "
                    f"{row['OptimizedShift']}"
                )

            keep_text = []

            for _, row in unchanged_rows.iterrows():
                keep_text.append(
                    f"keep {row['Employee']} on "
                    f"{row['CurrentShift']}"
                )

            action_parts = []

            if change_text:
                action_parts.append(
                    "; ".join(change_text)
                )

            if keep_text:
                action_parts.append(
                    "; ".join(keep_text)
                )

            if results["savings"] > 0:
                recommendation_text = (
                    "Recommended action: "
                    + "; ".join(action_parts)
                    + f". This reduces estimated labor cost by "
                    f"${results['savings']:,.2f}, or "
                    f"{results['savings_percent']:.2f}%."
                )

                st.info(recommendation_text)

            else:
                st.info(
                    "Recommended action: Keep the current schedule. "
                    "The optimizer did not identify a lower-cost staffing plan."
                )

            st.subheader("Schedule Changes")

            schedule_display = results["schedule_comparison"].rename(
                columns={
                    "Employee": "Employee",
                    "CurrentShift": "Current Shift",
                    "CurrentCost": "Current Cost",
                    "OptimizedShift": "Recommended Shift",
                    "OptimizedCost": "Recommended Cost",
                    "Changed": "Schedule Changed"
                }
            )

            st.dataframe(
                schedule_display,
                use_container_width=True
            )

        except Exception as error:
            if guided_mode:
                st.session_state.scheduling_guide_step = 2

                scheduling_guide_placeholder.info(
                    "⬇️ **Step 2 of 3 — Correct Your Scheduling Data**\n\n"
                    "The uploaded files need to be corrected before the optimization "
                    "can continue. Review the error below, update the affected CSV, "
                    "and upload the corrected file."
                )

            st.error(str(error))

if tool == "Resource Allocation Optimizer":
    st.header("Resource Allocation Optimizer")

    st.write(
        "Allocate limited budget, staff hours, or other resources "
        "across competing initiatives to maximize total business value."
    )

    resource_allocation_guide_placeholder = st.empty()

    if (
        guided_mode
        and st.session_state.resource_allocation_guide_step == 1
    ):
        resource_allocation_guide_placeholder.info(
            "⬇️ **Step 1 of 3 — Prepare Your Resource Allocation Data**\n\n"
            "Download both CSV templates below. Replace the sample values "
            "with your initiatives, expected value, resource requirements, "
            "current allocation, and available resource limits, then save both files."
        )

    resource_allocation_template = pd.DataFrame(
        {
            "Initiative": [
                "Marketing Campaign",
                "Sales Expansion",
                "Process Automation",
                "Customer Retention"
            ],
            "ProfitPerUnit": [
                1800,
                2200,
                2600,
                1400
            ],
            "BudgetPerUnit": [
                1200,
                1500,
                2000,
                900
            ],
            "HoursPerUnit": [
                18,
                24,
                20,
                12
            ],
            "MaxUnits": [
                8,
                6,
                5,
                10
            ],
            "CurrentUnits": [
                3,
                2,
                1,
                4
            ]
        }
    )

    resource_limits_template = pd.DataFrame(
        {
            "Resource": [
                "Budget",
                "StaffHours"
            ],
            "Limit": [
                15000,
                180
            ]
        }
    )

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="Download Resource Allocation Template",
            data=resource_allocation_template.to_csv(index=False),
            file_name="resource_allocation_template.csv",
            mime="text/csv"
        )

    with col2:
        st.download_button(
            label="Download Resource Limits Template",
            data=resource_limits_template.to_csv(index=False),
            file_name="resource_limits_template.csv",
            mime="text/csv"
        )

    with st.expander("How to format your Resource Allocation data"):
        st.markdown(
            """
            **Resource Allocation File**

            - **Initiative**: Name of the project, program, product, campaign, or activity competing for resources.
            - **ProfitPerUnit**: Estimated profit or value generated by one unit of that initiative.
            - **BudgetPerUnit**: Budget required for one unit.
            - **HoursPerUnit**: Staff hours required for one unit.
            - **MaxUnits**: Maximum number of units that can be funded or completed.
            - **CurrentUnits**: Number of units currently being funded or completed.

            **Resource Limits File**

            - **Resource**: Name of the constrained resource.
            - **Limit**: Total amount available.

            For this version, the required resource names are `Budget` and `StaffHours`.
            The current allocation must stay within the available resource limits.
            """
        )

    allocation_file = st.file_uploader(
        "Upload Resource Allocation Data CSV",
        type=["csv"],
        key="resource_allocation_upload"
    )

    limits_file = st.file_uploader(
        "Upload Resource Limits CSV",
        type=["csv"],
        key="resource_limits_upload"
    )

    if (
        guided_mode
        and (
            allocation_file is not None
            or limits_file is not None
        )
        and st.session_state.resource_allocation_guide_step == 1
    ):
        st.session_state.resource_allocation_guide_step = 2
        st.rerun()

    if (
        guided_mode
        and st.session_state.resource_allocation_guide_step == 2
    ):
        all_resource_files_uploaded = (
            allocation_file is not None
            and limits_file is not None
        )

        if all_resource_files_uploaded:
            resource_allocation_guide_placeholder.info(
                "⬇️ **Step 2 of 3 — Review Your Optimization Results**\n\n"
                "Both files have been uploaded. Hidden Profit Analytics will "
                "validate the data and calculate the optimal resource allocation below."
            )
        else:
            resource_allocation_guide_placeholder.info(
                "⬇️ **Step 2 of 3 — Upload Both Data Files**\n\n"
                "Upload your completed Resource Allocation and Resource Limits "
                "CSV files to continue."
            )

    if (
        allocation_file is not None
        and limits_file is not None
    ):
        try:
            results = run_resource_allocation_optimizer(
                allocation_file,
                limits_file
            )

            if guided_mode:
                st.session_state.resource_allocation_guide_step = 3

                resource_allocation_guide_placeholder.success(
                    "✅ **Step 3 of 3 — Review the Recommendation**\n\n"
                    "Your optimization is complete. Review the recommended "
                    "resource allocation, allocation changes, and potential "
                    "profit improvement below."
                )

            st.success("Optimization completed successfully.")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Current Profit",
                f"${results['current_profit']:,.2f}"
            )

            col2.metric(
                "Optimized Profit",
                f"${results['optimized_profit']:,.2f}"
            )

            col3.metric(
                "Additional Profit",
                f"${results['additional_profit']:,.2f}"
            )

            col4.metric(
                "Improvement %",
                f"{results['improvement_percent']:.2f}%"
            )

            allocation_comparison = results["allocation_comparison"]

            increased = allocation_comparison[
                allocation_comparison["Change"] > 0
            ]

            decreased = allocation_comparison[
                allocation_comparison["Change"] < 0
            ]

            unchanged = allocation_comparison[
                allocation_comparison["Change"] == 0
            ]

            action_parts = []

            for _, row in increased.iterrows():
                action_parts.append(
                    f"increase {row['Initiative']} by "
                    f"{row['Change']:,.0f} units"
                )

            for _, row in decreased.iterrows():
                action_parts.append(
                    f"decrease {row['Initiative']} by "
                    f"{abs(row['Change']):,.0f} units"
                )

            for _, row in unchanged.iterrows():
                action_parts.append(
                    f"keep {row['Initiative']} at "
                    f"{row['CurrentUnits']:,.0f} units"
                )

            if results["additional_profit"] > 0:
                recommendation_text = (
                    "Recommended action: "
                    + "; ".join(action_parts)
                    + f". This increases estimated profit by "
                    f"${results['additional_profit']:,.2f}, or "
                    f"{results['improvement_percent']:.2f}%."
                )

                st.info(recommendation_text)

            else:
                st.info(
                    "Recommended action: Keep the current resource allocation. "
                    "The optimizer did not identify a higher-profit allocation."
                )

            st.subheader("Allocation Changes")

            allocation_display = results["allocation_comparison"].rename(
                columns={
                    "Initiative": "Initiative",
                    "CurrentUnits": "Current Units",
                    "OptimizedUnits": "Recommended Units",
                    "Change": "Unit Change",
                    "ProfitPerUnit": "Profit per Unit",
                    "CurrentProfit": "Current Profit",
                    "OptimizedProfit": "Recommended Profit"
                }
            )

            st.dataframe(
                allocation_display,
                use_container_width=True
            )

            st.subheader("Resource Utilization")

            resource_summary = pd.DataFrame(
                {
                    "Resource": [
                        "Budget",
                        "Staff Hours"
                    ],
                    "Current Use": [
                        results["current_budget_used"],
                        results["current_hours_used"]
                    ],
                    "Recommended Use": [
                        results["optimized_budget_used"],
                        results["optimized_hours_used"]
                    ],
                    "Limit": [
                        results["budget_limit"],
                        results["hours_limit"]
                    ]
                }
            )

            st.dataframe(
                resource_summary,
                use_container_width=True
            )

        except Exception as error:
            if guided_mode:
                st.session_state.resource_allocation_guide_step = 2

                resource_allocation_guide_placeholder.info(
                    "⬇️ **Step 2 of 3 — Correct Your Resource Allocation Data**\n\n"
                    "The uploaded files need to be corrected before the optimization "
                    "can continue. Review the error below, update the affected CSV, "
                    "and upload the corrected file."
                )

            st.error(str(error))        

if tool == "Profit Analyzer" and st.session_state.hpa_page == "profit_analyzer":
    st.title("Hidden Profit Analytics")
    st.subheader("Business Optimization Dashboard")

    with st.expander("How to Use the Profit Analyzer", expanded=False):
        st.markdown(
            """
    1. **Enter the business information** and select a target profit margin.
    2. **Upload your financial data** using a CSV with Month, Revenue, and Expenses. If needed, download the CSV template in the Financial Data section.
    3. **Set the improvement assumptions** based on what is realistic for the business.
    4. Click **Run Analysis** to identify potential hidden profit opportunities.
    5. **Review the optimization recommendation, scenarios, and sensitivity analysis.**
    6. **Generate and download the Client Report** for a summary of the findings and recommended action plan.
    7. When you're finished testing, use the **Give Beta Feedback** button in the sidebar to share your experience.
    """
        )

    with st.expander("Profit Analyzer Help & FAQs", expanded=False):

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

    # ==========================================
    # STEP 1: BUSINESS INFORMATION
    # ==========================================

    if (
        guided_mode
        and tool == "Profit Analyzer"
        and st.session_state.profit_guide_step == 1
    ):
        st.sidebar.info(
            "⬇️ **Step 1 of 4 — Business Information**\n\n"
            "Enter your company name and target profit margin below."
        )

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

        if (
            guided_mode
            and st.session_state.profit_guide_step == 1
        ):
            if st.button(
                "Continue to Financial Data →",
                use_container_width=True
            ):
                st.session_state.profit_guide_step = 2
                st.rerun()

    target_margin = target_percent / 100

    # ==========================================
    # STEP 2: FINANCIAL DATA
    # ==========================================

    if (
        guided_mode
        and st.session_state.profit_guide_step == 2
    ):
        st.sidebar.info(
            "⬇️ **Step 2 of 4 — Financial Data**\n\n"
            "Download the CSV template, enter your financial data, "
            "then upload the completed file below."
        )

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

        if (
            guided_mode
            and st.session_state.profit_guide_step == 2
            and uploaded_file is not None
        ):
            st.session_state.profit_guide_step = 3
            st.rerun()

    # ==========================================
    # STEP 3: IMPROVEMENT ASSUMPTIONS
    # ==========================================

    if (
        guided_mode
        and st.session_state.profit_guide_step == 3
    ):
        st.sidebar.info(
            "⬇️ **Step 3 of 4 — Improvement Assumptions**\n\n"
            "Review and adjust the assumptions below to reflect "
            "realistic improvements for this business."
        )

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

            if (
                guided_mode
                and st.session_state.profit_guide_step == 3
            ):
                if st.button(
                    "Continue to Analysis →",
                    use_container_width=True
                ):
                    st.session_state.profit_guide_step = 4
                    st.rerun()

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

        step4_guide_placeholder = st.sidebar.empty()

        if (
            guided_mode
            and st.session_state.profit_guide_step == 4
        ):
            step4_guide_placeholder.info(
                "⬇️ **Step 4 of 4 — Run Your Analysis**\n\n"
                "Review your setup, then click **4. Run Analysis** below "
                "to generate your recommendations."
            )

        st.sidebar.divider()

        st.sidebar.caption(
            "Review the client information, financial data, "
            "and improvement assumptions before running the analysis."
        )

        guide_complete_placeholder = st.sidebar.empty()

        if (
            guided_mode
            and st.session_state.profit_guide_step == 5
            and st.session_state.get("analysis_ready", False)
        ):
            guide_complete_placeholder.success(
                "✅ **Guided setup complete**\n\n"
                "Your analysis is ready. Review the recommendations and generate "
                "the client report when you're ready."
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
            if guided_mode:
                st.session_state.profit_guide_step = 5

                step4_guide_placeholder.empty()

                guide_complete_placeholder.success(
                    "✅ **Guided setup complete**\n\n"
                    "Your analysis is ready. Review the recommendations and generate "
                    "the client report when you're ready."
                )

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
