class ProxyNode(object):
    # 代理节点类，存储节点信息
    def __init__(self, ip, port, max_count=-1):
        self.ip = ip
        self.port = port
        self.max_count = max_count
        self.remain_count = max_count

    @property
    def address(self):
        # 获取拼接好的地址
        return f"https://{self.ip}:{self.port}"
