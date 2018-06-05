import ckan.logic
import ckan.logic.auth

from ckan.common import _
from ckan.logic.auth.create import user_create as ckan_user_create 



@ckan.logic.auth_allow_anonymous_access
def user_create(context, data_dict = None):
    print "CREATO UN UTENTE CON IL MIO METODO "
    a = ckan_user_create(context, data_dict) 
    print a 
    return a 
