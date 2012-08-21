import cgi
import random
import time
import urllib
import urllib2
import json

class PayPalAccess:
    authorization_endpoint = 'https://www.paypal.com/webapps/auth/protocol/openidconnect/v1/authorize'
    access_token_endpoint = 'https://www.paypal.com/webapps/auth/protocol/openidconnect/v1/tokenservice'
    profile_endpoint = 'https://www.paypal.com/webapps/auth/protocol/openidconnect/v1/userinfo'
    logout_endpoint = 'https://www.paypal.com/webapps/auth/protocol/openidconnect/v1/endsession'
    validate_endpoint = 'https://www.paypal.com/webapps/auth/protocol/openidconnect/v1/checkid'
    
    key = 'YOUR APPLICATION ID'
    secret = 'YOUR APPLICATION SECRET'
    scopes = 'openid'                       #e.g. openid email profile https://uri.paypal.com/services/paypalattributes
    callback_url = 'YOUR CALLBACK URL'
    nonce = random.random() + time.time()
    
    access_token = ''
    refresh_token = ''
    id_token = ''
    
    def get_auth_url(self):
        #construct PayPal authorization URI
        self.auth_url = "%s?client_id=%s&response_type=code&scope=%s&redirect_uri=%s&nonce=%s" % (PayPalAccess.authorization_endpoint, PayPalAccess.key, PayPalAccess.scopes, PayPalAccess.callback_url, PayPalAccess.nonce)
        
        #redirect the user to the PayPal authorization URI
        return 'Location: ' + self.auth_url
    
    def get_access_token(self, code):
        self.code = code
        self.postvals = {'client_id': PayPalAccess.key, 'client_secret': PayPalAccess.secret, 'grant_type': 'authorization_code', 'code': self.code}
    
        #make request to capture access token
        self.params = urllib.urlencode(self.postvals)
        self.f = urllib.urlopen(PayPalAccess.access_token_endpoint, self.params)
        self.token = json.read(self.f.read())
        
        PayPalAccess.access_token = self.token['access_token']
        PayPalAccess.refresh_token = self.token['refresh_token']
        PayPalAccess.id_token = self.token['id_token']
        
        return self.token
    
    def refresh_access_token(self):
        self.postvals = {'client_id': PayPalAccess.key, 'client_secret': PayPalAccess.secret, 'grant_type': 'refresh_token', 'refresh_token': PayPalAccess.refresh_token}
    
        #make request to refresh access token
        self.params = urllib.urlencode(self.postvals)
        self.f = urllib.urlopen(PayPalAccess.access_token_endpoint, self.params)
        self.token = json.read(self.f.read())
        
        return self.token
    
    def validate_token(self):
        self.postvals = {'access_token': PayPalAccess.id_token}
        
        #make request to validate id token
        self.params = urllib.urlencode(self.postvals)
        self.f = urllib.urlopen(PayPalAccess.validate_endpoint, self.params)
        self.verification = self.f.read()
        
        return self.verification
    
    def get_profile(self):
        self.profile_url = "%s?schema=openid&access_token=%s" % (PayPalAccess.profile_endpoint, PayPalAccess.access_token)
        
        self.request = urllib2.Request(self.profile_url)
        self.response = urllib2.urlopen(self.request)
        self.profile = self.response.read()
        
        return self.profile

    def end_session(self):
        self.profile_url = "%s?id_token=%s&redirect_url=%s" % (PayPalAccess.logout_endpoint, PayPalAccess.id_token, PayPalAccess.callback_url + "&logout=true")
        
        self.request = urllib2.Request(self.profile_url)
        self.response = urllib2.urlopen(self.request)