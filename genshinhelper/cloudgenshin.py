"""
@Project   : genshinhelper
@Author    : y1ndan
@Blog      : https://www.yindan.me
@GitHub    : https://github.com/y1ndan
"""

from .utils import request


def get_cloudgenshin_free_time(headers):
    url = 'https://api-cloudgame.mihoyo.com/hk4e_cg_cn/wallet/wallet/get'
    return request('get', url, headers=headers).json()
