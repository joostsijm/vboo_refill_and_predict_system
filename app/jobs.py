"""Jobs for scheduler module"""

from app import app, api


def check_resources(state_id, capital_id, resource_id, do_refill):
    """Check resources and refill if necessary"""
    app.check_resources(state_id, capital_id, resource_id, do_refill)

def send_telegram_update(state_id, group_id, resource_type):
    """Send telegram update"""
    app.send_telegram_update(state_id, group_id, resource_type)

def refill_resource(state_id, capital_id, resource_id):
    """Execute refill job"""
    api.refill(state_id, capital_id, resource_id)
