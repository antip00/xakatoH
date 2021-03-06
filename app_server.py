import json
import requests


SUCCESS_STATUS_CODE = 200

AUTH_ENDPOINT = '/auth/token'
BOOK_ENDPOINT = '/book'
UNBOOK_ENDPOINT = '/unbook'
NOTIFICATION_ENDPOINT = '/notify'
JSON_ENDPOINT = '/json'


class InvalidLoginError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg


class NotAuthorizedError(RuntimeError):
    pass


class AttemptFailedError(RuntimeError):
    def __init__(self, msg):
        self.msg = msg


def get_login_payload(login, password):
    return {
        'username': login,
        'password': password
    }


def get_response_content(response):
    return json.loads(response.content.decode('utf8'))


def get_date_isoformat(date):
    return date.date().isoformat()


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


    def _authed_request(self, method, endpoint, data):
        if self._auth_headers is None:
            raise NotAuthorizedError()

        if data is not None:
            data["user"] = self._login

        return method(self._url + endpoint,
                      json=data,
                      headers=self._auth_headers)

    def _authed_get(self, endpoint, data=None):
        return self._authed_request(requests.get, endpoint, data)

    def _authed_post(self, endpoint, data=None):
        return self._authed_request(requests.post, endpoint, data)

    def try_protected(self):
        p = self._authed_get('/protected')
        print(get_response_content(p))

    def _get_attempt_data(self, date, room, time_id):
        return {
            "date": get_date_isoformat(date),
            "room_name": room,
            "time_id": time_id
        }

    def _attempt(self, endpoint, date, room, time_id):
        data = self._get_attempt_data(date, room, time_id)

        resp = self._authed_post(endpoint, data)
        resp_content = get_response_content(resp)

        if resp_content['success']:
            return

        raise AttemptFailedError(resp_content['error_msg'])

    def attempt_book(self, date, room, time_id):
        self._attempt(BOOK_ENDPOINT, date, room, time_id)

    def attempt_unbook(self, date, room, time_id):
        self._attempt(UNBOOK_ENDPOINT, date, room, time_id)

    def get_date_json(self, date):
        data = {"date": get_date_isoformat(date)}

        resp = self._authed_post(JSON_ENDPOINT, data)

        return json.loads(get_response_content(resp))


    def get_notification(self):
        resp = self._authed_post(NOTIFICATION_ENDPOINT, {})

        return get_response_content(resp)['notification']
