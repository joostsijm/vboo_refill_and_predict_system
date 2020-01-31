"""Main application"""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import joinedload

from app import SESSION, RESOURCE_MAX
from app.models import ResourceTrack, ResourceStat, Region


def save_resources(state_id, regions, resource_id):
    """Save resources to database"""
    session = SESSION()
    resource_track = ResourceTrack()
    resource_track.state_id = state_id
    resource_track.resource_type = resource_id
    resource_track.date_time = datetime.now()
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

def get_resources(region_id, date, resource_type):
    """Get resources on a date"""
    end_date_time = date.replace(hour=19, minute=0, second=0, microsecond=0)
    start_date_time = end_date_time - timedelta(1)
    session = SESSION()
    resource = {}
    resource_stats = session.query(ResourceStat) \
        .options(joinedload(ResourceStat.resource_track)) \
        .join(ResourceStat.resource_track) \
        .filter(ResourceStat.region_id == region_id) \
        .filter(ResourceTrack.resource_type == resource_type) \
        .filter(ResourceTrack.date_time >= start_date_time) \
        .filter(ResourceTrack.date_time <= end_date_time) \
        .order_by(ResourceTrack.date_time.desc()) \
        .all()
    start_limit = resource_stats[0].explored
    for resource_stat in resource_stats:
        time = resource_stat.resource_track.date_time
        resource[time] = resource_stat.explored + resource_stat.limit_left
    session.close()
    new_resource = {}
    for time, amount in resource.items():
        new_time = time.replace(tzinfo=timezone.utc).astimezone(tz=None) + timedelta(hours=1)
        new_resource[new_time] = amount - start_limit
    return new_resource


def _get_state_stat(session, state_id, resource_type, date_time, deep_exploration):
    """Get state stats from date"""
    ten_minutes = timedelta(minutes=10)
    query = session.query(ResourceStat) \
        .options(joinedload(ResourceStat.resource_track), joinedload(ResourceStat.region)) \
        .join(ResourceStat.resource_track) \
        .filter(ResourceTrack.state_id == state_id) \
        .filter(ResourceTrack.resource_type == resource_type) \
        .filter(ResourceTrack.date_time >= date_time - ten_minutes) \
        .filter(ResourceTrack.date_time <= date_time + ten_minutes) \
        .filter(ResourceTrack.date_time <= date_time + ten_minutes)
    if deep_exploration:
        query = query.filter(ResourceStat.deep_exploration > 0)
    stats = query.all()
    stats_dict = {}
    for stat in stats:
        stats_dict[stat.region_id] = stat
    return stats_dict

def get_work_percentage(state_id, resource_type, end_date_time, hours, times):
    """Get work percentage for state in last x hours"""
    end_date_time = end_date_time.replace(minute=0, second=0, microsecond=0)
    deep = bool(resource_type)

    session = SESSION()
    data = {
        0: {
            'date': end_date_time,
            'stats': _get_state_stat(session, state_id, resource_type, end_date_time, deep)
        }
    }
    for i in range(times, 0, -1):
        current_date_time = end_date_time - timedelta(hours=hours*i)
        data[i] = {
            'date': current_date_time,
            'stats': _get_state_stat(session, state_id, resource_type, current_date_time, deep)
        }
    session.close()

    regions = {}
    for region_id, stat in data[0]['stats'].items():
        regions[region_id] = stat.region.name

    for i in range(0, times):
        data[i]['progress'] = {}
        reset_date_time = data[i+1]['date']
        if reset_date_time.hour >= 19:
            reset_date_time = reset_date_time + timedelta(1)
        reset_date_time = reset_date_time.replace(hour=19)
        time_left = reset_date_time - data[i]['date']
        if time_left.seconds != 0:
            seconds_left = time_left.seconds
        else:
            seconds_left = 86400
        for region_id, stat in data[i]['stats'].items():
            if i+1 not in data or stat.region_id not in data[i+1]['stats']:
                continue
            next_stat = data[i+1]['stats'][stat.region_id]
            if seconds_left == 82800:
                mined = RESOURCE_MAX[resource_type] + next_stat.explored - stat.total()
                required = next_stat.total() / (seconds_left / (hours * 3600))
            else:
                mined = next_stat.total() - stat.total()
                required = next_stat.total() / (seconds_left / (hours * 3600))

            if required != 0:
                coefficient = 100 / RESOURCE_MAX[resource_type]
                percentage = (mined / required - 1) * next_stat.total() * coefficient + 100
            else:
                percentage = 100
            data[i]['progress'][stat.region_id] = percentage
            # print('{:4} left: {:3} mined: {:3} required: {:6.2f} percentage: {:6.2f}'.format(
            #     stat.region_id, next_stat.total(), mined, required, percentage
            # ))

    message_text = ''
    message_text += '{:15}: {:>8}\n'.format('region', 'workers')
    for date in data.values():
        if 'progress' in date:
            for region_id, progress in sorted(date['progress'].items(), key=lambda x: x[1]):
                message_text += '{:15}: {:6.2f} %\n'.format(
                    regions[region_id].replace('Netherlands', 'NL'),
                    progress
                )
    return message_text
