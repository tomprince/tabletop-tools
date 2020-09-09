from pathlib import Path

from steam.client import SteamClient
from steam.enums.common import EResult

from ..config import APPID, appdirs
from ._upload import upload_file

__all__ = ["cli_login", "update_file", "upload_file"]


def cli_login() -> SteamClient:
    cache_dir = Path(appdirs.user_cache_dir)
    client = SteamClient()
    client.credential_location = cache_dir.joinpath("steam")
    res = client.cli_login()
    if res != EResult.OK:
        raise Exception(f"Could not login: {res.name}")

    return client


def update_file(client: SteamClient, file_id: int, file_name: str) -> None:
    resp = client.send_um_and_wait(
        "PublishedFile.Update#1",
        {
            "appid": APPID,
            "publishedfileid": file_id,
            "filename": file_name,
        },
    )
    if resp.header.eresult != EResult.OK:
        raise Exception(f"Couldn't publish file: {EResult(resp.header.eresult).name}")
