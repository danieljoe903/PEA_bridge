import os
class Config:
    SQLALCHEMY_DATABASE_URI= 'mysql+mysqlconnector://root@localhost/pea_bridge'
    SQLALCHEMY_TRACK_MODIFICATION=False


    UPLOAD_FOLDER=os.path.join('pkg','static','upload')
    # MAX_CONTENT_LENGTH=5 * 1024 * 1024