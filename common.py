from fabric import Connection
import os
from config import *
from functools import reduce

class Terminal:


    def __init__(self, ip_address, password, user="root", *args):
        # 初始化连接
        self.host = "{}@{}".format(user,ip_address)
        self.password = password
        self.connection = Connection(self.host, connect_kwargs={"password": self.password})

    # 修改配置文件
    @staticmethod
    def edit_config_file(master=0):
        # 删除已存在的 jmeter.properties 文件
        if "jmeter.properties" in os.listdir("resources"):
            os.remove("resources/jmeter.properties")
        # 根据目的服务器职能，修改配置文件内容，master=0为默认压力机，master=1时为控制机
        if master:
            with open("jmeter.properties","r") as f:
                properties = f.readlines()
                # 拼接 remote_host 配置信息，并写入对应位置
                remote_host = reduce(lambda x,y:x[1]+":"+OPEN_PORT+","+y[1]+":"+OPEN_PORT,HOST_LIST)
                properties[267] = "remote_hosts={}\n".format(remote_host)
            with open("resources/jmeter.properties","w") as t:
                for i in properties:
                    t.write(i)
        else:
            with open("jmeter.properties", "r") as f:
                properties = f.readlines()
                # 编辑压力机参数信息
                properties[271] = "server_port={}\n".format(OPEN_PORT)
                properties[309] = "server.rmi.localport={}\n".format(OPEN_PORT)
            with open("resources/jmeter.properties","w") as t:
                for i in properties:
                    t.write(i)

    # 目标环境配置
    def deploy(self):
        # 导入用户环境变量
        if int(self.connection.run("ls -la /root/ |grep .bashrc|wc -l").stdout.split()[0]):
            self.connection.run("rm /root/.bashrc")
        self.connection.put("resources/bashrc","/root/.bashrc")
        # 创建 jdk 环境
        if "java" not in self.connection.run("ls /usr").stdout.split():
            self.connection.run("mkdir /usr/java")
        self.connection.put("resources/jdk-8u271-linux-x64.tar.gz", "/usr/java")
        self.connection.run("tar -zxvf /usr/java/jdk-8u271-linux-x64.tar.gz -C /usr/java/")
        self.connection.run("rm /usr/java/jdk-8u271-linux-x64.tar.gz")
        # 创建 jmeter 环境
        if "test" not in self.connection.run("ls /home").stdout.split():
            self.connection.run("mkdir /home/test")
        self.connection.put("resources/apache-jmeter-5.4.tar.gz", "/home/test")
        self.connection.run("tar -zxvf /home/test/apache-jmeter-5.4.tar.gz -C /home/test/")
        self.connection.run("rm /home/test/apache-jmeter-5.4.tar.gz")
        # 导入 jmeter 配置文件
        self.connection.put("resources/jmeter.properties", "/home/test/apache-jmeter-5.4/bin/")

    # 检验环境配置是否成功
    def check_deploy(self):
        try:
            if "java version" in self.connection.run("java -version").__str__() and  "Apache" in self.connection.run("jmeter -v").__str__():
                return True
            else:
                return False
        except:
            return False

    # 检验进程是否运行

if __name__=="__main__":
    pass
