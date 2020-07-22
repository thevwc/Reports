# config.py # AzureMonitorScheduling

import os
#import pyodbc
import urllib.parse

from dotenv import load_dotenv

# LOAD dotenv IN THE BASE DIRECTORY
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# print (os.getenv('Driver'))
# print (os.getenv('Server'))
# print (os.getenv('Database'))
# print (os.getenv('Username'))
# print (os.getenv('Password'))

params = urllib.parse.quote_plus('DRIVER=' +  os.getenv('Driver') + ';'
                                    'SERVER=' + os.getenv('Server') + ';'
                                    'DATABASE=' + os.getenv('Database') + ';'
                                    'UID=' + os.getenv('Username') + ';'
                                    'PWD=' + os.getenv('Password') + ';'
)
conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)

class Config(object):
    SECRET_KEY = os.environ.get('Secret_key') or 'juniorbr549wells'
    SQLALCHEMY_DATABASE_URI = conn_str 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD=True 
        
