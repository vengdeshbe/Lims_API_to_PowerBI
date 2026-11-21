from MODULE_dataframe_output import return_dataframe
import pandas as pd
from datetime import date, datetime

def validation(df,year):
    df["Registration_date"] = pd.to_datetime(df["Registration_date"],
                                         errors = "coerce",
                                         dayfirst=True)
    df_all_history = df.copy()


    
    print("="*60)
    print(f"\n{year} to till DATASET - INITIAL VALIDATION")
    print("="*60)
    print("Total records:", len(df_all_history))
    print("Minimum Registration Date:", df_all_history["Registration_date"].min())
    print("Maximum Registration Date:", df_all_history["Registration_date"].max())



    # ==========================================
    # SAMPLE NUMBER VALIDATION
    # ==========================================

    sample_numbers = df_all_history["Sample_Number"].astype("string").str.strip()

    valid_sample_numbers = sample_numbers[
        sample_numbers.notna() & sample_numbers.ne("")
    ]

    print("\n" + "=" * 60)
    print("SAMPLE NUMBER VALIDATION")
    print("=" * 60)

    print("Total records:", len(df_all_history))

    print("Blank Sample Numbers:",
        (sample_numbers.isna() | sample_numbers.eq("")).sum())

    print("Distinct Sample Numbers:",
        valid_sample_numbers.nunique())

    print("Repeated Sample Number rows:",
        valid_sample_numbers.duplicated().sum())


    repeated_sample_numbers = valid_sample_numbers[valid_sample_numbers.duplicated()]
    repeated_records = df_all_history[df_all_history["Sample_Number"].isin(repeated_sample_numbers)].copy()
    repeated_sample_records = repeated_records[[
            "Sample_Number",
            "Client_Name",
            "Sample_Name",
            "Registration_date",
            "Department",
            "Reporting_Date"
        ]].sort_values("Sample_Number")

    print("\n repeated sample records: ",
        repeated_sample_records)

    print("\n Exact Duplicates record: ",
        df_all_history.duplicated().sum())


    # ==========================================
    # STEP 3: CREATE CLEANED current year DATASET
    # ==========================================

    df_all_history_clean = df_all_history.copy()

    # 1. Normalize Sample Numbers
    df_all_history_clean["Sample_Number"] = (
        df_all_history_clean["Sample_Number"]
        .astype("string")
        .str.strip()
    )

    # 2. Remove exact duplicate rows
    before = len(df_all_history_clean)

    df_all_history_clean = df_all_history_clean.drop_duplicates()

    exact_removed = before - len(df_all_history_clean)

    # 3. Remove blank Sample Numbers
    blank_mask = (
        df_all_history_clean["Sample_Number"].isna()
        | df_all_history_clean["Sample_Number"].eq("")
    )

    blank_removed = blank_mask.sum()

    df_all_history_clean = df_all_history_clean.loc[~blank_mask].copy()

    # 4. Identify and remove all repeated Sample Numbers
    duplicate_mask = df_all_history_clean["Sample_Number"].duplicated(
        keep=False
    )

    duplicate_ids = (
        df_all_history_clean.loc[duplicate_mask, "Sample_Number"]
        .unique()
    )

    duplicate_removed = duplicate_mask.sum()

    df_all_history_clean = df_all_history_clean.loc[
        ~df_all_history_clean["Sample_Number"].isin(duplicate_ids)
    ].copy()

    # 5. Remove unnecessary columns
    columns_to_remove = [
        "Result_Received_Date",
        "Details_received_on",
        "Result_Entered_Date"
    ]

    df_all_history_clean = df_all_history_clean.drop(
        columns=columns_to_remove,
        errors="ignore"
    )
    df_all_history_clean["Results_Entered_By"] = df_all_history_clean["Results_Entered_By"].astype("string").str.strip().str.replace(",", ":")

    # ==========================================
    # CLEANING SUMMARY
    # ==========================================

    print("\n" + "=" * 55)
    print(f"{year} DATA CLEANING SUMMARY")
    print("=" * 55)

    print("Original records:", len(df_all_history))
    print("Exact duplicate rows removed:", exact_removed)
    print("Blank Sample Number rows removed:", blank_removed)
    print("Repeated Sample Number rows removed:", duplicate_removed)
    print("Final cleaned records:", len(df_all_history_clean))

    print("\nFINAL VALIDATION")
    print("Unique Sample Numbers:", df_all_history_clean["Sample_Number"].nunique())
    print("Remaining duplicate Sample Numbers:",
        df_all_history_clean["Sample_Number"].duplicated().sum())
    print("Remaining blank Sample Numbers:",
        df_all_history_clean["Sample_Number"].isna().sum()
        + df_all_history_clean["Sample_Number"].eq("").sum())

    print("Sample Number is unique:",
        df_all_history_clean["Sample_Number"].is_unique)

    from pathlib import Path
    from datetime import datetime

    # Get current year dynamically
    current_year = datetime.now().year

    # Generate dynamic filename
    file_name = f"Cleaned_Data_LIMS_{current_year}.csv"

    # Save CSV in the same folder
    output_file = Path(__file__).resolve().parent / file_name

    df_all_history_clean.to_csv(output_file, index=False)

    print(f"{file_name} file has been created successfully.")

    return df_all_history_clean