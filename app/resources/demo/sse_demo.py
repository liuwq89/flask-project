import requests

from app.common.driver import *


class SSEDemoInterface(CommonResource):
    ALLOW_METHOD = {
        "POST": "接口信息"
    }

    def __init__(self):
        super().__init__()

    @method_control
    def post(self):
        args = self.get_parser_args(self.post_parser_config)
        try:
            uri = ""
            headers = {}
            payload = {}
            # sse 流式数据
            response = requests.post(url=uri, headers=headers, json=payload, stream=True)
            if response.status_code != 200:
                ilog.error("请求失败: %s" % str(response))
                return self.http_resp(FAILED_CODE, "模型请求失败", status=400)
            
            def generate():
                for line in response.iter_lines(decode_unicode=True):
                    if line and line.startswith("data: "):
                        content = line[6:]
                        if content == "[DONE]":
                            yield self.send_sse_done()
                            break
                        try:
                            data = json.loads(content)
                            delta = data["choices"][0]["delta"]
                            if "content" in delta:
                                yield self.send_sse_msg(delta)
                        except Exception as e:
                            ilog.error("处理msg失败: %s, resp_msg=%s" % traceback.format_exc(), line)
                            yield self.send_sse_err(msg="处理content失败")
                            break

            return Response(stream_with_context(generate()), mimetype='text/event-stream')
        
        except Exception as e:
            ilog.error("请求失败: %s" % traceback.format_exc())
            return self.http_resp(FAILED_CODE, "请求失败", status=400)
        
            









