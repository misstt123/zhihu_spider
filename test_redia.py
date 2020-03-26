from redis import StrictRedis
import threading
import configparser

# 读取配置文件
filename = "config.ini"
con = configparser.ConfigParser()
# redis = StrictRedis()
con.read(filename, encoding='utf-8')

if __name__ == '__main__':
    print(con.has_section("db"))
    db = dict(con.items('db'))
    print(db['host'])
    print(db['port'])
