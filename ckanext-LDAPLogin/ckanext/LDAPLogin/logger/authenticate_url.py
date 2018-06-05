import sys
from keycloak.realm import KeycloakRealm
from keycloak.well_known import KeycloakWellKnown


client_id = 'python-ckan-datagate'
secret = '...secret...'

redirect_url = sys.argv[1]

realm = KeycloakRealm(server_url='https://www.snap4city.org', realm_name='master')
oidc_client = realm.open_id_connect(client_id=client_id, client_secret=secret)


# reperisce endpoints di configurazione per keycloak e relativa valrizzazione

print(oidc_client.authorization_url(redirect_uri=redirect_url), end='')

