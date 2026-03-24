from flask import Blueprint

admin_bp=Blueprint('admin',__name__,url_prefix='/manage')


from pkg.admin import admin_routes