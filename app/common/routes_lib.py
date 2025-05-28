

def _get_work_obj(route_dict: dict, version=None):
    """
    版本控制
    """
    if not version:
        version = "default"
    val = route_dict.get(version)
    if not val:
        version = "default"
    return route_dict[version]

get_work_obj = _get_work_obj


__all__ = ["get_work_obj"]


