# OAuth2 authentication extracted from client.py
# This file contains authentication logic for Microshare API
from .client import MicroshareClient

class MicroshareAuth:
    def __init__(self, client: MicroshareClient):
        self.client = client
    
    def authenticate(self):
        return self.client.authenticate()

