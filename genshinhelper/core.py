"""
@Project   : genshinhelper
@Author    : y1ndan
@Blog      : https://www.yindan.me
@GitHub    : https://github.com/y1ndan
"""

import uuid

from .exceptions import GenshinHelperException
from .utils import request, log, get_ds, nested_lookup, extract_subset_of_dict, merge_dicts, cookie_to_dict, today, _


def get_headers(oversea: bool = False, with_ds: bool = False, *args, **kwargs):
    ua_cn = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/{}'
    ua_os = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBSOversea/1.5.0'
    ua_default = ua_os if oversea else ua_cn
    app_version, client_type, ds = get_ds(*args, **kwargs)
    headers = {'User-Agent': ua_default.format(app_version)}
    if with_ds:
        headers.update({
            'x-rpc-device_id':
                str(uuid.uuid3(uuid.NAMESPACE_URL, ua_default)).replace(
                    '-', '').upper(),
            'x-rpc-client_type': client_type,
            'x-rpc-app_version': app_version,
            'DS': ds
        })
    return headers


class Client(object):
    def __init__(self, cookie: str = None):
        self.cookie = cookie_to_dict(cookie)
        self.headers = get_headers()
        self._roles_info = None
        self._sign_info = []
        self._rewards_info = []
        self._user_data = []
        self.api = 'https://api-takumi.mihoyo.com'
        self.act_id = None
        self.game_biz = None
        self.required_keys = {'region', 'game_uid', 'nickname', 'level', 'region_name'}

        self.roles_info_url = f'{self.api}/binding/api/getUserGameRolesByCookie' + '?game_biz={}'
        self.sign_info_url = None
        self.rewards_info_url = None
        self.sign_url = None

    @property
    def roles_info(self):
        if not self._roles_info:
            log.info(_('Preparing to get user game roles information ...'))
            url = self.roles_info_url.format(self.game_biz)
            response = request('get', url, headers=self.headers, cookies=self.cookie).json()
            log.debug(response)
            if response.get('retcode') != 0:
                raise GenshinHelperException(response.get('message'))

            raw_roles_info = nested_lookup(response, 'list', fetch_first=True)
            self._roles_info = [
                extract_subset_of_dict(i, self.required_keys)
                for i in raw_roles_info
            ]
        return self._roles_info

    @property
    def sign_info(self):
        ...
        return self._sign_info

    @property
    def rewards_info(self):
        if not self._rewards_info:
            log.info(_('Preparing to get monthly rewards information ...'))
            url = self.rewards_info_url
            response = request('get', url).json()
            self._rewards_info = nested_lookup(response, 'awards', fetch_first=True)
        return self._rewards_info

    @property
    def current_reward(self):
        sign_info = self.sign_info
        return [
            self.get_current_reward(i['total_sign_day'], i['is_sign'])
            for i in sign_info
        ]

    def get_current_reward(self, total_sign_day: int, is_sign: bool = False):
        rewards_info = self.rewards_info
        if isinstance(rewards_info[0], list):
            rewards_info = rewards_info[0]
        if is_sign:
            total_sign_day -= 1

        raw_current_reward = rewards_info[total_sign_day]
        return {'reward_' + k: v for k, v in raw_current_reward.items()}

    @property
    def user_data(self):
        sign_info = self.sign_info
        roles_info = self.roles_info
        current_reward = self.current_reward

        for i in range(len(sign_info)):
            d1 = roles_info[i]
            d2 = sign_info[i]
            d3 = current_reward[i]
            merged = merge_dicts(d1, d2, d3)
            self._user_data.append(merged)
        return self._user_data

    def sign(self):
        user_data = self.user_data
        log.info(_('Preparing to claim daily reward ...'))
        result = []
        for i in range(len(user_data)):
            user_data[i]['today'] = str(today())
            user_data[i]['status'] = _('👀 You have already checked-in')
            user_data[i]['addons'] = 'Olah! Odomu'
            user_data[i]['sign_response'] = None
            user_data[i]['end'] = ''
            total_sign_day = user_data[i]['total_sign_day']
            is_sign = user_data[i]['is_sign']

            if not is_sign:
                payload = {
                    'act_id': self.act_id,
                    'region': user_data[i]['region'],
                    'uid': user_data[i]['game_uid']
                }
                response = request(
                    'post',
                    self.sign_url,
                    headers=get_headers(with_ds=True),
                    json=payload, cookies=self.cookie).json()

                log.debug(response)
                user_data[i]['status'] = response.get('message', -1)
                user_data[i]['sign_response'] = response
                retcode = response.get('retcode', -1)
                # 0:      success
                # -5003:  already checked in
                if retcode == 0:
                    user_data[i]['total_sign_day'] = total_sign_day + 1
                    user_data[i]['is_sign'] = True
            result.append(user_data[i])

        self._user_data = result
        return result
