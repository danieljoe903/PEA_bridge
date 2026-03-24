from flask import Blueprint

agent_bp=Blueprint('agent',__name__)

from pkg.agent import agent_route