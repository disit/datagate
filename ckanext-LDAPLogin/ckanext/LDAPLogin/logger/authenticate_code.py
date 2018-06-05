
from keycloak.realm import KeycloakRealm
from keycloak.well_known import KeycloakWellKnown
import sys
import json

client_id = 'python-ckan-datagate'
secret = '...secret...'


realm = KeycloakRealm(server_url='https://www.snap4city.org', realm_name='master')
oidc_client = realm.open_id_connect(client_id=client_id, client_secret=secret)


# reperisce endpoints di configurazione per keycloak e relativa valrizzazione

redirect_uri = sys.argv[1]
code = sys.argv[2]

print(redirect_uri)
print(code)


user_code_json = None
user_code = None

try: 
    user_code = oidc_client.authorization_code( code, redirect_uri)
    user_code_json = json.dumps(user_code)
except Exception as e:
    print(e)

print(user_code, end='')

