import os
class Config:
    SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root@localhost/pea_bridge'
    SQLALCHEMY_TRACK_MODIFICATIONS=False


    UPLOAD_FOLDER=os.path.join('pkg','static','upload')
    