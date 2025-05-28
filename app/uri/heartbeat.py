from app.uri import Uri
from app.common import constants

from app.resources.heartbeat.heartbeat import HeartBeatResource


# heartbert
heartbeat_uri = Uri()
heartbeat_uri.set_prefix(constants.API_URI_PREFIX.rstrip("/"))

heartbeat_uri.add(HeartBeatResource, "/")




