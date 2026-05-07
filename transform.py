"""
This script transforms and cleans hiking data.
Takes the two dataframes as input (trails and hazards)
As output, it gives the cleaned/transformed dataframe with both datasets combined
and exports cleaned data as a csv
"""

import os

import pandas as pd

# Columns the rest of this file expects (avoids cryptic KeyErrors if CSVs change).
_TRAILS_COLUMNS_NEEDED = [
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
]
_HAZARDS_COLUMNS_NEEDED = [
    "Name",
    "Rattlesnakes",
    "Ticks",
    "Posionivy",
    "Falling",
]


# Helper function to extract the first number from a string
def extract_first_number(value):
    if pd.isna(value):
        return None

    text_value = str(value).replace(",", "")
    clean_text = ""

    for char in text_value:
        if char.isdigit() or char == ".":
            clean_text = clean_text + char
        elif clean_text != "":
            break

    if clean_text != "":
        return float(clean_text)
    return None


# Helper function to clean trail names for matching and eventually merging
def make_trail_name_key(value):
    if pd.isna(value):
        return ""

    text_value = str(value).strip().lower()
    text_value = " ".join(text_value.split())
    return text_value


# Helper function to standardize Yes/No style values
def clean_yes_no_value(value):
    if pd.isna(value):
        return "Unknown"

    text_value = str(value).strip().lower()

    if text_value in ["yes", "y", "true", "1"]:
        return "Yes"
    if text_value in ["no", "n", "false", "0"]:
        return "No"
    if text_value in ["es", "o"]:
        return "Unknown"

    yes_words = ["yes", "older kids", "on ", "crowded", "very", "sometimes", "group tour"]
    no_words = ["no", "not", "never", "too long"]

    for word in yes_words:
        if word in text_value:
            return "Yes"

    for word in no_words:
        if word in text_value:
            return "No"

    return "Unknown"


def transform(df_hiking_trails, df_trail_hazards):
    missing_trails = [
        col
        for col in _TRAILS_COLUMNS_NEEDED
        if col not in df_hiking_trails.columns
    ]
    missing_hazards = [
        col
        for col in _HAZARDS_COLUMNS_NEEDED
        if col not in df_trail_hazards.columns
    ]
    if missing_trails or missing_hazards:
        if missing_trails:
            print(
                "Transform stopped: hiking trails CSV is missing columns:",
                missing_trails,
            )
        if missing_hazards:
            print(
                "Transform stopped: hazards CSV is missing columns:",
                missing_hazards,
            )
        return None

    trails = df_hiking_trails.copy()
    hazards = df_trail_hazards.copy()

    # Normalize trail names and build simple merge keys
    trails["Trail Name"] = trails["Trail Name"].astype(str).str.strip()
    hazards["Name"] = hazards["Name"].astype(str).str.strip()

    trails["trail_name_key"] = trails["Trail Name"].apply(make_trail_name_key)
    hazards["trail_name_key"] = hazards["Name"].apply(make_trail_name_key)

    # Remove unnecessary row in hazards dataframe
    hazards = hazards[hazards["trail_name_key"] != "hike"]

    # Match key with trails for merging later
    hazards = hazards.rename(columns={"Name": "Trail Name"})

    # Merge into the main trail dataframe
    df = pd.merge(
        trails,
        hazards[["trail_name_key", "Rattlesnakes", "Ticks", "Posionivy", "Falling"]],
        on="trail_name_key",
        how="left",
    )

    # Clean hazard columns, then convert to Yes/No text
    hazard_columns = ["Rattlesnakes", "Ticks", "Posionivy", "Falling"]
    for col in hazard_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Summary column from hazard values
    hazardous_values = []
    for _, row in df.iterrows():
        total_hazards = (
            row["Rattlesnakes"] + row["Ticks"] + row["Posionivy"] + row["Falling"]
        )
        if total_hazards > 0:
            hazardous_values.append("Yes")
        else:
            hazardous_values.append("No")
    df["Hazardous"] = hazardous_values

    # Make hazard columns match other Yes/No style fields
    for col in hazard_columns:
        df[col] = df[col].replace({1: "Yes", 0: "No"})

    # Standardize the existing Yes and No columns
    yes_no_columns = ["Family Friendly", "Backpackable", "Crowded"]
    for col in yes_no_columns:
        cleaned_values = []
        for value in df[col]:
            cleaned_values.append(clean_yes_no_value(value))
        df[col] = cleaned_values
        
    
    # Replace original numeric-like columns with cleaned numeric values
    df["Distance"] = df["Distance"].apply(extract_first_number)
    df["High Point"] = df["High Point"].apply(extract_first_number)
    df["Elevation Gain"] = df["Elevation Gain"].apply(extract_first_number)

    # Handle missing values
    text_columns = [
        "Trail Type",
        "Difficulty",
        "Seasons",
        "Family Friendly",
        "Backpackable",
        "Crowded",
    ]
    for col in text_columns:
        df[col] = df[col].fillna("Unknown")

    df["Distance"] = df["Distance"].fillna(0)
    df["High Point"] = df["High Point"].fillna(0)
    df["Elevation Gain"] = df["Elevation Gain"].fillna(0)

    # Rename hazard columns to clearer names
    df = df.rename(
        columns={
            "Ticks": "Has Ticks",
            "Posionivy": "Has Poison Ivy",
            "Falling": "Risk of Falling",
            "Rattlesnakes": "Has Rattlesnakes",
        }
    )

    # Move Hazardous so it appears before all individual hazard columns
    hazard_detail_columns = [
        "Has Rattlesnakes",
        "Has Ticks",
        "Has Poison Ivy",
        "Risk of Falling",
    ]
    hazardous_col = df.pop("Hazardous")
    insert_index = df.columns.get_loc(hazard_detail_columns[0])
    df.insert(insert_index, "Hazardous", hazardous_col)

    # Standardize "Trail Type" data
    trail_type_clean = []
    for value in df["Trail Type"]:
        value_text = str(value).strip().lower()

        if "loop" in value_text:
            trail_type_clean.append("Loop")
        elif "out and back" in value_text or "out-and-back" in value_text or "in and out" in value_text:
            trail_type_clean.append("Out and Back")
        elif "point to point" in value_text or "traverse" in value_text or "shuttle" in value_text:
            trail_type_clean.append("Point to Point")
        else:
            trail_type_clean.append("Other")
    df["Trail Type"] = trail_type_clean

    # Standardize "Seasons" data
    season_clean = []
    for value in df["Seasons"]:
        value_text = str(value).strip().lower()

        if "all year" in value_text or "all season" in value_text or value_text == "all":
            season_clean.append("All year")
        elif "year round" in value_text or "year-round" in value_text or "year round" in value_text:
            season_clean.append("All year")
        elif "spring" in value_text and "fall" in value_text:
            season_clean.append("Spring to Fall")
        elif "summer" in value_text and "fall" in value_text:
            season_clean.append("Summer to Fall")
        elif "apr" in value_text or "may" in value_text or "oct" in value_text or "nov" in value_text:
            season_clean.append("Seasonal")
        else:
            season_clean.append("Unknown")
    df["Seasons"] = season_clean

    # Standardize "Difficulty" data
    difficulty_clean = []
    for value in df["Difficulty"]:
        value_text = str(value).strip().lower()

        if "easy" in value_text:
            difficulty_clean.append("Easy")
        elif "moderate" in value_text:
            difficulty_clean.append("Moderate")
        elif "difficult" in value_text:
            difficulty_clean.append("Difficult")
        else:
            difficulty_clean.append("Unknown")
    df["Difficulty"] = difficulty_clean

    # Remove helper merge key before exporting
    df = df.drop(columns=["trail_name_key"])

    # Complete process. Exports cleaned CSV, then passes on the dataframe for load.py
    processed_path = "data/processed/trails_clean.csv"
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.to_csv(processed_path, index=False)
    print("Transformation complete.")
    return df
