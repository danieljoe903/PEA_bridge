import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+mysqlconnector://root@localhost/pea_bridge"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    UPLOAD_FOLDER = os.path.join(
        "/home/danieljoe903/PEA_bridge",
        "pkg",
        "static",
        "uploads"
    )


    # ==========================================
    # EMAIL CONFIGURATION
    # ==========================================

    MAIL_SERVER = "smtp.gmail.com"

    MAIL_PORT = 465

    MAIL_USE_TLS = False

    MAIL_USE_SSL = True

    MAIL_USERNAME = os.getenv(
        "FLEXY_EMAIL"
    )

    MAIL_PASSWORD = os.getenv(
        "FLEXY_EMAIL_APP_PASSWORD"
    )

    MAIL_DEFAULT_SENDER = (
        "Flexy Properties",
        os.getenv("FLEXY_EMAIL")
    )

    FLEXY_EMAIL = os.getenv(
        "FLEXY_EMAIL"
    )