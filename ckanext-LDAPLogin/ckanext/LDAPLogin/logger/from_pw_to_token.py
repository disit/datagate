import sys

from keycloak.realm import KeycloakRealm
from keycloak.well_known import KeycloakWellKnown

# from keycloak.keycloak_openid import KeycloakOpenID

import json


client_id = 'python-ckan-datagate'
secret = '...secret...'

_username = sys.argv[1]
_password = sys.argv[2]



realm = KeycloakRealm(server_url='https://www.snap4city.org', realm_name='master')
oidc_client = realm.open_id_connect(client_id=client_id, client_secret=secret)

accesstoken = oidc_client._token_request('password', username=_username, password=_password)

print(json.dumps(accesstoken))
