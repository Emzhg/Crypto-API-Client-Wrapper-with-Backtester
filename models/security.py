from dataclasses import dataclass


@dataclass
class Credentials:
    pass


@dataclass
class ClientCredentials(Credentials):
    client_id: str
    client_secret: str


@dataclass
class PasswordCredentials(Credentials):
    client_id: str
    client_secret: str
    user: str
    password: str
