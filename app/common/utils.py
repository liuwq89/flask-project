import os
import json
import shutil
import hashlib
from datetime import datetime
from typing import Union, Optional


def loads_json_str(
        json_data: Optional[Union[str, bytes, dict, list]]
    ) -> Union[dict, list]:
    """
    Parse JSON string/bytes into a Python dict or list.

    Args:
        json_data (str | bytes | dict | list | None): Input JSON.

    Returns:
        dict | list: Parsed Python object, or empty dict if invalid.
    """
    if json_data:
        if isinstance(json_data, (str, bytes)):
            return json.loads(json_data)
        if isinstance(json_data, (dict, list)):
            return json_data
    return {}


def dumps_json_str(
        data: Optional[Union[dict, list]],
        ensure_ascii: bool = False,
        indent: Optional[int] = None
    ) -> str:
    """
    Serialize Python dict or list to JSON string.

    Args:
        data (dict | list | None): Python object to serialize.
        ensure_ascii (bool): If False, output will contain non-ASCII characters.
        indent (int | None): If set, JSON will be pretty-printed with this indentation.

    Returns:
        str: JSON-formatted string. Returns '{}' if input is invalid.
    """
    if data is None:
        return '{}'
    return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)


def get_md5(
        data: Union[str, bytes],
        cut_num: int = 100
    ) -> str:
    """
    Calculate MD5 hash for a string or bytes.

    Args:
        data (str | bytes): Input data.
        cut_num (int): Number of characters to return from the hash.

    Returns:
        str: MD5 hash string, truncated to `cut_num` characters.
    """
    if not isinstance(data, bytes):
        data = data.encode('utf-8')
    return hashlib.md5(data).hexdigest()[:cut_num]


def get_file_md5(file, cut_num: int = 32) -> str:
    """
    Calculate MD5 hash of a file-like object.

    Args:
        file: File-like object opened in binary/text mode.
        cut_num (int): Number of characters to return from the hash.

    Returns:
        str: MD5 hash string.
    """
    file.seek(0)
    file_content = file.read()
    file.seek(0)
    return get_md5(file_content, cut_num)


def remove_file_or_dir(path: str) -> None:
    """
    Remove a file, symbolic link, or directory if it exists.

    Args:
        path (str): Path to file or directory.

    Returns:
        None
    """
    if path and os.path.exists(path):
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)


def timestamp_to_date_str(timestamp: int, date_format: int = 1) -> str:
    """
    Convert a timestamp to a formatted date string.

    Args:
        timestamp (int): Unix timestamp.
        date_format (int): 1 for 'YYYY-MM-DD HH:MM:SS', else 'YYYY-MM-DD'.

    Returns:
        str: Formatted date string.
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S' if date_format == 1 else '%Y-%m-%d')


def date_to_timestamp(time: Union[datetime, str], date_format: str) -> int:
    """
    Convert a datetime object or a date string to Unix timestamp.

    Args:
        time (datetime | str): Date input.
        date_format (str): Format to parse the string if `time` is str.

    Returns:
        int: Unix timestamp.

    Raises:
        TypeError: If `time` is neither str nor datetime.
    """
    if isinstance(time, datetime):
        return int(time.timestamp())
    if isinstance(time, str):
        if time.isdigit():
            return int(time)
        return int(datetime.strptime(time, date_format).timestamp())
    raise TypeError("Unsupported time type, must be datetime or str.")








