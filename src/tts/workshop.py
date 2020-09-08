from typing import Any, Dict, cast

import bson
import requests

FILE_DETAILS_URL = (
    "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
)


def _get_file_details(fileid: int) -> Dict[str, Any]:
    response = requests.post(
        FILE_DETAILS_URL,
        data={"publishedfileids[0]": fileid, "itemcount": 1},
    )
    response.raise_for_status()
    # Get the only details returned
    [details] = response.json()["response"]["publishedfiledetails"]
    return cast(Dict[str, Any], details)


def get_workshop_mod(fileid: int) -> Dict[Any, Any]:
    details = _get_file_details(fileid)
    file_url = details["file_url"]
    response = requests.get(file_url)
    response.raise_for_status()
    return bson.loads(response.content)
