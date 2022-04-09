import json
import requests


SUCCESS_STATUS_CODE = 200

AUTH_ENDPOINT = '/auth/token'
BOOK_ENDPOINT = '/book'
UNBOOK_ENDPOINT = '/unbook'


class InvalidLoginError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg


class NotAuthorizedError(RuntimeError):
    pass


def get_login_payload(login, password):
    return {
        'username': login,
        'password': password
    }


def get_response_content(response):
    return json.loads(response.content.decode('utf8'))


class AppServer:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._url = "http://{}:{}".format(self._host, self._port)
        self._auth_headers = None

    def _fill_auth_info(self, login_content):
        token = login_content['access_token']
        token_type = login_content['token_type']

        self._auth_headers = {'Authorization': '{} {}'.format(token_type, token)}

    def auth(self, login, password):
        payload = get_login_payload(login, password)

        auth_response = requests.post(self._url + AUTH_ENDPOINT, data=payload)
        auth_content = get_response_content(auth_response)

        if auth_response.status_code != SUCCESS_STATUS_CODE:
            raise InvalidLoginError(auth_content['detail'])

        self._login = login
        self._fill_auth_info(auth_content)

    def _authed_get(self, endpoint, data=None):
        if self._auth_headers is None:
            raise NotAuthorizedError()

        return requests.get(self._url + endpoint,
                            data=data,
                            headers=self._auth_headers)

    def _authed_post(self, endpoint, data=None):
        if self._auth_headers is None:
            raise NotAuthorizedError()

        return requests.post(self._url + endpoint,
                             data=data,
                             headers=self._auth_headers)

    def try_protected(self):
        p = self._authed_get('/protected')
        print(get_response_content(p))
