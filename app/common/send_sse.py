import json
from typing import Optional, Union


def send_sse_msg(data: Optional[Union[str, bytes, dict]]) -> str:
    """send sse message data."""
    if not data:
        data = {}
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False)
    return f"event: message\ndata: {data}\n\n"

def send_sse_done() -> str:
    """send sse end flag data."""
    return "event: done\ndata: [DONE]\n\n"

def send_sse_err(code=0, msg="请求失败", data=None) -> str:
    """send sse error data."""
    result = {
        "code": code,
        "message": msg,
        "data": data if data is not None else {}
    }
    result_json = json.dumps(result, ensure_ascii=False)
    return f"event: error\ndata: {result_json}"


__all__ = ["send_sse_msg", "send_sse_done", "send_sse_err"]



