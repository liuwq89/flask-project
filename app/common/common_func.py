from datetime import datetime
from typing import Union, Tuple, Any, Literal

from flask import jsonify
from flask import Response

from app.common import constants
from app.common.utils import loads_json_str, dumps_json_str


def __process_query_item_data(
        item,
        *,
        date_format: Literal[0, 1] = 1,
        item_features: list = [],
        json_load_features: list = [],
        json_dump_features: list = [],
    ) -> dict:
    """
    将单条数据对象转换为标准 JSON 字典结构.

    Args:
        item: 原始数据项，可以是对象或 dict.
        date_format: 日期格式化方式, 0 为 'YYYY-MM-DD', 1 为 'YYYY-MM-DD HH:MM:SS'.
        item_features: 要提取的字段名列表；若为 None 则自动过滤私有属性.
        json_load_features: 需要反序列化 JSON 的字段名.
        json_dump_features: 需要序列化为 JSON 字符串的字段名.

    Returns:
        dict: 单条数据格式化后的结果.
    """
    format_result = {}
    if not item:
        return format_result
    if not item_features:
        item_features = [
            attr for attr in dir(item)
            if not attr.startswith('_') and attr not in constants.DB_QUERY_OBJ_ATTRS
        ]
    for feature in item_features:
        if isinstance(item, dict) and feature in item:
            feature_value = item.get(feature)
        elif hasattr(item, feature):
            feature_value = getattr(item, feature)
        else:
            continue

        if feature_value == None:
            format_result[feature] = feature_value
            continue

        if feature in json_load_features:
            feature_value = loads_json_str(feature)
            # if feature_value == "":
            #     feature_value = {}
            # elif not isinstance(feature_value, dict) and not isinstance(feature_value, list):
            #     feature_value = json.loads(feature_value)
                
        if feature in json_dump_features:
            feature_value = dumps_json_str(feature)
            # if feature_value == "":
            #     feature_value = "{}"
            # elif isinstance(feature_value, dict) or isinstance(feature_value, list):
            #     feature_value = json.dumps(feature_value)
        
        if isinstance(feature, datetime):
            format_result[feature] = feature_value.strftime(
                '%Y-%m-%d %H:%M:%S' if date_format == 1 else '%Y-%m-%d'
            )
        else:
            format_result[feature] = feature_value
    return format_result


def query_data_process(
        data: Union[Tuple[Any, ...], Any],
        *,
        date_format: Literal[0, 1] = 1,
        data_features: list = [],
        json_load_features: list = [],
        json_dump_features: list = [],
    ) -> Union[dict, list]:
    """
    处理查询结果数据, 支持单条或多条数据的格式化, 将单条数据对象转换为标准 JSON 字典结构.

    Args:
        data: 原始数据集，可以是单条或多条数据.
        date_format: 日期格式化方式, 0 为 'YYYY-MM-DD', 1 为 'YYYY-MM-DD HH:MM:SS'.
        item_features: 要提取的字段名列表；若为 None 则自动过滤私有属性.
        json_load_features: 需要反序列化 JSON 的字段名.
        json_dump_features: 需要序列化为 JSON 字符串的字段名.

    Returns:
        list: 多条数据格式化后的结果.
        dict: 单条数据格式化后的结果.
    """
    if isinstance(data, list):
        return [
            __process_query_item_data(
                item,
                date_format,
                data_features,
                json_load_features,
                json_dump_features
            )
            for item in data
        ]
    else:
        return __process_query_item_data(
            data,
            date_format,
            data_features,
            json_load_features,
            json_dump_features
        )


def http_resp(code=1, message="请求成功", data=None, *, request_id=None, status=200) -> Response:
    """
    return http response.
    
    Egg. code>1 -> success, code=0 -> failed.
    """
    return_data = {
        "code": code,
        "message": message,
        "data": data if data is not None else {}
    }
    if request_id:
        return_data["request_id"] = request_id
    response = jsonify(return_data)
    response.status_code = status
    return response


__all__ = ["query_data_process", "http_resp"]

