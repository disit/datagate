import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import pylons

from ckanext.LDAPLogin.logic.auth.create import user_create
from logger import login



def debugmsg():
    debug =  str(pylons.session.get('ckanext-ldap-user')) 
    debug+= "   ######   "                
    debug +=  str(pylons.session.get('normal-user'))
    return debug


class LdaploginPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IAuthenticator)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates') # richiesto per le pagine html
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'LDAPLogin')

    # IAuthenticator

    def identify(self): 
        print str(pylons.session.get('ckanext-ldap-user'))
        user = pylons.session.get('ckanext-ldap-user')
        if user:
            plugins.toolkit.c.user = user
        else:
            user = pylons.session.get('normal-user')
            if user: 
                plugins.toolkit.c.user = user


    def login(self):
        pass

    def logout(self):
        if 'ckanext-ldap-user' in pylons.session:
            del pylons.session['ckanext-ldap-user']
            
        if 'normal-user' in pylons.session:
            del pylons.session['normal-user']
        pylons.session.save()

    def abort(self, status_code, detail, headers, comment):
        return status_code, detail, headers, comment


    # IRoutes

    def before_map(self, _map):
        _map.connect('/ldap_login_handler', controller='ckanext.LDAPLogin.logger.login:LdapLogin', action='login_handler')
        _map.connect('/ssologin_handler', controller='ckanext.LDAPLogin.logger.login:LdapLogin', action='ssologin_handler')
        _map.connect('/ssologout_handler', controller='ckanext.LDAPLogin.logger.login:LdapLogin', action='ssologout_handler')
        return _map

    # ITemplateHelper
    def get_helpers(self):
        return {'debug': debugmsg}

    # IAuthFunctions
    def get_auth_functions(self):
        return { 'user_create': user_create}


