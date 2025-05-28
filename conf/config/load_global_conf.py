import os

from conf.config.base import ROOT_PATH

global_conf_path = "/run/secrets/global.conf"
if not os.path.exists(global_conf_path):
    global_conf_path = os.path.join(ROOT_PATH, "conf/global/global.conf")
if not os.path.exists(global_conf_path):
    raise FileNotFoundError(f"global.conf not found at {global_conf_path}")


def _load_global_conf(path: str) -> dict:
    conf = {}
    if os.path.exists(path):
        with open(path) as file:
            for line in file:
                if not line or line.strip().startswith("#") or line.find("=") == -1:
                    continue
                key, value = map(str.strip, line.split("=", 1))
                if value.lower() == "false":
                    conf[key] = False
                elif value.lower() == "true":
                    conf[key] = True
                else:
                    conf[key] = value
    return conf

global_conf = _load_global_conf(global_conf_path)


__all__ = ["global_conf"]




