from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from config import Config
from flask_bootstrap import Bootstrap
from pymongo import MongoClient

app = Flask(__name__)
app.config.from_object(Config)
app.config.update(SESSION_COOKIE_NAME = 'marketplace')
login = LoginManager(app)
login.login_view = 'login'
client = MongoClient("mongodb+srv://ccl1:ccl1234@cluster0.79iqn.mongodb.net/ccl1?retryWrites=true&w=majority")
db = client.get_database('market')
# mongo = PyMongo(app)
bootstrap = Bootstrap(app)


from app import routes