import os


class Config(object):
    SECRET_KEY = os.environ.get('FLASKKEY') or 'you-will-never-guess'
    LOGLEVEL = os.environ.get('LOGLEVEL') or 'INFO'
    LOGFILE = os.environ.get('LOGFILE') or "viservice.log"
    LOGDIR = os.environ.get('LOGDIR') or "./log/"
    DBHOST = os.environ.get('DBHOST') or '192.168.0.134'
    DATABASE = os.environ.get('DATABASE') or 'automation'
    DBUSER = os.environ.get('DBUSER') or 'rjn'
    DBPWD = os.environ.get('DBPWD') or 'zaxxon'
    WWWHOST = os.environ.get('WWWHOST') or '0.0.0.0'
    WWWPORT = os.environ.get('WWWPORT') or '5000'
