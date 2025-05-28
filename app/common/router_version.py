

def __get_work_obj(route_dict: dict, version=None):
    if not version:
        version = "default"
    val = route_dict.get(version)
    if not val:
        version = "default"
    return route_dict[version]

get_work_obj = __get_work_obj


__all__ = ["get_work_obj"]

