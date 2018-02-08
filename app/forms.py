from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, \
 SubmitField, SelectField, TextAreaField
from wtforms.validators import NumberRange, DataRequired, Email, EqualTo, Length

from config import Config
from app.models import User, Document

class FormLogin(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class FormRegistration(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password (will be ignored for OAuth users)', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password (will be ignored for OAuth users)', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class FormForwardCms(FlaskForm):
	forward_distance = IntegerField('Move fwd (cms)',[NumberRange(min=0, max=500)])
	forward_submit = SubmitField('Submit')
		
class FormBackwardCms(FlaskForm):
	backward_distance = IntegerField('Move back (cms)',[NumberRange(min=0, max=500)])
	backward_submit = SubmitField('Submit')
	
class FormLeftTurnDegrees(FlaskForm):
	lturn_degrees = IntegerField('Turn left (degrees)',[NumberRange(min=0, max=360)])
	lturn_submit = SubmitField('Submit')
	
class FormRightTurnDegrees(FlaskForm):
	rturn_degrees = IntegerField('Turn right (degrees)',[NumberRange(min=0, max=360)])
	rturn_submit = SubmitField('Submit')
	
class FormPic(FlaskForm):
	pic_submit = SubmitField('Take Picture')

class FormSettings(FlaskForm):
    camera_res = SelectField('Camera Resolution (horizontal)',choices=Config.CAMERA_RES_LIST)
    camera_sharpness = IntegerField('Camera Sharpness (-100 to 100)', [NumberRange(min=-100, max=100)])
    submit = SubmitField('Submit')

class FormEdit(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

class FormServo(FlaskForm):
    position = IntegerField('New position to look at (0-180)',[NumberRange(min=0, max=180)])
    submit = SubmitField('Submit')

class FormDistance(FlaskForm):
    get_distance = SubmitField('Get Distance')

class FormListBuckets(FlaskForm):
    get_buckets = SubmitField('Get Available GCS buckets')