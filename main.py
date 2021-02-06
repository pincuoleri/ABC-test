from config import *
from common import *


# 设定控制机为 HOST_LIST 中第几个
master_server_index = "1"

# 进行部署
for index, server in enumerate(HOST_LIST):
    connection = Terminal(server[1], PASS_WORD_LIST, user=server[0])
    if index+1 == master_server_index:
        # 控制机 配置文件
        connection.edit_config_file(1)
    else:
        # 压力机 配置文件
        connection.edit_config_file()
    print("开始部署服务器： {}\n".format(server[1]))
    connection.deploy()
print("部署服务器： {} 完成\n".format(server[1]))

# 检测环境是否部署成功
check_list = []
for server in HOST_LIST:
    connection = Terminal(server[1], PASS_WORD_LIST, user=server[0])
    if connection.check_deploy():
        check_list.append("{} -- OK!\n".format(server[1]))
    else:
        check_list.append("{} -- WRONG!\n".format(server[1]))
for i in check_list:
    print(i)