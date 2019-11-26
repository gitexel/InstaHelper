import hashlib
import json
import random
import re
import string
import logging
from instagram_web_api import Client
from instagram_web_api.client import login_required
from instagram_web_api.compat import (
    compat_urllib_request, compat_urllib_parse,
    compat_urllib_error,
    compat_http_client,
)
from instagram_web_api.errors import (
    ClientError, ClientLoginError,
    ClientConnectionError, ClientBadRequestError,
    ClientForbiddenError, ClientThrottledError,
)
from socket import timeout, error as socket_error
from ssl import SSLError
from backend import BackendService
from models import UserProfile
from errors import ChallengeError
from helpers import check_instagram_errors
from settings import UserData

logging.basicConfig(level=logging.INFO)


class MyClient(Client):

    @staticmethod
    def _extract_rhx_gis(html):
        mobj = re.search(
            r'"rhx_gis":"(?P<rhx_gis>[a-f0-9]{32})"', html, re.MULTILINE)
        if mobj:
            return mobj.group('rhx_gis')  # result of the main method

        options = string.ascii_lowercase + string.digits
        text = ''.join([random.choice(options) for _ in range(8)])
        return hashlib.md5(text.encode()).hexdigest()

    @login_required
    def suggested_users(self, suggested_count=50, exclude_ids=None, ignore_cache=True):
        """
        Get suggested users

        :param suggested_count: count of suggested users
        :param exclude_ids:
        :param ignore_cache:

        """
        if exclude_ids is None:
            exclude_ids = []

        variables = {
            'fetch_media_count': 0,
            'fetch_suggested_count': suggested_count,
            'ignore_cache': ignore_cache,
            'filter_followed_friends': True,
            'seen_ids': exclude_ids,
            'include_reel': False,
        }
        query = {
            'query_hash': 'bd90987150a65578bc0dd5d4e60f113d',
            'variables': json.dumps(variables, separators=(',', ':'))
        }
        return self._make_request(self.GRAPHQL_API_URL, query=query)

    def _make_request(self, url, params=None, headers=None, query=None,
                      return_response=False, get_method=None):
        """
        Calls the web API.

        :param url: fully formed api url
        :param params: post params
        :param headers: custom headers
        :param query: get url params
        :param return_response: bool flag to only return the http response object
        :param get_method: custom http method type
        :return:
        """
        if not headers:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Accept-Language': 'en-US',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'close',
            }
            if params or params == '':
                headers.update({
                    'x-csrftoken': self.csrftoken,
                    'x-requested-with': 'XMLHttpRequest',
                    'x-instagram-ajax': self.rollout_hash,
                    'Referer': 'https://www.instagram.com',
                    'Authority': 'www.instagram.com',
                    'Origin': 'https://www.instagram.com',
                    'Content-Type': 'application/x-www-form-urlencoded'
                })
        if query:
            url += ('?' if '?' not in url else '&') + compat_urllib_parse.urlencode(query)
            sig = self.generate_request_signature(query, url)
            if sig:
                headers['X-Instagram-GIS'] = sig

        req = compat_urllib_request.Request(url, headers=headers)
        if get_method:
            req.get_method = get_method

        data = None
        if params or params == '':
            if params == '':  # force post if empty string
                data = ''.encode('ascii')
            else:
                data = compat_urllib_parse.urlencode(params).encode('ascii')
        try:
            self.logger.debug('REQUEST: {0!s} {1!s}'.format(url, req.get_method()))
            self.logger.debug('REQ HEADERS: {0!s}'.format(
                ['{}: {}'.format(k, v) for k, v in headers.items()]
            ))
            self.logger.debug('REQ COOKIES: {0!s}'.format(
                ['{}: {}'.format(c.name, c.value) for c in self.cookie_jar]
            ))
            self.logger.debug('REQ DATA: {0!s}'.format(data))
            res = self.opener.open(req, data=data, timeout=self.timeout)

            self.logger.debug('RESPONSE: {0:d} {1!s}'.format(
                res.code, res.geturl()
            ))
            self.logger.debug('RES HEADERS: {0!s}'.format(
                [u'{}: {}'.format(k, v) for k, v in res.info().items()]
            ))

            if return_response:
                return res

            response_content = self._read_response(res)
            self.logger.debug('RES BODY: {0!s}'.format(response_content))
            if 'www.instagram.com/challenge' in response_content:
                raise ChallengeError(res.geturl())  # raise error with challenge url
            return json.loads(response_content)

        except compat_urllib_error.HTTPError as e:
            msg = 'HTTPError "{0!s}" while opening {1!s}'.format(e.reason, url)
            if e.code == 400:
                raise ClientBadRequestError(msg, e.code)
            elif e.code == 403:
                raise ClientForbiddenError(msg, e.code)
            elif e.code == 429:
                raise ClientThrottledError(msg, e.code)
            raise ClientError(msg, e.code)

        except (SSLError, timeout, socket_error,
                compat_urllib_error.URLError,  # URLError is base of HTTPError
                compat_http_client.HTTPException,
                ConnectionError) as connection_error:
            raise ClientConnectionError('{} {}'.format(
                connection_error.__class__.__name__, str(connection_error)))


class InstaService:
    def __init__(self, username='', password='', settings=None):
        self.user_data = UserData()
        self.username = username or self.user_data.username
        self.client = MyClient(
            auto_patch=True,
            authenticate=False,
            username=self.username,
            password=password,
            settings=settings
        )

        self.client.cookie_jar._cookies = self.user_data.cookie
        self.backend_api = BackendService(username=self.username, key=self.user_data.subscription_key)
        self.excluded_ids = set()

    @check_instagram_errors
    def client_login(self) -> str:
        try:
            result = self.client.login()
            result = 'Authenticated - userId: %s ' % result.get('userId') if result.get(
                'authenticated') else 'Not authenticated'
        except ClientLoginError as CLE:
            result = CLE.msg

        return result

    @check_instagram_errors
    def get_suggested_users(self, followers_count=10000000, enable_popular=False) -> list:

        result = self.client.suggested_users(exclude_ids=list(self.excluded_ids), ignore_cache=False)
        users = []
        edges = result.get('data', {}).get('user', {}).get('edge_suggested_users', {}).get('edges', [])

        for edge in edges:
            node = edge.get('node')
            description = node.get('description')
            user = node.get('user')

            if (description == 'Suggested for you') or enable_popular:
                user_followers_count = user.get('edge_followed_by', {}).get('count', 0)
                if user_followers_count <= followers_count:
                    users.append(UserProfile(user))
                else:
                    pass
            if len(self.excluded_ids) < 235:
                self.excluded_ids.add(int(user.get('id')))
        return users

    @check_instagram_errors
    def get_client_profile(self, username='') -> UserProfile:

        result = self.client.user_info2(username or self.username)

        return result

    @check_instagram_errors
    def follow_user(self, user_id: int):
        result = self.client.friendships_create(user_id=user_id)
        return result.get('result', '') == 'following'

    @property
    def cookie_dict(self) -> dict:
        # get _cookies instead if cookie_jar to be able to save using pickle
        # todo search if you can use cookie_jar directly to QSettings
        # noinspection PyProtectedMember
        return self.client.cookie_jar._cookies

    def set_cookie_dict(self, cookie):
        self.client.cookie_jar._cookies = cookie

    def get_subscription_status(self) -> dict:
        self.backend_api.key = self.user_data.get_subscription_key(refresh_settings=True)
        return self.backend_api.subscription_status()
