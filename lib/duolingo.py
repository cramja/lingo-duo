import requests


class Duo(object):

    def __init__(self, username, password):
        self.jwt = None
        self.session = requests.sessions.session()
        self.username = None
        self.id = None

        self._login(username, password)

    def _login(self, username, password):
        """
        Authenticate through ``https://www.duolingo.com/login``.
        """
        login_url = "https://www.duolingo.com/login"
        data = {"login": username, "password": password}
        response = self._post(login_url, data=data)
        attempt = response.json()

        if attempt.get('response') == 'OK':
            self.jwt = response.headers['jwt']
            self.username = attempt["username"]
            self.id = attempt["user_id"]
        else:
            raise Exception("Login failed")

    def _post(self, url, data=None):
        headers = {}
        if self.jwt is not None:
            headers['Authorization'] = 'Bearer ' + self.jwt
        req = requests.Request('POST',
                               url,
                               json=data,
                               headers=headers,
                               cookies=self.session.cookies)
        prepped = req.prepare()
        return self.session.send(prepped)

    def _get(self, url):
        headers = {}
        if self.jwt is not None:
            headers['Authorization'] = 'Bearer ' + self.jwt
        req = requests.Request('GET',
                               url,
                               headers=headers,
                               cookies=self.session.cookies)
        prepped = req.prepare()
        return self.session.send(prepped)

    def get_vocabulary(self):
        vocab_url = "https://www.duolingo.com/vocabulary/overview"
        response = self._get(vocab_url)
        response.raise_for_status()

        return response.json()['vocab_overview']

    def logout(self):
        logout_url = "https://www.duolingo.com/logout"
        self._post(logout_url)
