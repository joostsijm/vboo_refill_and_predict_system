"""Main application"""

from app import Session
from app.models import ResourceTrack, ResourceStat


def save_resources(state_id, regions, resource_id):
    """Save resources to database"""
    session = Session()
    resource_track = ResourceTrack()
    resource_track.state_id = state_id
    resource_track.resource_type = resource_id
    session.add(resource_track)

    for region_id, region in regions.items():
        resource_stat = ResourceStat()
        resource_stat.resource_track_id = resource_track.id
        resource_stat.region_id = region_id
        resource_stat.explored = region['explored']
        resource_stat.deep_exploration = region['deep_exploration']
        resource_stat.limit_left = region['limit_left']
        session.add(resource_stat)
    session.commit()
    session.close()
