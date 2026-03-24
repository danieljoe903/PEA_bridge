from flask import Blueprint

user_bp=Blueprint('user',__name__)


from pkg.user import user_routes