"""Utilities.
@Project   : genshinhelper
@Author    : y1ndan
@Blog      : https://www.yindan.me
@GitHub    : https://github.com/y1ndan
"""

import datetime
import gettext
import hashlib
import json
import logging
import os
import random
import string
import time
from urllib.parse import urlencode

import requests

from genshinhelper import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

log = logger = logging

_localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
_translate = gettext.translation(
    'genshinhelper', _localedir, languages=[config.LANGUAGE], fallback=True)
_ = _translate.gettext

MESSAGE_TEMPLATE = _('''
    {today:#^18}
    🔅{nickname} {level} {region_name}
    Today's reward: {reward_name} × {reward_cnt}
    Total monthly check-ins: {total_sign_day} days
    Status: {status}
    {addons}
    {end:#^18}''')

DAIRY_TEMPLATE = _('''Traveler month {month} diary
    💠primogems: {current_primogems}
    🌕mora: {current_mora}''')

FINANCE_TEMPLATE = _('''Captain month {month} finance
    💎hcoin: {month_hcoin}
    🔮star: {month_star}''')


def set_lang(lang=None):
    if lang:
        os.environ['LANGUAGE'] = lang


def today():
    return datetime.date.today()


def month():
    return today().month


def get_mihoyo_app_cookie(cookie):
    if 'stoken' in cookie:
        return cookie

    cookie_dict = cookie_to_dict(cookie)
    stuid = cookie_dict['account_id']
    login_ticket = cookie_dict['login_ticket']
    url = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?uid={}&login_ticket={}&token_types=3'.format(stuid, login_ticket)
    response = request('get', url).json()
    list = nested_lookup(response, 'list', fetch_first=True)
    stoken = nested_lookup([i for i in list if i['name'] == 'stoken'], 'token', fetch_first=True)
    if not stoken:
        log.error(_('Failed to convert:\n{response}').format(response=response))
        return

    app_cookie = f'stuid={stuid}; stoken={stoken}; login_ticket={login_ticket}'
    log.info(_(f'Successful conversion!\n{app_cookie}').format(app_cookie=app_cookie))
    return app_cookie


def minutes_to_hours(minutes):
    minutes = int(minutes)
    if minutes < 0:
        raise ValueError('Input number cannot be negative')

    return {'hour': int(minutes / 60), 'minute': minutes % 60}


def get_cookies(cookies: str = None):
    if '#' in cookies:
        return cookies.split('#')
    elif isinstance(cookies, list):
        return cookies
    elif '{' in cookies:
        return json.loads(cookies)
    else:
        return cookies.splitlines()


def extract_cookie(name: str, cookie: str):
    if name not in cookie:
        raise Exception(
            _('Failed to extract cookie: The cookie does not contain the `{name}` field.').format(
                name=name
            )
        )
    return cookie.split(f'{name}=')[1].split(';')[0]


def cookie_to_dict(cookie):
    if cookie and '=' in cookie:
        cookie = dict([line.strip().split('=', 1) for line in cookie.split(';')])
    return cookie


def merge_dicts(*dict_args):
    result = {}
    for d in dict_args:
        result.update(d)
    return result


def extract_subset_of_dict(raw_dict, keys):
    subset = {}
    if isinstance(raw_dict, dict):
        subset = {key: value for key, value in raw_dict.items() if key in keys}
    return subset


def nested_lookup(obj, key, with_keys=False, fetch_first=False):
    result = list(_nested_lookup(obj, key, with_keys=with_keys))
    if with_keys:
        values = [v for k, v in _nested_lookup(obj, key, with_keys=with_keys)]
        result = {key: values}
    if fetch_first:
        result = result[0] if result else result
    return result


def _nested_lookup(obj, key, with_keys=False):
    if isinstance(obj, list):
        for i in obj:
            yield from _nested_lookup(i, key, with_keys=with_keys)

    if isinstance(obj, dict):
        for k, v in obj.items():
            if key == k:
                if with_keys:
                    yield k, v
                else:
                    yield v

            if isinstance(v, list) or isinstance(v, dict):
                yield from _nested_lookup(v, key, with_keys=with_keys)


def get_ds(ds_type: str = None, new_ds: bool = False, data: dict = None, params: dict = None):
    # 1:  ios
    # 2:  android
    # 4:  pc web
    # 5:  mobile web
    def new():
        t = str(int(time.time()))
        r = str(random.randint(100001, 200000))
        b = json.dumps(data) if data else ''
        q = urlencode(params) if params else ''
        c = _hexdigest(f'salt={salt}&t={t}&r={r}&b={b}&q={q}')
        return f'{t},{r},{c}'

    def old():
        t = str(int(time.time()))
        r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
        c = _hexdigest(f'salt={salt}&t={t}&r={r}')
        return f'{t},{r},{c}'

    app_version = '2.35.2'
    client_type = '5'
    salt = 'N50pqm7FSy2AkFz2B3TqtuZMJ5TOl3Ep'
    ds = old()
    if ds_type == '2' or ds_type == 'android':
        app_version = '2.35.2'
        client_type = '2'
        salt = 'ZSHlXeQUBis52qD1kEgKt5lUYed4b7Bb'
        ds = old()
    if ds_type == 'android_new':
        app_version = '2.35.2'
        client_type = '2'
        salt = 't0qEgfub6cvueAPgR5m9aQWWVciEer7v'
        ds = new()
    if new_ds:
        app_version = '2.35.2'
        client_type = '5'
        salt = 'xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs'
        ds = new()

    return app_version, client_type, ds


def _hexdigest(text):
    md5 = hashlib.md5()
    md5.update(text.encode())
    return md5.hexdigest()


def request(*args, **kwargs):
    is_retry = True
    count = 0
    max_retries = 3
    sleep_seconds = 5
    while is_retry and count <= max_retries:
        try:
            s = requests.Session()
            response = s.request(*args, **kwargs)
            is_retry = False
        except Exception as e:
            if count == max_retries:
                raise e
            log.error(_('Request failed: {}').format(e))
            count += 1
            log.info(
                _('Trying to reconnect in {} seconds ({}/{})...').format(
                    sleep_seconds, count, max_retries))
            time.sleep(sleep_seconds)
        else:
            return response

