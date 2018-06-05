import sys
import re

from keycloak.realm import KeycloakRealm
from keycloak.well_known import KeycloakWellKnown

# from keycloak.keycloak_openid import KeycloakOpenID

import json


client_id = 'python-ckan-datagate'
secret = '...secret...'
 

#token = json.loads( "'''" + sys.argv[1] + "'''" )

access_token = sys.argv[1].split("access_token':")[1].split("'")[1]
refresh_token = sys.argv[1].split("refresh_token':")[1].split("'")[1]

 
realm = KeycloakRealm(server_url='https://www.snap4city.org', realm_name='master')
oidc_client = realm.open_id_connect(client_id=client_id, client_secret=secret)


userinfo = {}
try:
    userinfo = oidc_client.logout(refresh_token)
except Exception as e:
    pass


