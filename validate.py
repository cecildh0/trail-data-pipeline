"""
Validation checks for transformed trail data.
Raises ValueError if important checks fail.
"""


def validate(df):
    if df is None:
        print("Validation skipped: no dataframe to check.")
        return

    if len(df) == 0:
        print("Validation skipped: no rows in dataframe.")
        return

    # Required output columns we expect after transform
    required_columns = [
        "Trail Name",
        "Trail Type",
        "Distance",
        "High Point",
        "Elevation Gain",
        "Difficulty",
        "Seasons",
        "Family Friendly",
        "Backpackable",
        "Crowded",
        "Hazardous",
        "Has Rattlesnakes",
        "Has Ticks",
        "Has Poison Ivy",
        "Risk of Falling",
    ]

    # Ensure required columns exist
    missing_columns = []
    for col in required_columns:
        if col not in df.columns:
            missing_columns.append(col)
    if len(missing_columns) > 0:
        raise ValueError(f"Validation failed: missing columns: {missing_columns}")

    # Ensure trail names are not blank
    blank_trail_names = 0
    for value in df["Trail Name"]:
        if value is None:
            blank_trail_names += 1
        elif str(value).strip() == "":
            blank_trail_names += 1
    if blank_trail_names > 0:
        raise ValueError(
            f"Validation failed: found {blank_trail_names} blank Trail Name values."
        )

    # Ensure Yes/No style columns only contain expected values
    yes_no_columns = [
        "Family Friendly",
        "Backpackable",
        "Crowded",
        "Has Rattlesnakes",
        "Hazardous",
        "Has Ticks",
        "Has Poison Ivy",
        "Risk of Falling",
    ]
    allowed_values = ["Yes", "No", "Unknown"]

    for col in yes_no_columns:
        invalid_count = 0
        for value in df[col]:
            if value not in allowed_values:
                invalid_count += 1
        if invalid_count > 0:
            raise ValueError(
                f"Validation failed: column '{col}' has {invalid_count} invalid values."
            )

    print("Validation passed.")
