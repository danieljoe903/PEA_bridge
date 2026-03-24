from flask import Blueprint

property_bp=Blueprint('property',__name__)

from pkg.property import pro_route