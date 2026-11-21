
from pathlib import Path
from datetime import datetime

from MODULE_historicaldata import historical_data_extraction
from MODULE_dataframe_output import return_dataframe
from MODULE_data_validation import validation
from MODULE_sharepoint_upload import upload_file_to_sharepoint


print("=" * 60)
print("LIMS DATA PIPELINE STARTED")
print("=" * 60)


# STEP 1: Extract data from LIMS API
print("\nSTEP 1: Extracting historical data...")

history_data_list = historical_data_extraction()


# STEP 2: Convert API response into DataFrame
print("\nSTEP 2: Creating DataFrame...")

df = return_dataframe(history_data=history_data_list)


# STEP 3: Validate and clean data
print("\nSTEP 3: Validating and cleaning data...")
year = datetime.now().year
cleaned_df = validation(df=df,year=year)


# STEP 4: Final quality checks
print("\nSTEP 4: Performing final quality checks...")

if cleaned_df is None or cleaned_df.empty:
    raise ValueError("Validation failed: Cleaned DataFrame is empty.")

if "Sample_Number" not in cleaned_df.columns:
    raise ValueError("Validation failed: Sample_Number column is missing.")

sample_numbers = cleaned_df["Sample_Number"].astype("string").str.strip()

if sample_numbers.isna().any() or sample_numbers.eq("").any():
    raise ValueError("Validation failed: Blank Sample Numbers found.")

if sample_numbers.duplicated().any():
    raise ValueError("Validation failed: Duplicate Sample Numbers found.")

print("Final validation successful!")
print("Total valid records:", len(cleaned_df))


# STEP 5: Upload cleaned CSV to SharePoint Staging
print("\nSTEP 5: Uploading cleaned data to SharePoint...")

BASE_DIR = Path(__file__).resolve().parent

year = datetime.now().year

csv_file = BASE_DIR / f"Cleaned_data_Lims_{year}.csv"

filename = f"Cleaned_data_Lims_{year}.csv"

upload_file_to_sharepoint(
    local_file_path=csv_file,
    folder_path="Curated_Data",
    file_name=filename
)


print("\n" + "=" * 60)
print("LIMS DATA PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 60)
