#!venv/bin/python

'''
Oauth helper module to handle Oauth/oauth2 with main providers
'''

from config import Config
import logging
logger = logging.getLogger(Config.APP_NAME)

import json
from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        logger.debug('**DEBUG: Authorized')
        pass

    def callback(self):
        logger.debug('**DEBUG: Callback')
        pass

    def get_callback_url(self):
        logger.debug('**DEBUG: Oauth: get-Callback-URL: {}'.format(url_for('oauth_callback', provider=self.provider_name,
                       _external=True)))
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',           
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )
        me = oauth_session.get('me').json()
        username = me.get('name').replace(' ','') #name without spaces
        #in case facebook does not provide email
        if not me.get('email'):
            #make it up putting together the name
            me['email'] = username +'@facebook'
        return (
            'facebook$' + me['id'], #callback returns social_id, username, email
            username,         #use "name" as "username"
            me.get('email')
            )


class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.service = OAuth1Service(
            name='twitter',
            consumer_key=self.consumer_id,
            consumer_secret=self.consumer_secret,
            request_token_url='https://api.twitter.com/oauth/request_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            access_token_url='https://api.twitter.com/oauth/access_token',
            base_url='https://api.twitter.com/1.1/'
        )

    def authorize(self):
        request_token = self.service.get_request_token(
            params={'oauth_callback': self.get_callback_url()}
        )
        session['request_token'] = request_token
        return redirect(self.service.get_authorize_url(request_token[0]))

    def callback(self):
        request_token = session.pop('request_token')
        if 'oauth_verifier' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            request_token[0],
            request_token[1],
            data={'oauth_verifier': request.args['oauth_verifier']}
        )
        me = oauth_session.get('account/verify_credentials.json').json()
        social_id = 'twitter$' + str(me.get('id'))
        #make-up a username - nickname, will be used for profile URLs etc
        username = me.get('screen_name').replace(' ','') #without spaces
        #in case Twitter does not provide email
        if not me.get('email'):
            #make it up putting together the name
            me['email'] = username +'@twitter'
        return (social_id,
                username, 
                me.get('email')   # Twitter does not provide email
                )


class GoogleSignIn(OAuthSignIn):
    '''
    Shamelessly copied from https://github.com/heroku/heroku-airflow/blob/master/airflow_login/airflow_auth.py
    '''
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        self.service = OAuth2Service(
                name='google',
                client_id=self.consumer_id,
                client_secret=self.consumer_secret,
                authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
                base_url="https://www.googleapis.com/oauth2/v3/userinfo",
                access_token_url="https://www.googleapis.com/oauth2/v4/token"
        )

    def authorize(self):   #removed "scheme" as a parameter
        return redirect(self.service.get_authorize_url(
            scope='email profile',
            response_type='code',
            redirect_uri=self.get_callback_url())   #was get_callback_url(scheme)
            )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
                data={'code': request.args['code'],
                      'grant_type': 'authorization_code',
                      'redirect_uri': self.get_callback_url()
                     },
                decoder = json.loads
        )
        me = oauth_session.get('').json()
        return (me['name'],
                me['sub'],
                me['email'])