from datetime import date


def api_requirements():
    API_URL = "https://blr-eureka.enso-lims.com/blrapi/api/PowerBimisReport"

    HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    STARTDATE = date(2026, 1, 1)

    ENDDATE = date(2026, 11, 1)

    return API_URL, HEADERS , STARTDATE, ENDDATE


