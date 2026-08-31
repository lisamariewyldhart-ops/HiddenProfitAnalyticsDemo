import pandas as pd
import pulp


def run_set_covering_optimizer(csv_file="set_covering_data.csv"):
    # -----------------------------
    # LOAD BUSINESS DATA
    # -----------------------------
    try:
        data = pd.read_csv(csv_file)

    except pd.errors.EmptyDataError:
        raise ValueError(
            "The Set Covering CSV is empty. "
            "Please download the Set Covering template, enter your data, "
            "and upload the completed file."
        )

    except pd.errors.ParserError:
        raise ValueError(
            "The Set Covering CSV could not be read correctly. "
            "Please make sure it is a valid CSV file and has not been "
            "reformatted or saved with an unusual delimiter."
        )

    if data.empty:
        raise ValueError(
            "The Set Covering CSV does not contain any options."
        )

    data.columns = data.columns.str.strip()

    # -----------------------------
    # VALIDATE REQUIRED COLUMNS
    # -----------------------------
    required_columns = {
        "Option",
        "Cost",
        "CurrentSelected"
    }

    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(
            "Your Set Covering file is missing the required column(s): "
            + ", ".join(sorted(missing_columns))
            + ". Please use the downloadable Set Covering CSV template "
              "and keep the column names exactly as shown."
        )

    # -----------------------------
    # CLEAN OPTION NAMES
    # -----------------------------
    data["Option"] = (
        data["Option"]
        .astype(str)
        .str.strip()
    )

    if data["Option"].eq("").any():
        raise ValueError(
            "Option names cannot be blank."
        )

    # -----------------------------
    # CHECK BLANK REQUIRED VALUES
    # -----------------------------
    if data[
        ["Option", "Cost", "CurrentSelected"]
    ].isnull().any().any():
        raise ValueError(
            "The Set Covering file contains blank values. "
            "Every row must include an Option, Cost, "
            "and CurrentSelected value."
        )

    # -----------------------------
    # VALIDATE COST
    # -----------------------------
    data["Cost"] = pd.to_numeric(
        data["Cost"],
        errors="coerce"
    )

    if data["Cost"].isnull().any():
        raise ValueError(
            "One or more Cost values are not numeric. "
            "Enter numbers only in the Cost column."
        )

    if (data["Cost"] < 0).any():
        raise ValueError(
            "Cost values cannot be negative."
        )

    # -----------------------------
    # VALIDATE CURRENT SELECTED
    # -----------------------------
    data["CurrentSelected"] = pd.to_numeric(
        data["CurrentSelected"],
        errors="coerce"
    )

    if data["CurrentSelected"].isnull().any():
        raise ValueError(
            "CurrentSelected must contain only 0 or 1. "
            "Use 1 if an option is currently selected and 0 otherwise."
        )

    if not data["CurrentSelected"].isin([0, 1]).all():
        raise ValueError(
            "CurrentSelected must contain only 0 or 1. "
            "Use 1 for a selected option and 0 for an unselected option."
        )

    # -----------------------------
    # CHECK DUPLICATE OPTIONS
    # -----------------------------
    duplicate_options = data["Option"].duplicated(
        keep=False
    )

    if duplicate_options.any():
        duplicate_text = ", ".join(
            sorted(
                data.loc[
                    duplicate_options,
                    "Option"
                ].unique()
            )
        )

        raise ValueError(
            "Duplicate option names were found: "
            f"{duplicate_text}. "
            "Each option should appear only once."
        )

    # -----------------------------
    # IDENTIFY OPTIONS AND COVERAGE COLUMNS
    # -----------------------------
    options = data["Option"].tolist()

    zones = [
        column
        for column in data.columns
        if column not in [
            "Option",
            "Cost",
            "CurrentSelected"
        ]
    ]

    if not zones:
        raise ValueError(
            "No coverage columns were found. "
            "Add at least one column representing a required "
            "location, customer group, route, time period, or item."
        )

    # -----------------------------
    # VALIDATE COVERAGE DATA
    # -----------------------------
    for zone in zones:
        data[zone] = pd.to_numeric(
            data[zone],
            errors="coerce"
        )

        if data[zone].isnull().any():
            raise ValueError(
                f"Coverage values in '{zone}' must be numeric. "
                "Enter only 1 for covered or 0 for not covered."
            )

        if not data[zone].isin([0, 1]).all():
            raise ValueError(
                f"Coverage values in '{zone}' must be 0 or 1."
            )

        if data[zone].sum() == 0:
            raise ValueError(
                f"'{zone}' cannot be covered because no option "
                "has a coverage value of 1 for that requirement."
            )

    # -----------------------------
    # VALIDATE CURRENT COVERAGE
    # -----------------------------
    uncovered_current = []

    for zone in zones:
        current_coverage = (
            data[zone] * data["CurrentSelected"]
        ).sum()

        if current_coverage < 1:
            uncovered_current.append(zone)

    if uncovered_current:
        raise ValueError(
            "The current configuration does not cover: "
            + ", ".join(uncovered_current)
            + ". At least one currently selected option must cover "
              "each required coverage column."
        )

    # -----------------------------
    # CREATE COST DICTIONARY
    # -----------------------------
    cost = {
        row["Option"]: row["Cost"]
        for _, row in data.iterrows()
    }

    # -----------------------------
    # CREATE OPTIMIZATION MODEL
    # -----------------------------
    model = pulp.LpProblem(
        "Set_Covering_Optimizer",
        pulp.LpMinimize
    )

    # -----------------------------
    # DECISION VARIABLES
    # -----------------------------
    x = pulp.LpVariable.dicts(
        "Select",
        options,
        cat="Binary"
    )

    # -----------------------------
    # OBJECTIVE FUNCTION
    # -----------------------------
    model += pulp.lpSum(
        cost[option] * x[option]
        for option in options
    )

    # -----------------------------
    # COVERAGE CONSTRAINTS
    # -----------------------------
    for zone in zones:
        model += pulp.lpSum(
            data.loc[
                data["Option"] == option,
                zone
            ].iloc[0] * x[option]
            for option in options
        ) >= 1

    # -----------------------------
    # SOLVE MODEL
    # -----------------------------
    model.solve(
        pulp.PULP_CBC_CMD(msg=False)
    )

    status = pulp.LpStatus[model.status]

    if status != "Optimal":
        raise ValueError(
            f"No optimal solution could be found. Status: {status}"
        )

    # -----------------------------
    # BUILD OPTIMIZED RESULTS
    # -----------------------------
    optimized_rows = []

    for option in options:
        selected = int(
            pulp.value(x[option]) == 1
        )

        optimized_rows.append(
            {
                "Option": option,
                "Cost": cost[option],
                "CurrentSelected": int(
                    data.loc[
                        data["Option"] == option,
                        "CurrentSelected"
                    ].iloc[0]
                ),
                "OptimizedSelected": selected
            }
        )

    comparison_df = pd.DataFrame(optimized_rows)

    comparison_df["Recommendation"] = (
        comparison_df.apply(
            lambda row:
            "Keep"
            if row["CurrentSelected"] == 1
            and row["OptimizedSelected"] == 1
            else "Remove"
            if row["CurrentSelected"] == 1
            and row["OptimizedSelected"] == 0
            else "Add"
            if row["CurrentSelected"] == 0
            and row["OptimizedSelected"] == 1
            else "Not Needed",
            axis=1
        )
    )

    selected_options = comparison_df[
        comparison_df["OptimizedSelected"] == 1
    ][["Option", "Cost"]].copy()

    # -----------------------------
    # CALCULATE BUSINESS IMPACT
    # -----------------------------
    current_cost = (
        data["Cost"] * data["CurrentSelected"]
    ).sum()

    optimized_cost = pulp.value(model.objective)

    savings = current_cost - optimized_cost

    savings_percent = (
        (savings / current_cost) * 100
        if current_cost > 0
        else 0
    )

    # -----------------------------
    # RETURN RESULTS
    # -----------------------------
    return {
        "status": status,
        "selected_options": selected_options,
        "comparison": comparison_df,
        "current_cost": current_cost,
        "optimized_cost": optimized_cost,
        "savings": savings,
        "savings_percent": savings_percent
    }


# -----------------------------
# RUN DIRECTLY FOR TESTING
# -----------------------------
if __name__ == "__main__":
    results = run_set_covering_optimizer()

    print("\nSet Covering Optimizer")
    print("----------------------")

    print(f"Status: {results['status']}")

    print("\nRecommended Options:")

    for _, row in results["selected_options"].iterrows():
        print(
            f"{row['Option']} | "
            f"Cost: ${row['Cost']:,.2f}"
        )

    print("\nConfiguration Changes:")

    for _, row in results["comparison"].iterrows():
        print(
            f"{row['Option']}: "
            f"{row['Recommendation']}"
        )

    print(
        f"\nCurrent Total Cost: "
        f"${results['current_cost']:,.2f}"
    )

    print(
        f"Optimized Total Cost: "
        f"${results['optimized_cost']:,.2f}"
    )

    print(
        f"Potential Savings: "
        f"${results['savings']:,.2f}"
    )

    print(
        f"Savings Percentage: "
        f"{results['savings_percent']:.2f}%"
    )