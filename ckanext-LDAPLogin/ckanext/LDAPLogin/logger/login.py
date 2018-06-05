import pylons
import ckan.plugins as p

import ldap
import uuid
import os
import json
import ast

from ckan.common import request
from ckan.common import config
from ckan.model.user import User
from ckan.lib.helpers import flash_error

import ckan.model

import subprocess
import urlparse

redirect_login = 'https://datagate.snap4city.org/ssologin_handler'
redirect_logout =  'https://datagate.snap4city.org/ssologout_handler'


error_message = "Wrong username or password. You can use both your LDAP or CKAN credentials"


class LdapLogin(p.toolkit.BaseController):

    def __init__(self):


        self.ldapServerAddress = config.get('ckanext.ldapLogin.server_address', False)
        self.baseDn = config.get('ckanext.ldapLogin.base_dn', False)


    def ssologin_handler(self):
         
        if 'code' in request.GET:
            print 'ESISTE IL CODE'
            user_code = request.GET['code'] 

            user_token = subprocess.check_output("python3 " +  os.path.dirname(os.path.abspath(__file__))   + "/authenticate_code.py " + redirect_login + ' "' + user_code + '"'  ,shell=True )
            print user_token
          
            user_info = subprocess.check_output( "python3 " +  os.path.dirname(os.path.abspath(__file__))   + '/from_token_to_user.py "' + user_token + '"'  ,shell=True  )          
            print user_info        

            user_name = user_info.split("preferred_username':")[1].split("'")[1]
            if self._ldap_auth_from_token(user_name):
                # ldap ha certificato l'utente associato al token... procediamo col login vero e proprio
                pylons.session['ckanext-ldap-user'] = str(user_name)
                pylons.session.save()
                p.toolkit.redirect_to("https://datagate.snap4city.org/user/"+str(user_name) )
            else:
                try:
                    user_dict = p.toolkit.get_action('user_show')(data_dict={'id':user_name})
                    usr = User.by_name(user_dict['name'])                  
                except p.toolkit.ObjectNotFound:
                    usr = None
                    p.toolkit.redirect_to(control='user', action='login')
                if usr:
                    pylons.session['normal-user'] = str(user_name) 
                    pylons.session.save()
                    p.toolkit.redirect_to("https://datagate.snap4city.org/user/"+str(user_name) )
            

        else:
            url = subprocess.check_output("python3 " +  os.path.dirname(os.path.abspath(__file__))   + "/authenticate_url.py " + redirect_login ,shell=True )
            p.toolkit.redirect_to( url)
       

    def ssologout_handler(self):
        print "LOGOUT ....................."
        if 'code' in request.GET:
            user_code = request.GET['code'] 
            user_token = subprocess.check_output("python3 " +  os.path.dirname(os.path.abspath(__file__))   + "/authenticate_code.py " + redirect_logout + ' "' + user_code + '"'  ,shell=True ) 
            subprocess.check_output( "python3 " +  os.path.dirname(os.path.abspath(__file__)) + '/manage_logout.py "' + user_token + '"', shell = True)
            if 'ckanext-ldap-user' in pylons.session:
                del pylons.session['ckanext-ldap-user']
            if 'normal-user' in pylons.session:
                del pylons.session['normal-user']
            pylons.session.save()   
             
        else:
            url = subprocess.check_output("python3 " +  os.path.dirname(os.path.abspath(__file__))   + "/authenticate_url.py " + redirect_logout ,shell=True )
            p.toolkit.redirect_to( url)
    


    def login_handler(self):
        params = request.POST
        if 'login' in params and 'password' in params:
            login = params['login'] 
            password = params['password']
           
            # code = subprocess.check_output("python3 " +os.path.dirname(os.path.abspath(__file__))  + "/from_pw_to_token.py '" + login + "' '" + password + "'", shell=True   )
            # print code

            found_ldap = self._ldap_authentication(login, password)
            if found_ldap:
                pylons.session['ckanext-ldap-user'] = str(login)
                pylons.session.save() 
                p.toolkit.redirect_to("/user/"+str(login))
            else:
                try:
                    user_dict = p.toolkit.get_action('user_show')(data_dict={'id':login})
                    usr = User.by_name(user_dict['name'])
                   
                except p.toolkit.ObjectNotFound:
                    usr = None
                    p.toolkit.redirect_to(control='user', action='login')

                if usr and usr.validate_password(password):
                    pylons.session['normal-user'] = str(login) 
                    pylons.session.save()
                    p.toolkit.redirect_to('/user/' + str(login) )
                else:
                    flash_error(error_message)
                    p.toolkit.redirect_to('/user/login')
   

    def _ldap_auth_from_token(self, usname):
        l = ldap.initialize(self.ldapServerAddress)
        try: 
            username = 'cn=' + usname + ',' + self.baseDn 
            x = l.search_s(self.baseDn, ldap.SCOPE_SUBTREE, 'uid='+usname)
            l.unbind()
            if len(x) > 0:
                # non ci sono utenti con quell'username

                try:
                    user_dict = p.toolkit.get_action('user_show')(data_dict={'id':usname})
                    usr = User.by_name(user_dict['name'])
                                
                    if usr.state == 'deleted':
                       usr.activate()
                       ckan.model.Session.commit()                 
                  
                except p.toolkit.ObjectNotFound:
                    usr = None

                if usr is None: 
                    ldap_dataTuple  = x[0] # dovrebbe esserci un solo utente con quell'id
                    print ldap_dataTuple
                    email = "placeholder@domain.com" 
                    if "email" in ldap_dataTuple[1].keys():
                        email =ldap_dataTuple[1]["email"]
                    elif "mail" in ldap_dataTuple[1].keys():
                        email = ldap_dataTuple[1]["mail"]                
      		
                    user_dict_from_ldap = {'name':str(usname), 'email':email, 'password':str(uuid.uuid4())}
                    print "USER CREATE....................................................."
                    try:
                        print str(p.toolkit.get_action('user_create')(context={'ignore_auth':True}, data_dict=user_dict_from_ldap))
                    except ValidationError:
                        print "VALIDATION ERROR"          

            #p.toolkit.redirect_to('/user/' +str(un))  
                return True 
            else: # l'utente non e' ldap, ma SSO ha crtificato per lui
                try:
                    user_dict = p.toolkit.get_action('user_show')(data_dict={'id':usname})
                    usr = User.by_name(user_dict['name'])
                                
                    if usr.state == 'deleted':
                       usr.activate()
                       ckan.model.Session.commit()                 
                  
                except p.toolkit.ObjectNotFound:
                    usr = None

                if usr is None: 
                    email = "placeholder@domain.com"                 
                    user_dict_notldap = {'name':str(usname), 'email':email, 'password':str(uuid.uuid4())}
                    print "USER CREATE....................................................."
                    try:
                        print str(p.toolkit.get_action('user_create')(context={'ignore_auth':True}, data_dict=user_dict_notldap))
                    except ValidationError:
                        print "VALIDATION ERROR"          


                

        except ldap.LDAPError: 
            # l.unbind()
            return False
















    def _ldap_authentication(self, un, password ): 
        l = ldap.initialize(self.ldapServerAddress)
        try: 
            username = 'cn=' + un + ',' + self.baseDn
            i = l.bind_s(username, password) 
            x = l.search_s(self.baseDn, ldap.SCOPE_SUBTREE, 'uid='+un)
            l.unbind()

            try:
                user_dict = p.toolkit.get_action('user_show')(data_dict={'id':un})
                usr = User.by_name(user_dict['name'])
                                
                if usr.state == 'deleted':
                   usr.activate()
                   ckan.model.Session.commit()                 
                  
            except p.toolkit.ObjectNotFound:
                usr = None

            if usr is None: 
                ldap_dataTuple  = x[0] # dovrebbe esserci un solo utente con quell'id
                print ldap_dataTuple
                email = "placeholder@domain.com" 
                if "email" in ldap_dataTuple[1].keys():
                    email =ldap_dataTuple[1]["email"]
                elif "mail" in ldap_dataTuple[1].keys():
                    email = ldap_dataTuple[1]["mail"]                
      		
                user_dict_from_ldap = {'name':str(un), 'email':email, 'password':str(uuid.uuid4())}
                print "USER CREATE....................................................."
                try:
                    print str(p.toolkit.get_action('user_create')(context={'ignore_auth':True}, data_dict=user_dict_from_ldap))
                except ValidationError:
                    print "VALIDATION ERROR"          

            #p.toolkit.redirect_to('/user/' +str(un))  
            return True 

        except ldap.LDAPError: 
            # l.unbind()
            return False





