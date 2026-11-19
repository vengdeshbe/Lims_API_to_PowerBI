# LIMS API to Power BI

This project extracts historical laboratory information management system (LIMS) data through a REST API, processes and cleans the response with Python and pandas, and exports a CSV file that can be loaded into Microsoft Power BI.

> [!IMPORTANT]
> The API endpoint and date range are currently configured directly in `historical_extraction.py`. Review both values before running the script, and do not commit API keys, passwords, internal hostnames, or laboratory data to GitHub.

## Features

- Requests historical data in smaller date batches
- Supports a configurable LIMS branch value in the JSON payload
- Parses and validates API responses
- Converts `Registration_date` to pandas datetime values
- Filters records from 1 January 2026 up to, but not including, 1 November 2026
- Removes:
  - Exact duplicate rows
  - Rows with blank sample numbers
  - All rows belonging to repeated sample numbers
  - The configured result-detail date columns
- Prints extraction, validation, and cleaning summaries
- Creates `cleaned_df_2026_till_oct.csv`

## Project Structure

```text
.
|-- historical_extraction.py  # Main API extraction and data-cleaning script
|-- test_python.py            # Python environment smoke-test script
|-- .gitignore                # Python, environment, and IDE exclusions
|-- LICENSE                   # MIT License
`-- README.md
```

## Requirements

- Python 3.9 or newer
- Internet access to the configured LIMS API
- Access permissions for the LIMS endpoint

Python packages:

- `requests`
- `pandas`

## Installation

Clone the repository and create a virtual environment:

```powershell
git clone https://github.com/<your-username>/Lims_API_to_PowerBI.git
cd Lims_API_to_PowerBI

python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install requests pandas
```

For Command Prompt:

```bat
.venv\Scripts\activate.bat
pip install requests pandas
```

You can verify the Python environment with:

```powershell
python test_python.py
```

## Configuration

Open `historical_extraction.py` and update the constants near the top of the file:

```python
API_URL = "https://your-lims-host/api/PowerBimisReport"

START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 11, 1)
```

The request payload is sent as:

```json
{
  "branch": 1,
  "FromDate": "2026-01-01",
  "ToDate": "2026-01-30"
}
```

Change `branch` if the API requires a different branch identifier.

The script uses 30-day batch limits and does not cross the configured `END_DATE`. A batch may finish at the end of a month or exactly 29 days after the batch start, whichever occurs first.

## Running the Extraction

From the repository directory, run:

```powershell
python historical_extraction.py
```

The script prints:

- The date range for each batch
- The number of records returned by each batch
- Any batch-level extraction errors
- Initial dataset date and sample-number validation
- Exact and repeated duplicate counts
- The cleaned-record summary

If one batch fails, the script continues with the next batch. The CSV can therefore contain data from successful batches only. Review the console output carefully before using the result in production.

## Output

The script creates:

```text
cleaned_df_2026_till_oct.csv
```

The CSV is written in the directory from which the script is run. It contains the cleaned records only and omits these columns when present:

- `Result_Received_Date`
- `Details_received_on`
- `Result_Entered_Date`

The script does not automatically create the CSV if the API response shape or required columns are unexpected, so preserve error output for troubleshooting.

## Cleaning Logic

1. Registration dates are parsed with `dayfirst=True`.
2. Records outside 1 January 2026 through 31 October 2026 are excluded.
3. `Sample_Number` values are converted to strings and trimmed.
4. Exact duplicate rows are removed.
5. Rows with missing or blank sample numbers are removed.
6. If a sample number occurs more than once, every row with that sample number is removed.
7. Configured date-detail columns are removed if they exist.

This strict sample-number strategy avoids uncertain matching. It removes both copies of a repeated sample number rather than keeping a single copy.

## Loading into Power BI Desktop

1. Open Power BI Desktop.
2. Select **Get data** > **Text/CSV**.
3. Select `cleaned_df_2026_till_oct.csv`.
4. Review the detected data types in the preview.
5. Select **Load** or open **Transform Data** to add further transformations.
6. Refresh the report after rerunning the Python script and replacing or updating the CSV.

For direct scheduling or repeated imports, use a dedicated service account and a secure process for storing API configuration. For Power BI Service scheduling, account for gateway and network access requirements.

## API Response Requirement

The script expects the successful JSON response to follow this shape:

```json
{
  "data": [
    {
      "result": [
        {
          "Registration_date": "01/01/2026",
          "Sample_Number": "SAMPLE-001"
        }
      ]
    }
  ]
}
```

Additional fields are kept in the DataFrame and written to the CSV. The script requires `Registration_date` for date filtering and handles `Sample_Number` during cleaning.

## Troubleshooting

### HTTP or authentication error

- Confirm that the endpoint is reachable.
- Confirm network, VPN, firewall, and certificate requirements.
- Confirm that the API accepts the `branch`, `FromDate`, and `ToDate` values.
- Increase or reduce the `timeout=120` value if appropriate.

### Unexpected JSON structure

The script currently assumes `result["data"][0]["result"]`. Compare the API response with the response shape documented above.

### Missing columns

Optional date-detail columns are ignored when absent. Required cleaning columns such as `Registration_date` and `Sample_Number` must exist in the API records.

### CSV has no or fewer records

- Review failed batch messages in the console.
- Verify the date range.
- Check that API records fall within the 2026-01-01 to 2026-10-31 date window.
- Remember that repeated sample numbers are removed in full.

## Security and Data Handling

- Laboratory records may contain personally identifiable or commercially sensitive information.
- Do not publish real API responses or CSV exports containing sensitive data.
- Add generated CSV files and local environment files to `.gitignore` where appropriate.
- Configure credentials through environment variables or a secrets manager instead of hardcoding them.
- Follow your organization's data-retention and access-control policies.

## License

This project is licensed under the [MIT License](LICENSE).
