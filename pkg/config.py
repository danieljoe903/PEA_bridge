import os
class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@localhost/pea_bridge'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join('pkg', 'static', 'upload')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'danieljoe903@gmail.com'
    MAIL_PASSWORD = 'zhwbogpjshysozuh'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False