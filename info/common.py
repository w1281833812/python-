# 定义索引转换过滤器
def index_convert(index):
    index_dict = {1: "first", 2: "second", 3: "third"}
    return index_dict.get(index, "")
