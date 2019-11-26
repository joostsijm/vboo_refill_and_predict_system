"""Main application"""

def print_resources(regions):
    """print resources"""
    print('region                        expl max   D left    c %    t %')
    for region in regions.values():
        region['explored_percentage'] = 100 / region['maximum'] * region['explored']
        region['total_left'] = region['explored'] + region['limit_left']
        region['total_percentage'] = 100 / 2500 * region['total_left']

        print('{:25}: {:7.2f}{:4}{:4}{:5}{:7.2f}{:7.2f}'.format(
            region['region_name'],
            region['explored'],
            region['maximum'],
            region['deep_exploration'],
            region['limit_left'],
            region['explored_percentage'],
            region['total_percentage'],
        ))


def need_refill(regions, limit):
    """Check if refill is needed"""
    for region in regions.values():
        percentage = 100 / region['maximum'] * region['explored']
        if percentage < limit and region['limit_left']:
            return True
    return False


def max_refill_seconds(regions, limit, max_time):
    """Give random seconds for next refill"""
    lowest_percentage = limit
    for region in regions.values():
        percentage = 100 / region['maximum'] * region['explored']
        if percentage < lowest_percentage:
            lowest_percentage = percentage
    return int(max_time / limit * lowest_percentage)
