import hashlib
import time

import requests
from steam.client import SteamClient
from steam.enums.common import EResult
from steam.protobufs.steammessages_cloud_pb2 import ClientCloudFileUploadBlockDetails

from ..config import APPID


def _hash_sha1(data: bytes) -> bytes:
    m = hashlib.sha1()
    m.update(data)
    return m.digest()


def upload_file(client: SteamClient, file_name: str, file_data: bytes) -> None:
    file_sha = _hash_sha1(file_data)
    resp = client.send_um_and_wait(
        "Cloud.ClientBeginFileUpload#1",
        {
            "appid": APPID,
            "file_size": len(file_data),
            "raw_file_size": len(file_data),
            "file_sha": file_sha,
            "filename": file_name,
            "can_encrypt": False,
            "time_stamp": int(time.time()),
            "is_shared_file": False,
        },
    )
    if resp.header.eresult == EResult.DuplicateRequest:
        # Already uploaded.
        return
    if resp.header.eresult != EResult.OK:
        raise Exception(f"Couldn't start upload: {EResult(resp.header.eresult).name}")
    try:
        for block_request in resp.body.block_requests:
            _upload_block(block_request, file_data)
    except Exception:
        client.send_um_and_wait(
            "Cloud.ClientCommitFileUpload#1",
            {
                "appid": APPID,
                "filename": file_name,
                "file_sha": file_sha,
                "transfer_succeeded": False,
            },
        )
        raise
    else:
        resp = client.send_um_and_wait(
            "Cloud.ClientCommitFileUpload#1",
            {
                "appid": APPID,
                "filename": file_name,
                "file_sha": file_sha,
                "transfer_succeeded": True,
            },
        )
        if resp.header.eresult != EResult.OK:
            raise Exception(
                f"Couldn't commit upload: {EResult(resp.header.eresult).name}"
            )


def _upload_block(
    block_request: ClientCloudFileUploadBlockDetails, file_data: bytes
) -> None:
    url = f"https://{block_request.url_host}{block_request.url_path}"
    headers = {}
    for header in block_request.request_headers:
        if header.name == "Content-Disposition":
            headers[header.name] = header.value.rstrip(";")
        else:
            headers[header.name] = header.value
    block_end = block_request.block_offset + block_request.block_length
    block_data = file_data[block_request.block_offset : block_end]
    headers["Content-Length"] = f"{block_request.block_length}"
    headers[
        "Content-Range"
    ] = f"bytes {block_request.block_offset}-{block_end}/{len(file_data)}"
    response = requests.put(url, headers=headers, data=block_data)
    response.raise_for_status()
