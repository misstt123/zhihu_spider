import redis
import threading
import configparser
import pymysql
from DBUtils.PooledDB import PooledDB

# red
# 读取配置文件
filename = "config.ini"
config = configparser.ConfigParser()
# redis = StrictRedis()
config.read(filename, encoding='utf-8')
db = dict(config.items('db'))

conn_thread = PooledDB(
    pymysql,
    mincached=int(db['mincached']),
    host=db['host'],
    port=int(db['port']),
    user=db['user'],
    passwd=db['password'],
    db=str(db['db'])
)

# 连接redis
redis_conf = dict(config.items('redis'))
host =redis_conf['host']
port = int(redis_conf['port'])
pool = redis.ConnectionPool( #连接池
    host=host,
    port=port,
)
redis=redis.Redis(connection_pool=pool)

if __name__ == '__main__':
    try:
        # redis.set('lisi',13,ex=10)
        # redis.lpush("user",1,2,2,343)

        # redis.
        redis.rpush('user','23',32)

        # conn = conn_thread.connection()
        # cursor = conn.cursor()
        # sql = "insert into company(name1,age) values(%s,%s)"
        # cursor.execute(sql, ("张三", 33))
        # conn.commit()
        # conn.close()
        #
        # print()
    except  Exception as e:
        print(e)
