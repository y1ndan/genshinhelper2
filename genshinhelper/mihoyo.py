"""
@Project   : genshinhelper
@Author    : y1ndan
@Blog      : https://www.yindan.me
@GitHub    : https://github.com/y1ndan
"""

import random
import time

from .core import Client, get_headers
from .utils import request, log, nested_lookup, extract_subset_of_dict, merge_dicts, cookie_to_dict, _


class YuanShen(Client):
    def __init__(self, cookie: str = None):
        super().__init__(cookie)
        self.act_id = 'e202009291139501'
        self.game_biz = 'hk4e_cn'
        self.required_keys.update({
            'total_sign_day', 'today', 'is_sign', 'first_bind',
            'current_primogems', 'current_mora'
        })

        self.sign_info_url = f'{self.api}/event/bbs_sign_reward/info?act_id={self.act_id}' + '&uid={}&region={}'
        self.rewards_info_url = f'{self.api}/event/bbs_sign_reward/home?act_id={self.act_id}'
        self.sign_url = f'{self.api}/event/bbs_sign_reward/sign'

        self._travelers_dairy = None
        self._daily_note = None
        self.travelers_dairy_url = 'https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo?bind_uid={}&bind_region={}&month={}&bbs_presentation_style=fullscreen&bbs_auth_required=true&mys_source=GameRecord'
        self.daily_note_url = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote'

    @property
    def sign_info(self):
        if not self._sign_info:
            roles_info = self.roles_info
            self._sign_info = [
                self.get_sign_info(i['game_uid'], i['region'])
                for i in roles_info
            ]
        return self._sign_info

    def get_sign_info(self, uid: str, region: str):
        log.info(_('Preparing to get check-in information ...'))
        url = self.sign_info_url.format(uid, region)
        response = request('get', url, headers=self.headers, cookies=self.cookie).json()
        data = nested_lookup(response, 'data', fetch_first=True)
        return extract_subset_of_dict(data, self.required_keys)

    @property
    def travelers_dairy(self):
        roles_info = self.roles_info
        """
        self._travelers_dairy = [
            self.get_travelers_dairy(i['game_uid'], i['region'])
            for i in roles_info
        ]
        """
        """
        修复等级不足10级时无法查看旅行者札记(无法获取每个月获得的摩拉原石数量)
        导致 _tp 为None
        使 genshin-checkin-help 中会出现`list index out of range`的bug
        """
        self._travelers_dairy = []
        for i in roles_info:
            _tp = self.get_travelers_dairy(i['game_uid'], i['region'])
            if _tp is None:
                self._travelers_dairy.append({'month_data': {}})
            else:
                self._travelers_dairy.append(_tp)

        return self._travelers_dairy

    def get_travelers_dairy(self, uid: str, region: str, month: int = 0):
        log.info(_("Preparing to get traveler's dairy ..."))
        url = self.travelers_dairy_url.format(uid, region, month)
        response = request('get', url, headers=self.headers, cookies=self.cookie).json()
        return nested_lookup(response, 'data', fetch_first=True)

    @property
    def month_dairy(self):
        raw_month_data = nested_lookup(self.travelers_dairy, 'month_data')
        return [
            extract_subset_of_dict(i, self.required_keys)
            for i in raw_month_data
        ]

    @property
    def daily_note(self):
        roles_info = self.roles_info
        self._daily_note = [
            self.get_daily_note(i['game_uid'], i['region'])
            for i in roles_info
        ]
        return self._daily_note

    def get_daily_note(self, uid: str, region: str):
        log.info(_('Preparing to get Yuan Shen daily note ...'))
        url = self.daily_note_url
        payload = {
            'role_id': uid,
            'server': region
        }
        response = request('get', url, headers=get_headers(with_ds=True, new_ds=True, params=payload), params=payload, cookies=self.cookie).json()
        data = nested_lookup(response, 'data', fetch_first=True)
        return data if data else response


class Honkai3rd(Client):
    def __init__(self, cookie: str = None):
        super().__init__(cookie)
        self.act_id = 'e202207181446311'
        self.game_biz = 'bh3_cn'
        self.required_keys.update({
            'total_sign_day', 'today', 'is_sign', 'first_bind',
            'month_hcoin', 'month_star'
        })

        self.sign_info_url = f'{self.api}/event/luna/info?act_id={self.act_id}' + '&uid={}&region={}'
        self.rewards_info_url = f'{self.api}/event/luna/home?act_id={self.act_id}'
        self.sign_url = f'{self.api}/event/luna/sign'

        self._bh3_finance = None
        self.bh3_finance_url = 'https://api.mihoyo.com/bh3-weekly_finance/api/index?bind_uid={}&bind_region={}&game_biz=bh3_cn'

    @property
    def sign_info(self):
        if not self._sign_info:
            roles_info = self.roles_info
            self._sign_info = [
                self.get_sign_info(i['game_uid'], i['region'])
                for i in roles_info
            ]
        return self._sign_info

    def get_sign_info(self, uid: str, region: str):
        log.info(_('Preparing to get check-in information ...'))
        url = self.sign_info_url.format(uid, region)
        response = request('get', url, headers=self.headers, cookies=self.cookie).json()
        data = nested_lookup(response, 'data', fetch_first=True)
        return extract_subset_of_dict(data, self.required_keys)

    @property
    def bh3_finance(self):
        roles_info = self.roles_info
        self._bh3_finance = [
            self.get_bh3_finance(i['game_uid'], i['region'])
            for i in roles_info
        ]
        return self._bh3_finance

    # Requires the game roles level greater than 25
    def get_bh3_finance(self, uid: str, region: str):
        log.info(_('Preparing to get Honkai 3rd finance ...'))
        url = self.bh3_finance_url.format(uid, region)
        response = request('get', url, headers=self.headers, cookies=self.cookie).json()
        return nested_lookup(response, 'data', fetch_first=True)

    @property
    def month_finance(self):
        bh3_finance = self.bh3_finance
        return [
            extract_subset_of_dict(i, self.required_keys)
            for i in bh3_finance
        ]


class MysDailyMissions(object):
    def __init__(self, cookie: str = None):
        self.cookie = cookie_to_dict(cookie)
        self.api = 'https://bbs-api.mihoyo.com'
        self.state_url = f'{self.api}/apihub/sapi/getUserMissionsState'
        self.sign_url = f'{self.api}/apihub/app/api/signIn'
        self.post_list_url = f'{self.api}/post/api/getForumPostList?&is_good=false&is_hot=false&page_size=20&sort_type=1' + '&forum_id={}'
        self.post_full_url = f'{self.api}/post/api/getPostFull' + '?post_id={}'
        self.upvote_url = f'{self.api}/apihub/sapi/upvotePost'
        self.share_url = f'{self.api}/apihub/api/getShareConf?entity_type=1' + '&entity_id={}'

        self._missions_state = None
        self._posts = None

        self.game_ids_dict = {1: '崩坏3', 2: '原神', 3: '崩坏2', 4: '未定事件簿', 5: '大别野', 6: '崩坏: 星穹铁道', 8: '绝区零'}
        self.forum_ids_dict = {1: '崩坏3', 26: '原神', 30: '崩坏2', 37: '未定事件簿', 34: '大别野', 52: '崩坏: 星穹铁道', 57: '绝区零'}
        self.game_ids = list(self.game_ids_dict.keys())
        self.forum_ids = list(self.forum_ids_dict.keys())
        self.result = {
            'sign': [],
            'view': [],
            'upvote': [],
            'share': []
        }

    @property
    def headers(self):
        headers = get_headers(with_ds=True, ds_type='android')
        headers.update({
            'User-Agent': 'okhttp/4.8.0',
            'Referer': 'https://app.mihoyo.com',
            'x-rpc-channel': 'miyousheluodi'
        })
        return headers

    @property
    def missions_state(self):
        log.info(_('Preparing to get user missions state ...'))
        url = self.state_url
        response = request('get', url, headers=self.headers, cookies=self.cookie).json()
        data = nested_lookup(response, 'data')
        states = nested_lookup(response, 'states', fetch_first=True)
        _missions_state = {
            i['mission_key']: i['is_get_award'] for i in states if i['mission_id'] in (58, 59, 60, 61)
        }
        self._missions_state = {
            'total_points': nested_lookup(data, 'total_points', fetch_first=True),
            'is_sign': _missions_state.get('continuous_sign', False),
            'is_view': _missions_state.get('view_post_0', False),
            'is_upvote': _missions_state.get('post_up_0', False),
            'is_share': _missions_state.get('share_post_0', False)
        }
        return self._missions_state

    def sign(self, game_id: int = None):
        if not game_id:
            game_id = random.choice(self.game_ids)
        if game_id not in self.game_ids:
            raise ValueError(f'The value of game_id is one of {self.game_ids}')

        log.info(_('Preparing to check-in for {} ...').format(self.game_ids_dict[game_id]))
        url = self.sign_url
        data = {'gids': str(game_id)}
        headers = get_headers(with_ds=True, ds_type='android_new', data=data)
        headers.update({
            'User-Agent': 'okhttp/4.8.0',
            'Referer': 'https://app.mihoyo.com',
            'x-rpc-channel': 'miyousheluodi'
        })
        response = request('post', url, json=data, headers=headers, cookies=self.cookie).json()
        message = response.get('message')
        result = {'name': self.game_ids_dict[game_id], 'message': message}
        self.result['sign'].append(result)
        return result

    def get_posts(self, forum_id: int = None):
        if not forum_id:
            forum_id = random.choice(self.forum_ids)
        if forum_id not in self.forum_ids:
            raise ValueError(f'The value of forum_id is one of {self.forum_ids}')

        log.info(_('Preparing to get posts of {} ...').format(self.forum_ids_dict[forum_id]))
        url = self.post_list_url.format(forum_id)
        response = request('get', url).json()
        post_list = nested_lookup(response, 'list', fetch_first=True)
        posts = [{
            'post_id': nested_lookup(post, 'post_id', fetch_first=True),
            'title': nested_lookup(post, 'subject', fetch_first=True)
        } for post in post_list]
        log.info(_('Successfully get {} posts').format(len(posts)))
        return posts

    def view_post(self, post: dict):
        log.info(_('Preparing to view post {} ...').format(post['title']))
        time.sleep(3)
        url = self.post_full_url.format(post['post_id'])
        response = request('get', url, headers=self.headers, cookies=self.cookie).json()
        message = response.get('message')
        log.info(message)
        result = {'title': post['title'], 'message': message}
        self.result['view'].append(result)
        return result

    def upvote_post(self, post: dict):
        log.info(_('Preparing to upvote post {} ...').format(post['title']))
        time.sleep(3)
        url = self.upvote_url
        data = {'post_id': post['post_id'], 'is_cancel': False}
        response = request('post', url, json=data, headers=self.headers, cookies=self.cookie).json()
        message = response.get('message')
        log.info(message)
        result = {'title': post['title'], 'message': message}
        self.result['upvote'].append(result)
        return result

    def share_post(self, post: dict):
        log.info(_('Preparing to share post {} ...').format(post['title']))
        url = self.share_url.format(post['post_id'])
        response = request('get', url, headers=self.headers, cookies=self.cookie).json()
        message = response.get('message')
        log.info(message)
        result = {'title': post['title'], 'message': message}
        self.result['share'].append(result)
        return result

    def run(self, forum_id: int = None):
        state = self.missions_state
        [self.sign(i) for i in self.game_ids if not state['is_sign']]

        posts = self.get_posts(forum_id)
        [self.view_post(i) for i in random.sample(posts[0:5], 5) if not state['is_view']]
        [self.upvote_post(i) for i in random.sample(posts[5:17], 10) if not state['is_upvote']]
        [self.share_post(i) for i in random.sample(posts[-3:-1], 1) if not state['is_share']]

        state = self.missions_state
        self.result = merge_dicts(state, self.result)
        return self.result
