from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,RadioField,SelectField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

buttons={'style':"padding: 5px;height: 30px;width: 100px;font-size: 14px;color: white;background: orange;border: none;margin: 8px;border-radius: 50px;box-shadow: 0px 0px 10px orange;outline: none;"}
inputs = {'style':"width: 80%;height: 30px;padding: 9px;color: orange;border: 1px solid orange;box-shadow: 1px 0px 3px orange;border-radius: 50px;font-size: 15px;text-transform: capitalize;outline: none;"}



class LoginForm(FlaskForm):
    username = StringField('Username : ', validators=[DataRequired()])
    password = PasswordField('Password :', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In!',render_kw=buttons)


class RegistrationForm(FlaskForm):
    username = StringField('Username :', validators=[DataRequired()])
    email = StringField('Email :', validators=[DataRequired(), Email()])
    password = PasswordField('Password :', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Register',render_kw=buttons)

class ProductForm(FlaskForm):
    prod_name = StringField('Product Name :', validators=[DataRequired()])
    prod_value = StringField('Value :', validators=[DataRequired()])
    prod_desc = StringField('Description :', validators=[DataRequired()])
    image = FileField(u'Image File', validators=[DataRequired()])
    # img = StringField('Img :', validators=[DataRequired()])
    # username = StringField('Username :', validators=[DataRequired()])
    submit = SubmitField('Publish!',render_kw=buttons)

class Profile(FlaskForm):
    prof_name = StringField('Search Seller :', validators=[DataRequired()], render_kw=inputs)
    submit = SubmitField('Search!',render_kw=buttons)


class Explore(FlaskForm):
    search = StringField('Search Jute Product', validators=[DataRequired()], render_kw=inputs)
    submit = SubmitField('Search!',render_kw=buttons)



    
