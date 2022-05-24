from abc import ABCMeta, abstractmethod
from typing import Union
#from authlib.integrations.requests_client import OAuth2Session
from requests import Response
from models.security import *


class BaseClient(metaclass=ABCMeta):
    base_url = None

    @property
    @abstractmethod
    def session(self):
        raise NotImplementedError

    @abstractmethod
    def _get_url(self, route):
        raise NotImplementedError

    @staticmethod
    def _handle_response(response: Response):
        if response.status_code == 200 or response.status_code == 201:
            print(response.json())
            return response.json()
        else:
            print(response.json())

    def _get(self, route, **kwargs) -> object:
        url = self._get_url(route)
        print(f'request : {url}')
        response = self.session.get(url, **kwargs)
        return self._handle_response(response)

    def _geturl(self, route, **kwargs) -> object:
        url = route
        print(f'request : {url}')
        response = self.session.get(url, **kwargs)
        return self._handle_response(response)



class Client(BaseClient):


    @property
    def session(self):
        raise NotImplementedError

    def _get_url(self, url):
        return self.base_url + url

"""

class OAuth2Client(Client):

    def __init__(self, credentials: Union[ClientCredentials, PasswordCredentials]):
        super().__init__()
        self.credentials = credentials

    @property
    def headers(self):
        raise NotImplementedError

    @property
    def session(self) -> OAuth2Session:
        _session = None
        if isinstance(self.credentials, ClientCredentials):
            _session = OAuth2Session(
                self.credentials.client_id,
                self.credentials.client_secret
            )

        if isinstance(self.credentials, PasswordCredentials):
            pass

        return _session if _session is not None else None
"""