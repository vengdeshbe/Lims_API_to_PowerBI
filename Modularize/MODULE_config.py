from datetime import date


def api_requirements():
    API_URL = "https://blr-eureka.enso-lims.com/blrapi/api/PowerBimisReport"

    HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    today = date.today()

    STARTDATE = date(today.year,1,1)

    ENDDATE = today

    return API_URL, HEADERS , STARTDATE, ENDDATE


