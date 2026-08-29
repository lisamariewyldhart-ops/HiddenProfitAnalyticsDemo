import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
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

def create_pdf_report(
    data,
    total_revenue,
    total_profit,
    total_opportunity,
    largest_opportunity,
    best_scenario,
    company_name,
    target_margin
):
    pdf_name = "hidden_profit_report.pdf"

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

    # Title
    story.append(
    Paragraph(
        "Hidden Profit Analytics",
        styles["Title"]
    )
    )

    story.append(
        Paragraph(
            f"{company_name} - Business Optimization Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 0.20 * inch))

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
        f"The {best_scenario['Scenario']} scenario provides the "
        f"lowest-cost feasible strategy for closing this profit gap. "
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

    story.append(Spacer(1, 0.25 * inch))

    # Key Metrics
    story.append(
        Paragraph(
            "Key Financial Metrics",
            styles["Heading2"]
        )
    )
    metrics_data = [
            ["Metric", "Value"],
            [
                "Total Revenue",
                f"${total_revenue:,.2f}"
            ],
            [
                "Total Profit",
                f"${total_profit:,.2f}"
            ],
            [
                "Target Profit Margin",
                f"{target_margin * 100:.0f}%"
            ],
            [
                "Total Hidden Profit Opportunity",
                f"${total_opportunity:,.2f}"
            ],
            [
                "Largest Opportunity",
                f"{largest_opportunity['Month']} "
                f"(${largest_opportunity['Profit Opportunity']:,.2f})"
            ],
            [
                "Recommended Scenario",
                best_scenario["Scenario"]
            ]
        ]
    metrics_table = Table(
        metrics_data,
        colWidths=[3.5 * inch, 3.0 * inch]
    )

    metrics_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(metrics_table)
    story.append(Spacer(1, 0.3 * inch))

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

    for _, row in data.iterrows():
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
            "Scenario Cost Comparison",
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

    # Recommendation
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

    doc.build(story)

    print()
    print(f"PDF report saved to {pdf_name}")
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

    plt.title("Implementation Cost by Feasible Scenario")
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

    recommended_scenario = best_scenario["Scenario"]
    recommended_cost = best_scenario["Implementation Cost"]

    plt.annotate(
        f"Recommended: {recommended_scenario}",
        xy=(recommended_scenario, recommended_cost),
        xytext=(0, -35),
        textcoords="offset points",
        ha="center",
        va="top"
    )

    plt.tight_layout()
    plt.savefig("scenario_cost_comparison.png")
    plt.close()
