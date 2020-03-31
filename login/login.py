import sys
import os
from PIL import Image
from bs4 import BeautifulSoup
import time
import re
import json
import configparser
import requests
import http.cookiejar as cookielib
import traceback


class Login:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language":"zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Host": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        "Origin": "https://www.zhihu.com/",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "Pragma":"no-cache"
    }
    __xsrf = ''
    __session = ''
    username = ''
    password = ''

    def __init__(self, session):
        if not session:
            requests.adapters.DEFAULT_RETRIES = 5
            self.session = requests.Session()
            self.session.cookies = cookielib.LWPCookieJar(filename='cookie')
            self.session.keep_alive = False
            try:
                self.session.cookies.load(ignore_discard=True)
            except:
                print('Cookie 未能加载')
            finally:
                pass
        else:
            self.__session = session

        # 获取配置
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

    # json转成字符串cookie
    def json2String(self, data):
        json_data = dict(data)
        # print(json_data)
        # keys = json_data.keys()
        # values = json_data.values()
        # i=0
        str = ''
        for key, value in json_data.items():
            prefix = "{}={};".format(key, value)
            str += prefix
        return str.rstrip(';')

    # 获取xsrf
    def get_xsrf(self):
        index_url = 'http://www.zhihu.com/explore'
        # 获取登录时需要用到的_xsrf
        try:
            index_page = self.__session.get(index_url, headers=self.headers, timeout=35)
        except:
            print('获取知乎页面失败，请检查网络连接')
            sys.exit()

        html = index_page.text
        # cookie_text=requests.session().cookies
        # print(cookie_text)

        cookies_dict = requests.utils.dict_from_cookiejar(self.__session.cookies)


        # 把cookies转化成字典。
        # print("cookie:" + str(cookies_dict))
        # dictinfo =json.loads(cookies_dict)
        # print(json.dumps(cookies_dict))
        self.__session.cookies.save()
        return self.json2String(cookies_dict)

        # 这里的_xsrf 返回的是一个list
        # BS = BeautifulSoup(html, 'html.parser')
        # xsrf_input = BS.find({'name': '_xsrf'})
        # pattern = r'value=\"(.*?)\"'
        # # print(xsrf_input)
        # self.__xsrf = re.findall(pattern, str(xsrf_input))[0]
        # print("获取到xsrf:" + str(self.__xsrf))
        #
        # self.headers['X-Xsrftoken'] = self.__xsrf
        # self.__session.cookies.save()  # 获取完之后保存一下cookie

        return self.__xsrf

    # 获取验证码
    def get_captcha(self):
        t = str(time.time() * 1000)
        captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        r = self.__session.get(captcha_url, headers=self.headers, timeout=35)
        with open('captcha.jpg', 'wb') as f:
            f.write(r.content)
            f.close()
            # 用pillow 的 Image 显示验证码
            # 如果没有安装 pillow 到源代码所在的目录去找到验证码然后手动输入
        try:
            im = Image.open('captcha.jpg')
            im.show()
            im.close()
        except:
            print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
            captcha = input("请输入验证码\n>")
        return captcha

    # 验证是否登陆
    def check_login(self):
        check_url = 'https://www.zhihu.com/settings/profile'
        try:
            login_check = self.__session.get(check_url, allow_redirects=False, headers=self.headers, timeout=35)
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            print("验证登陆失败，请检查网络")
            sys.exit()
        print("验证登陆的http status code为：" + str(login_check.status_code))
        if int(login_check.status_code) == 200:
            return True
        else:
            return False

    # 进行模拟登陆
    def do_login(self):
        self.headers["X-Requested-With"] = "fetch"
        self.headers["Referer"]="https://www.zhihu.com/signin?next=%2Fhot"
        try:
            # 模拟登陆
            if self.check_login():
                print('您已经登录')
                return
            else:
                if self.config.get("zhihu_account", "username") and self.config.get("zhihu_account", "password"):
                    self.username = self.config.get("zhihu_account", "username")
                    self.password = self.config.get("zhihu_account", "password")
                else:
                    self.username = input('请输入你的用户名\n>  ')
                    self.password = input("请输入你的密码\n>  ")
        except Exception as err:
            print(traceback.print_exc())
            print(err)
            sys.exit()

        if re.match(r"^1\d{10}$", self.username):
            print("手机登陆\n")
            post_url = 'https://www.zhihu.com/signin?next=%2Ffollow'
            self.headers['Cookie']=self.get_xsrf()
            postdata = {
                'password': self.password,
                'remember_me': 'true',
                'phone_num': self.username,
            }
        # else:
        #     print("邮箱登陆\n")
        #     post_url = 'https://www.zhihu.com/login/email'
        #     postdata = {
        #         '_xsrf': self.get_xsrf(),
        #         'password': self.password,
        #         'remember_me': 'true',
        #         'email': self.username,
        #     }

        try:
            login_page = self.__session.post(post_url, postdata, headers=self.headers, timeout=35)
            # print(login_page.text)
            # print(postdata)
            login_json = json.loads(login_page.text.encode('latin-1').decode('unicode-escape'))
            # print(login_json)
            # 需要输入验证码 r = 0为登陆成功代码
            if int(login_json['r']) == 1:
                sys.exit("需要填写验证码")
        except:
            postdata['captcha'] = self.get_captcha()
            login_page = self.__session.post(post_url, postdata, headers=self.headers, timeout=35)
            print(login_page.text.encode('latin-1').decode('unicode-escape'))
        # 保存登陆cookie
        self.__session.cookies.save()
