from flask import Blueprint
 
interest_bp= Blueprint('interest',__name__)

from pkg.client_interest import interest_route