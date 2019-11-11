"""Main application"""

from app import SESSION
from app.models import ResourceTrack, ResourceStat, Region


def save_resources(state_id, regions, resource_id):
    """Save resources to database"""
    session = SESSION()
    resource_track = ResourceTrack()
    resource_track.state_id = state_id
    resource_track.resource_type = resource_id
    session.add(resource_track)
    session.commit()

    for region_id, region_dict in regions.items():
        region = session.query(Region).get(region_id)
        if not region:
            region = save_region(session, region_id, region_dict)

        resource_stat = ResourceStat()
        resource_stat.resource_track_id = resource_track.id
        resource_stat.region_id = region.id
        resource_stat.explored = region_dict['explored']
        resource_stat.deep_exploration = region_dict['deep_exploration']
        resource_stat.limit_left = region_dict['limit_left']
        session.add(resource_stat)

    session.commit()
    session.close()

def save_region(session, region_id, region_dict):
    """Save player to database"""
    region = Region()
    region.id = region_id
    region.name = region_dict['region_name']
    session.add(region)
    return region
