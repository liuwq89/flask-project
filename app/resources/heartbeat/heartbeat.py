from app.common.driver import *


class HeartBeatResource(CommonResource):
    ALLOW_METHOD = {
        "GET": "心跳检测"
    }

    def __init__(self):
        super().__init__()

    @method_control
    @access_logger
    def get(self):
        return self.http_resp()




