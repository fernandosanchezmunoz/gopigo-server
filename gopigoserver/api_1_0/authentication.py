from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth 

from gopigoserver.models import User
from gopigoserver.api_1_0 import api

from gopigoserver.api_1_0.errors import unauthorized, forbidden

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password): 
	if not email_or_token or email_or_token == '':
		#g.current_user = AnonymousUser()
		return False 		#anonymous not allowed
	if password == '':		#token used
		g.current_user = User.verify_auth_token(email_or_token) 
		g.token_used = True
		return g.current_user is not None
	user = User.query.filter_by(email = email_or_token).first() 
	if not user:
		return False
	g.current_user = user
	g.token_used = False

	return user.check_password(password)

@auth.error_handler
def auth_error():
	return unauthorized('Invalid credentials')

@api.before_request 
@auth.login_required 
def before_request():
	if not g.current_user.is_authenticated:
		return forbidden('Unconfirmed account')

@api.route('/token')
#@api.route('/tokens/', methods=['POST'])
def get_token():
	if g.current_user.is_anonymous() or g.token_used: 
		return unauthorized('Invalid credentials')
	return jsonify({'token': \
		g.current_user.generate_auth_token( expiration=3600), 'expiration': 3600})

