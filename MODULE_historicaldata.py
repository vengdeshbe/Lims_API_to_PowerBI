import requests
from datetime import date, timedelta
import calendar

from MODULE_config import api_requirements


def historical_data_extraction():

    API_URL, HEADERS, STARTDATE, ENDDATE = api_requirements()
    START_DATE = STARTDATE
    END_DATE = ENDDATE

    all_records = []


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

    return all_records