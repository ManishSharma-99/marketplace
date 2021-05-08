import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess-market'
    # MONGO_URI = 'mongodb://localhost:27017/market'
    # MONGO_DBNAME = 'market'