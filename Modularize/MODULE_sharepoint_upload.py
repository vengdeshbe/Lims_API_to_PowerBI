
import os
from pathlib import Path
from urllib.parse import quote

import requests
import msal
from dotenv import load_dotenv


# Load SharePoint credentials
BASE_DIR = Path(__file__).resolve().parent

env_path = BASE_DIR / "sharepoint_config.env"

if not env_path.exists():
    env_path = BASE_DIR.parent / "sharepoint_config.env"

load_dotenv(env_path)

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

SITE_HOST = "eurekaserv.sharepoint.com"
SITE_PATH = "/sites/Bangalore_MIS"
LIBRARY_NAME = "LIMS_Data"


def get_access_token():

    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )

    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    if "access_token" not in result:
        raise Exception(
            f"Authentication failed: {result.get('error_description')}"
        )

    return result["access_token"]


def upload_file_to_sharepoint(
    local_file_path,
    folder_path="Staging",
    file_name=None
):

    local_file_path = Path(local_file_path)

    if not local_file_path.exists():
        raise FileNotFoundError(
            f"File not found: {local_file_path}"
        )

    if not all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        raise ValueError("SharePoint credentials are missing.")

    if file_name is None:
        file_name = local_file_path.name

    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Get SharePoint site ID
    site_url = (
        f"https://graph.microsoft.com/v1.0/sites/"
        f"{SITE_HOST}:{SITE_PATH}?$select=id"
    )

    site_response = requests.get(
        site_url, headers=headers, timeout=60
    )
    site_response.raise_for_status()

    site_id = site_response.json()["id"]

    # Find LIMS_Data document library
    drives_url = (
        f"https://graph.microsoft.com/v1.0/sites/"
        f"{site_id}/drives"
    )

    drives_response = requests.get(
        drives_url, headers=headers, timeout=60
    )
    drives_response.raise_for_status()

    drives = drives_response.json()["value"]

    drive = next(
        (d for d in drives if d["name"] == LIBRARY_NAME),
        None
    )

    if drive is None:
        raise Exception(
            f"Document library '{LIBRARY_NAME}' not found."
        )

    drive_id = drive["id"]

    # Prepare destination path
    remote_path = f"{folder_path.strip('/')}/{file_name}"
    encoded_path = quote(remote_path, safe="/")

    upload_url = (
        f"https://graph.microsoft.com/v1.0/drives/"
        f"{drive_id}/root:/{encoded_path}:/content"
    )

    # Upload or replace existing file
    with open(local_file_path, "rb") as file:
        upload_response = requests.put(
            upload_url,
            headers=headers,
            data=file,
            timeout=300
        )

    upload_response.raise_for_status()

    print("SharePoint upload/replacement successful!")
    print("File:", file_name)
    print("Folder:", folder_path)
    print("HTTP Status:", upload_response.status_code)

    return upload_response.json()
