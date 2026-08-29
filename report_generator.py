import matplotlib.pyplot as plt

from datetime import date
import tempfile
from reportlab.lib import colors
from reportlab.lib import styles
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)

def add_page_footer(canvas, doc, company_name):
    canvas.saveState()

    page_number = canvas.getPageNumber()

    footer_text = (
        f"Hidden Profit Analytics | "
        f"{company_name} | Confidential"
    )

    canvas.setFont("Helvetica", 8)

    canvas.drawString(
        0.5 * inch,
        0.30 * inch,
        footer_text
    )

    canvas.drawRightString(
        8.0 * inch,
        0.30 * inch,
        f"Page {page_number}"
    )

    canvas.restoreState()

def create_pdf_report(
    analyzed_data,
    total_revenue,
    total_profit,
    total_opportunity,
    largest_opportunity,
    best_scenario,
    company_name,
    target_margin,
    revenue_cost,
    expense_cost,
    max_revenue_increase,
    max_expense_reduction,
    sensitivity_df,
    sensitivity_percent
):
    temp_pdf = tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False
    )
    pdf_name = temp_pdf.name
    temp_pdf.close()

    doc = SimpleDocTemplate(
        pdf_name,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )

    styles = getSampleStyleSheet()
    story = []
    report_date = date.today().strftime("%B %d, %Y")

# ==========================================
# REPORT HEADER
# ==========================================

    story.append(
        Paragraph(
            "Hidden Profit Analytics",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            f"{company_name} - Profit Opportunity & Optimization Report",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            f"Report Date: {report_date}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 0.18 * inch))

        # Executive Summary
    story.append(
        Paragraph(
            "Executive Summary",
            styles["Heading2"]
        )
    )

    summary_text = (
        f"{largest_opportunity['Month']} represents the largest "
        f"hidden profit opportunity at "
        f"${largest_opportunity['Profit Opportunity']:,.2f}. "
        f"The custom optimization model provides the "
        f"lowest-cost feasible strategy for closing this profit gap "
        f"under the selected client assumptions. "
        f"The recommended strategy calls for "
        f"${best_scenario['Revenue Increase']:,.2f} in additional revenue "
        f"and ${best_scenario['Expense Reduction']:,.2f} in expense reduction, "
        f"with an estimated implementation cost of "
        f"${best_scenario['Implementation Cost']:,.2f}."
    )

    story.append(
        Paragraph(
            summary_text,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 0.15 * inch))

    recommendation_box_data = [
        [
            Paragraph(
                "<b>Executive Recommendation</b>",
                styles["BodyText"]
            )
        ],
        [
            Paragraph(
                (
                    f"Close {largest_opportunity['Month']}'s "
                    f"${largest_opportunity['Profit Opportunity']:,.2f} "
                    f"profit gap using the "
                    f"<b>custom optimized strategy</b>: "
                    f"${best_scenario['Expense Reduction']:,.2f} in "
                    f"expense reduction and "
                    f"${best_scenario['Revenue Increase']:,.2f} in "
                    f"additional revenue. "
                    f"The estimated implementation cost is "
                    f"${best_scenario['Implementation Cost']:,.2f}."
                ),
                styles["BodyText"]
            )
        ]
    ]

    recommendation_box = Table(
        recommendation_box_data,
        colWidths=[6.5 * inch]
    )

    recommendation_box.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("BOX", (0, 0), (-1, -1), 1, colors.grey),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP")
        ])
    )

    story.append(recommendation_box)

    story.append(Spacer(1, 0.20 * inch))

    # ==========================================
    # KEY FINANCIAL METRICS
    # ==========================================

    story.append(
        Paragraph(
            "Key Financial Metrics",
            styles["Heading2"]
        )
    )

    kpi_style = styles["BodyText"].clone("KPIStyle")
    kpi_style.alignment = 1

    kpi_data = [
        [
            Paragraph(
                f"<b>${total_revenue:,.0f}</b><br/>Total Revenue",
                kpi_style
            ),
            Paragraph(
                f"<b>${total_profit:,.0f}</b><br/>Total Profit",
                kpi_style
            ),
            Paragraph(
                f"<b>${total_opportunity:,.0f}</b><br/>Hidden Profit Opportunity",
                kpi_style
            ),
            Paragraph(
                f"<b>{target_margin * 100:.0f}%</b><br/>Target Margin",
                kpi_style
            )
        ]
    ]

    kpi_table = Table(
        kpi_data,
        colWidths=[
            1.625 * inch,
            1.625 * inch,
            1.625 * inch,
            1.625 * inch
        ]
    )

    kpi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(kpi_table)
    story.append(Spacer(1, 0.15 * inch))

    priority_data = [
        ["Priority Opportunity", "Recommended Strategy"],
        [
            f"{largest_opportunity['Month']} "
            f"(${largest_opportunity['Profit Opportunity']:,.2f})",
            "Custom Optimization"
        ]
    ]

    priority_table = Table(
        priority_data,
        colWidths=[3.25 * inch, 3.25 * inch]
    )

    priority_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
        ])
    )

    story.append(priority_table)
    story.append(Spacer(1, 0.25 * inch))

    # Monthly Analysis Table
    story.append(
        Paragraph(
            "Monthly Opportunity Analysis",
            styles["Heading2"]
        )
    )

    monthly_table_data = [
        [
            "Month",
            "Revenue",
            "Expenses",
            "Profit",
            "Margin",
            "Performance",
            "Opportunity"
        ]
    ]

    for _, row in analyzed_data.iterrows():
        monthly_table_data.append([
            row["Month"],
            f"${row['Revenue']:,.0f}",
            f"${row['Expenses']:,.0f}",
            f"${row['Profit']:,.0f}",
            f"{row['Profit Margin']:.2f}%",
            row["Performance"],
            f"${row['Profit Opportunity']:,.0f}"
        ])

    monthly_table = Table(
        monthly_table_data,
        repeatRows=1
    )

    monthly_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (1, 1), (4, -1), "RIGHT"),
            ("ALIGN", (6, 1), (6, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ])
    )

    story.append(monthly_table)
    story.append(PageBreak())

    # Charts
    story.append(
        Paragraph(
            "Profit Opportunity by Month",
            styles["Heading2"]
        )
    )

    story.append(
        Image(
            "profit_opportunity.png",
            width=5.8 * inch,
            height=3.3 * inch
        )
    )

    story.append(Spacer(1, 0.08 * inch))

    story.append(
        Paragraph(
            "Predefined Scenario Cost Comparison",
            styles["Heading2"]
        )
    )

    story.append(
        Image(
            "scenario_cost_comparison.png",
            width=5.0 * inch,
            height=3.1 * inch
        )
    )

    # ==========================================
    # OPTIMIZATION ASSUMPTIONS
    # ==========================================

    story.append(Spacer(1, 0.15 * inch))

    story.append(
        Paragraph(
            "Optimization Assumptions",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            "The optimization model uses the following client-specific "
            "assumptions to determine the recommended strategy.",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 0.10 * inch))

    assumptions_data = [
        [
            "Revenue Cost / $1",
            "Expense Cost / $1",
            "Max Revenue Increase",
            "Max Expense Reduction"
        ],
        [
            f"${revenue_cost:.2f}",
            f"${expense_cost:.2f}",
            f"${max_revenue_increase:,.0f}",
            f"${max_expense_reduction:,.0f}"
        ]
    ]

    assumptions_table = Table(
        assumptions_data,
        colWidths=[
            1.625 * inch,
            1.625 * inch,
            1.625 * inch,
            1.625 * inch
        ]
    )

    assumptions_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
        ])
    )

    story.append(assumptions_table)
    story.append(Spacer(1, 0.20 * inch))

    # ==========================================
    # RECOMMENDED STRATEGY
    # ==========================================

    story.append(PageBreak())

    story.append(
        Paragraph(
            "Recommended Strategy",
            styles["Heading2"]
        )
    )

    recommendation_data = [
        ["Recommendation", "Amount"],
        [
            "Revenue Increase",
            f"${best_scenario['Revenue Increase']:,.2f}"
        ],
        [
            "Expense Reduction",
            f"${best_scenario['Expense Reduction']:,.2f}"
        ],
        [
            "Implementation Cost",
            f"${best_scenario['Implementation Cost']:,.2f}"
        ]
    ]

    recommendation_table = Table(
        recommendation_data,
        colWidths=[3.5 * inch, 2.5 * inch]
    )

    recommendation_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(recommendation_table)

    story.append(Spacer(1, 0.15 * inch))

    business_impact = (
        f"<b>Business Impact:</b> The recommended "
        f"{best_scenario['Scenario']} strategy closes "
        f"{largest_opportunity['Month']}'s "
        f"${largest_opportunity['Profit Opportunity']:,.2f} profit gap "
        f"at the lowest estimated implementation cost. "
        f"The model recommends "
        f"${best_scenario['Expense Reduction']:,.2f} in expense reduction "
        f"and ${best_scenario['Revenue Increase']:,.2f} in additional revenue."
    )

    story.append(
        Paragraph(
            business_impact,
            styles["BodyText"]
        )
    )
    story.append(Spacer(1, 0.12 * inch))

    if expense_cost < revenue_cost:
        strategy_reason = (
            f"<b>Why This Strategy:</b> Expense reduction is prioritized because "
            f"its estimated implementation cost is ${expense_cost:.2f} per $1 of "
            f"profit improvement, compared with ${revenue_cost:.2f} per $1 through "
            f"additional revenue. The model therefore uses the lower-cost expense "
            f"reduction opportunity first, subject to the client's realistic limits, "
            f"and then uses additional revenue to close any remaining profit gap."
        )

    elif revenue_cost < expense_cost:
        strategy_reason = (
            f"<b>Why This Strategy:</b> Revenue growth is prioritized because "
            f"its estimated implementation cost is ${revenue_cost:.2f} per $1 of "
            f"profit improvement, compared with ${expense_cost:.2f} per $1 through "
            f"expense reduction. The model therefore uses the lower-cost revenue "
            f"opportunity first, subject to the client's realistic limits, "
            f"and then uses expense reduction to close any remaining profit gap."
        )

    else:
        strategy_reason = (
            f"<b>Why This Strategy:</b> Revenue growth and expense reduction have "
            f"the same estimated implementation cost of ${revenue_cost:.2f} per $1 "
            f"of profit improvement. The recommended mix is therefore driven "
            f"primarily by the realistic improvement limits entered for the business."
        )

    story.append(
        Paragraph(
            strategy_reason,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 0.18 * inch))

    # ==========================================
    # ROI & PAYBACK ANALYSIS
    # ==========================================

    monthly_profit_improvement = (
        best_scenario["Revenue Increase"]
        + best_scenario["Expense Reduction"]
    )

    first_month_net_benefit = (
        monthly_profit_improvement
        - best_scenario["Implementation Cost"]
    )

    implementation_cost = best_scenario["Implementation Cost"]

    if implementation_cost > 0:
        benefit_cost_ratio = (
            monthly_profit_improvement
            / implementation_cost
        )

        payback_months = (
            implementation_cost
            / monthly_profit_improvement
        )
    else:
        benefit_cost_ratio = None
        payback_months = 0


    story.append(
        Paragraph(
            "ROI & Payback Analysis",
            styles["Heading2"]
        )
    )

    roi_header_style = ParagraphStyle(
        "ROIHeader",
        parent=styles["BodyText"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        leading=12
    )
    
    roi_data = [
        [
            Paragraph(
                "Monthly Profit<br/>Improvement",
                roi_header_style
            ),
            Paragraph(
                "First-Month<br/>Net Benefit",
                roi_header_style
            ),
            Paragraph(
                "Benefit-Cost<br/>Ratio",
                roi_header_style
            ),
            Paragraph(
                "Estimated<br/>Payback",
                roi_header_style
            )
        ],
        [
            f"${monthly_profit_improvement:,.2f}",
            f"${first_month_net_benefit:,.2f}",
            (
                f"{benefit_cost_ratio:.2f}x"
                if benefit_cost_ratio is not None
                else "No Cost"
            ),
            (
                f"{payback_months:.2f} months"
                if implementation_cost > 0
                else "Immediate"
            )
        ]
    ]

    roi_table = Table(
        roi_data,
        colWidths=[
            1.65 * inch,
            1.65 * inch,
            1.45 * inch,
            1.45 * inch
        ]
    )

    roi_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(roi_table)

    story.append(Spacer(1, 0.10 * inch))

    if implementation_cost > 0:
        roi_summary = (
            f"<b>Financial Return:</b> The recommended strategy is expected "
            f"to generate ${monthly_profit_improvement:,.2f} in monthly profit "
            f"improvement for an estimated implementation cost of "
            f"${implementation_cost:,.2f}. This represents a "
            f"{benefit_cost_ratio:.2f}x benefit-cost ratio and an estimated "
            f"payback period of {payback_months:.2f} months."
        )
    else:
        roi_summary = (
            f"<b>Financial Return:</b> The recommended strategy is expected "
            f"to generate ${monthly_profit_improvement:,.2f} in monthly profit "
            f"improvement with no estimated implementation cost."
        )

    story.append(
        Paragraph(
            roi_summary,
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 0.18 * inch))

    # ==========================================
    # RECOMMENDATION ROBUSTNESS
    # ==========================================

    feasible_sensitivity = sensitivity_df[
        sensitivity_df["Status"] == "Feasible"
    ].copy()

    if not feasible_sensitivity.empty:

        strategy_combinations = feasible_sensitivity[
            ["Revenue Increase", "Expense Reduction"]
        ].drop_duplicates()

        strategy_changes = len(strategy_combinations) - 1
        scenarios_tested = len(feasible_sensitivity)

        min_sensitivity_cost = feasible_sensitivity[
            "Implementation Cost"
        ].min()

        max_sensitivity_cost = feasible_sensitivity[
            "Implementation Cost"
        ].max()

        story.append(
            Paragraph(
                "Recommendation Robustness",
                styles["Heading2"]
            )
        )

        robustness_data = [
            [
                Paragraph(
                    "<b>Scenarios Tested</b>",
                    roi_header_style
                ),
                Paragraph(
                    "<b>Strategy Changes</b>",
                    roi_header_style
                ),
                Paragraph(
                    "<b>Implementation Cost Range</b>",
                    roi_header_style
                )
            ],
            [
                f"{scenarios_tested}",
                f"{strategy_changes}",
                (
                    f"${min_sensitivity_cost:,.2f} - "
                    f"${max_sensitivity_cost:,.2f}"
                )
            ]
        ]

        robustness_table = Table(
            robustness_data,
            colWidths=[
                1.8 * inch,
                1.8 * inch,
                2.6 * inch
            ]
        )

        robustness_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
            ])
        )

        story.append(robustness_table)
        story.append(Spacer(1, 0.10 * inch))

        if strategy_changes == 0:

            robustness_summary = (
                f"<b>Robust Recommendation:</b> The optimal strategy remained "
                f"unchanged across all {scenarios_tested} tested "
                f"+/-{sensitivity_percent}% implementation-cost scenarios. "
                f"The model consistently recommended "
                f"${best_scenario['Expense Reduction']:,.2f} in "
                f"monthly expense reduction and "
                f"${best_scenario['Revenue Increase']:,.2f} in additional "
                f"monthly revenue. Estimated implementation cost ranged from "
                f"${min_sensitivity_cost:,.2f} to "
                f"${max_sensitivity_cost:,.2f}, indicating that the "
                f"recommendation is robust to moderate changes in the "
                f"underlying cost assumptions."
            )

        else:

            robustness_summary = (
                f"<b>Sensitivity Detected:</b> The optimal strategy changed "
                f"under some of the {scenarios_tested} tested "
                f"+/-{sensitivity_percent}% implementation-cost scenarios. "
                f"Estimated implementation cost ranged from "
                f"${min_sensitivity_cost:,.2f} to "
                f"${max_sensitivity_cost:,.2f}. Management should review "
                f"the sensitivity results before implementation."
            )

        story.append(
            Paragraph(
                robustness_summary,
                styles["BodyText"]
            )
        )

        story.append(Spacer(1, 0.18 * inch))

    # ==========================================
    # MANAGEMENT ACTION PLAN
    # ==========================================

    story.append(PageBreak())
    
    story.append(
        Paragraph(
            "Management Action Plan",
            styles["Heading2"]
        )
    )

    action_plan = [
    [
        Paragraph("<b>1</b>", styles["BodyText"]),
        Paragraph("<b>Review Expenses</b>", styles["BodyText"]),
        Paragraph(
            f"Evaluate {largest_opportunity['Month']} operating "
            f"expenses and identify approximately "
            f"${best_scenario['Expense Reduction']:,.2f} "
            f"in achievable cost reductions.",
            styles["BodyText"]
        )
    ],
    [
        Paragraph("<b>2</b>", styles["BodyText"]),
        Paragraph(
            "<b>Capture Revenue Opportunity</b>",
            styles["BodyText"]
        ),
        Paragraph(
            f"Identify opportunities to generate at least "
            f"${best_scenario['Revenue Increase']:,.2f} "
            f"in additional revenue.",
            styles["BodyText"]
        )
    ],
    [
        Paragraph("<b>3</b>", styles["BodyText"]),
        Paragraph(
            "<b>Control Implementation Cost</b>",
            styles["BodyText"]
        ),
        Paragraph(
            f"Prioritize improvement actions whose combined "
            f"implementation cost remains near or below the "
            f"modeled ${best_scenario['Implementation Cost']:,.2f}.",
            styles["BodyText"]
        )
    ],
    [
        Paragraph("<b>4</b>", styles["BodyText"]),
        Paragraph(
            "<b>Measure Results</b>",
            styles["BodyText"]
        ),
        Paragraph(
            f"Re-run the Hidden Profit Analysis after implementation "
            f"to evaluate progress toward the "
            f"{target_margin * 100:.0f}% target profit margin.",
            styles["BodyText"]
        )
    ]
]

    action_table = Table(
        action_plan,
        colWidths=[
            0.4 * inch,
            1.8 * inch,
            4.3 * inch
        ]
    )

    action_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(action_table)

    # ==========================================
    # 90-DAY IMPLEMENTATION ROADMAP
    # ==========================================

    story.append(Spacer(1, 0.30 * inch))

    story.append(
        Paragraph(
            "90-Day Implementation Roadmap",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            "A phased implementation plan for translating the optimization "
            "recommendation into measurable financial results.",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 0.12 * inch))

    roadmap_data = [
        [
            Paragraph("<b>Timeline</b>", styles["BodyText"]),
            Paragraph("<b>Phase</b>", styles["BodyText"]),
            Paragraph("<b>Management Focus</b>", styles["BodyText"])
        ],
        [
            Paragraph("<b>Days 1-30</b>", styles["BodyText"]),
            Paragraph("<b>Diagnose</b>", styles["BodyText"]),
            Paragraph(
                f"Review {largest_opportunity['Month']} operating expenses "
                f"to identify specific opportunities for approximately "
                f"${best_scenario['Expense Reduction']:,.2f} in monthly "
                f"expense reduction. Validate opportunities to generate at "
                f"least ${best_scenario['Revenue Increase']:,.2f} in "
                f"additional monthly revenue.",
                styles["BodyText"]
            )
        ],
        [
            Paragraph("<b>Days 31-60</b>", styles["BodyText"]),
            Paragraph("<b>Implement</b>", styles["BodyText"]),
            Paragraph(
                f"Execute the selected cost-reduction and revenue initiatives. "
                f"Track implementation spending against the modeled "
                f"${best_scenario['Implementation Cost']:,.2f} implementation "
                f"cost and document actual financial results.",
                styles["BodyText"]
            )
        ],
        [
            Paragraph("<b>Days 61-90</b>", styles["BodyText"]),
            Paragraph("<b>Measure</b>", styles["BodyText"]),
            Paragraph(
                f"Compare actual revenue, expenses, profit margin, and "
                f"implementation cost with the optimization targets. "
                f"Re-run Hidden Profit Analytics to measure progress toward "
                f"the {target_margin:.0%} target profit margin and identify "
                f"the next improvement opportunity.",
                styles["BodyText"]
            )
        ]
    ]

    roadmap_table = Table(
        roadmap_data,
        colWidths=[
            1.0 * inch,
            1.15 * inch,
            4.35 * inch
        ]
    )

    roadmap_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (1, -1), "CENTER"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
        ])
    )

    story.append(roadmap_table)

    doc.build(
        story,
        onFirstPage=lambda canvas, doc: add_page_footer(
            canvas,
            doc,
            company_name
        ),
        onLaterPages=lambda canvas, doc: add_page_footer(
            canvas,
            doc,
            company_name
        )
    )

    print()
    print(f"PDF report saved to {pdf_name}")
    return pdf_name

def create_profit_opportunity_chart(
    data,
    largest_opportunity
):
    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        data["Month"],
        data["Profit Opportunity"]
    )

    plt.title("Hidden Profit Opportunity by Month")
    plt.xlabel("Month")
    plt.ylabel("Profit Opportunity ($)")

    for bar in bars:
        height = bar.get_height()

        plt.annotate(
            f"${height:,.0f}",
            xy=(
                bar.get_x() + bar.get_width() / 2,
                height
            ),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom"
        )

    priority_month = largest_opportunity["Month"]
    priority_value = largest_opportunity["Profit Opportunity"]

    plt.annotate(
        f"Priority: {priority_month}",
        xy=(priority_month, priority_value),
        xytext=(0, -35),
        textcoords="offset points",
        ha="center",
        va="top"
    )

    plt.tight_layout()
    plt.savefig("profit_opportunity.png")
    plt.close()


def create_scenario_cost_chart(
    scenario_results_df,
    best_scenario
):
    feasible_chart_data = scenario_results_df[
        scenario_results_df["Status"] == "Feasible"
    ]

    if feasible_chart_data.empty:
        print("No feasible scenarios available for chart.")
        return

    plt.figure(figsize=(8, 6))

    scenario_bars = plt.bar(
        feasible_chart_data["Scenario"],
        feasible_chart_data["Implementation Cost"]
    )

    plt.title("Implementation Cost by Predefined Scenario")
    plt.xlabel("Scenario")
    plt.ylabel("Implementation Cost ($)")

    for bar in scenario_bars:
        height = bar.get_height()

        plt.annotate(
            f"${height:,.0f}",
            xy=(
                bar.get_x() + bar.get_width() / 2,
                height
            ),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom"
        )

    lowest_cost_scenario = best_scenario["Scenario"]
    lowest_cost = best_scenario["Implementation Cost"]

    plt.annotate(
        f"Lowest-Cost: {lowest_cost_scenario}",
        xy=(lowest_cost_scenario, lowest_cost),
        xytext=(0, -35),
        textcoords="offset points",
        ha="center",
        va="top"
    )

    plt.tight_layout()
    plt.savefig("scenario_cost_comparison.png")
    plt.close()
