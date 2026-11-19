
import requests
import pandas as pd
from datetime import date, timedelta
import calendar
from Markdown import log_historical_extraction

# =====================================================
# API CONFIGURATION
# =====================================================

API_URL = "https://blr-eureka.enso-lims.com/blrapi/api/PowerBimisReport"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 11, 1)

all_records = []

# =====================================================
# HISTORICAL DATA EXTRACTION
# =====================================================

current_date = START_DATE

batch_number = 1

while current_date <= END_DATE:

    last_day = calendar.monthrange(
        current_date.year,
        current_date.month
    )[1]

    month_end = date(
        current_date.year,
        current_date.month,
        last_day
    )

    batch_end = min(
        month_end,
        current_date + timedelta(days=29),
        END_DATE
    )

    from_date = current_date.strftime("%Y-%m-%d")
    to_date = batch_end.strftime("%Y-%m-%d")

    print("\n" + "=" * 60)
    print(f"PROCESSING BATCH {batch_number}")
    print(f"FromDate: {from_date}")
    print(f"ToDate: {to_date}")
    print("=" * 60)

    payload = {
        "branch": 1,
        "FromDate": from_date,
        "ToDate": to_date
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=HEADERS,
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        records = result["data"][0]["result"]

        print("Records received:", len(records))

        all_records.extend(records)

    except Exception as e:
        print("ERROR in batch:", batch_number)
        print("Error details:", e)

    current_date = batch_end + timedelta(days=1)
    batch_number += 1


# =====================================================
# COMBINE ALL RECORDS
# =====================================================

df = pd.DataFrame(all_records)

df["Registration_date"] = pd.to_datetime(df["Registration_date"],
                                         errors = "coerce",
                                         dayfirst=True)
df_2026_till_oct = df[(df["Registration_date"]>="2026-01-01")
                        & (df["Registration_date"]<"2026-11-01")].copy()

print("="*60)
print("\n2026 till oct DATASET - INITIAL VALIDATION")
print("="*60)
print("Total records:", len(df_2026_till_oct))
print("Minimum Registration Date:", df_2026_till_oct["Registration_date"].min())
print("Maximum Registration Date:", df_2026_till_oct["Registration_date"].max())



# ==========================================
# SAMPLE NUMBER VALIDATION
# ==========================================

sample_numbers = df_2026_till_oct["Sample_Number"].astype("string").str.strip()

valid_sample_numbers = sample_numbers[
    sample_numbers.notna() & sample_numbers.ne("")
]

print("\n" + "=" * 60)
print("SAMPLE NUMBER VALIDATION")
print("=" * 60)

print("Total records:", len(df_2026_till_oct))

print("Blank Sample Numbers:",
      (sample_numbers.isna() | sample_numbers.eq("")).sum())

print("Distinct Sample Numbers:",
      valid_sample_numbers.nunique())

print("Repeated Sample Number rows:",
      valid_sample_numbers.duplicated().sum())


repeated_sample_numbers = valid_sample_numbers[valid_sample_numbers.duplicated()]
repeated_records = df_2026_till_oct[df_2026_till_oct["Sample_Number"].isin(repeated_sample_numbers)].copy()
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
      df_2026_till_oct.duplicated().sum())


# ==========================================
# STEP 3: CREATE CLEANED 2026 DATASET
# ==========================================

df_2026_till_oct_clean = df_2026_till_oct.copy()

# 1. Normalize Sample Numbers
df_2026_till_oct_clean["Sample_Number"] = (
    df_2026_till_oct_clean["Sample_Number"]
    .astype("string")
    .str.strip()
)

# 2. Remove exact duplicate rows
before = len(df_2026_till_oct_clean)

df_2026_till_oct_clean = df_2026_till_oct_clean.drop_duplicates()

exact_removed = before - len(df_2026_till_oct_clean)

# 3. Remove blank Sample Numbers
blank_mask = (
    df_2026_till_oct_clean["Sample_Number"].isna()
    | df_2026_till_oct_clean["Sample_Number"].eq("")
)

blank_removed = blank_mask.sum()

df_2026_till_oct_clean = df_2026_till_oct_clean.loc[~blank_mask].copy()

# 4. Identify and remove all repeated Sample Numbers
duplicate_mask = df_2026_till_oct_clean["Sample_Number"].duplicated(
    keep=False
)

duplicate_ids = (
    df_2026_till_oct_clean.loc[duplicate_mask, "Sample_Number"]
    .unique()
)

duplicate_removed = duplicate_mask.sum()

df_2026_till_oct_clean = df_2026_till_oct_clean.loc[
    ~df_2026_till_oct_clean["Sample_Number"].isin(duplicate_ids)
].copy()

# 5. Remove unnecessary columns
columns_to_remove = [
    "Result_Received_Date",
    "Details_received_on",
    "Result_Entered_Date"
]

df_2026_till_oct_clean = df_2026_till_oct_clean.drop(
    columns=columns_to_remove,
    errors="ignore"
)
df_2026_till_oct_clean["Results_Entered_By"] = df_2026_till_oct_clean["Results_Entered_By"].astype("string").str.strip().str.replace(",", ":")

# ==========================================
# CLEANING SUMMARY
# ==========================================

print("\n" + "=" * 55)
print("2026 DATA CLEANING SUMMARY")
print("=" * 55)

print("Original records:", len(df_2026_till_oct))
print("Exact duplicate rows removed:", exact_removed)
print("Blank Sample Number rows removed:", blank_removed)
print("Repeated Sample Number rows removed:", duplicate_removed)
print("Final cleaned records:", len(df_2026_till_oct_clean))

print("\nFINAL VALIDATION")
print("Unique Sample Numbers:", df_2026_till_oct_clean["Sample_Number"].nunique())
print("Remaining duplicate Sample Numbers:",
      df_2026_till_oct_clean["Sample_Number"].duplicated().sum())
print("Remaining blank Sample Numbers:",
      df_2026_till_oct_clean["Sample_Number"].isna().sum()
      + df_2026_till_oct_clean["Sample_Number"].eq("").sum())

print("Sample Number is unique:",
      df_2026_till_oct_clean["Sample_Number"].is_unique)

df_2026_till_oct_clean.to_csv("cleaned_df_2026_till_oct.csv", index=False)

print("cleaned_df_2026_till_oct.csv file has been created successfully.")

log_historical_extraction(record_count=len(df_2026_till_oct))

print("historical_extraction_log.md file has been created successfully.")