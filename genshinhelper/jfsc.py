"""
@Project   : genshinhelper
@Author    : y1ndan
@Blog      : https://www.yindan.me
@GitHub    : https://github.com/y1ndan
"""

from .utils import request

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.1(0x1800012a) NetType/4G Language/zh_CN'
}


def check_jfsc(token):
    url = 'http://ysjfsc.mihoyo.com/api/SignIn/checkSign'
    payload = {'token': token}
    response = request('get', url, headers=headers, params=payload).json()
    return True if response.get('is_sign') else False


def sign_jfsc(token):
    url = 'http://ysjfsc.mihoyo.com/api/SignIn/sign'
    payload = {'token': token}
    return request('post', url, headers=headers, data=payload).json()
