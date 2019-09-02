"""Main application"""

import re

import requests
from bs4 import BeautifulSoup

from hvs import BASE_URL, HEADERS, Session
from hvs.models import ResourceTrack, ResourceStat


RESOURCES = {
    0: 'gold',
    2: 'oil',
    4: 'ore',
    11: 'uranium',
    15: 'diamond',
}

def download_resources(state_id, resource_id):
    """Download the resource list"""
    response = requests.get(
        '{}listed/stateresources/{}/{}'.format(BASE_URL, state_id, RESOURCES[resource_id]),
        headers=HEADERS
    )
    return parse_resources(response.text)


def read_resources():
    """Read resource file"""
    with open('resources.html') as file:
        return parse_resources(file)


def parse_resources(html):
    """Read the resources left"""
    soup = BeautifulSoup(html, 'html.parser')

    regions_tree = soup.find_all(class_='list_link')

    regions = {}
    for region_tree in regions_tree:
        region_id = int(region_tree['user'])
        columns = region_tree.find_all('td')
        regions[region_id] = {
            'name': re.sub('Factories: .*$', '', columns[1].text),
            'explored': float(columns[2].string),
            'maximum': int(float(columns[3].string)),
            'deep_exploration': int(columns[4].string),
            'limit_left': int(columns[5].string),
        }
    return regions

def print_resources(regions):
    """print resources"""
    print('region                        expl max   D left    c %    t %')
    for region in regions.values():
        region['explored_percentage'] = 100 / region['maximum'] * region['explored']
        region['total_left'] = region['explored'] + region['limit_left']
        region['total_percentage'] = 100 / 2500 * region['total_left']

        print('{:25}: {:7.2f}{:4}{:4}{:5}{:7.2f}{:7.2f}'.format(
            region['name'],
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
    return max_time / limit * lowest_percentage


def refill(state_id, capital_id, resource_id):
    """Main function"""
    # Check location
    response = requests.get(
        '{}main/content'.format(BASE_URL),
        headers=HEADERS
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    state_div = soup.find_all('div', {'class': 'index_case_50'})[1]
    action = state_div.findChild()['action']
    current_state_id = int(re.sub('.*/', '', action))
    print('Current state: {}'.format(current_state_id))

    data = {
        'tmp_gov': resource_id
    }
    params = {}
    if current_state_id != state_id:
        params['alt'] = True

    requests.post(
        '{}parliament/donew/42/{}/0'.format(BASE_URL, resource_id),
        headers=HEADERS,
        params=params,
        data=data
    )

    response = requests.get(
        '{}parliament/index/{}'.format(BASE_URL, capital_id),
        headers=HEADERS
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    active_laws = soup.find('div', {'id': 'parliament_active_laws'})
    resource_name = RESOURCES[resource_id]
    exploration_laws = active_laws.findAll(
        text='Resources exploration: state, {} resources'.format(resource_name)
    )
    print('Resources exploration: state, {} resources'.format(resource_name))
    print(exploration_laws)
    for exploration_law in exploration_laws:
        action = exploration_law.parent.parent['action']
        action = action.replace('law', 'votelaw')
        result = requests.post(
            '{}{}/pro'.format(BASE_URL, action),
            headers=HEADERS
        )
        print(result.text)


def save_resources(state_id, regions, resource_id):
    """Save resources to database"""
    session = Session()
    resource_track = ResourceTrack()
    resource_track.state_id = state_id
    resource_track.resource_id = resource_id
    session.add(resource_track)
    session.commit()

    for region_id, region in regions.items():
        resource_stat = ResourceStat()
        resource_stat.region_id = region_id
        resource_stat.explored = region['explored']
        resource_stat.deep_exploration = region['deep_exploration']
        resource_stat.limit_left = region['limit_left']
        session.add(resource_stat)
    session.commit()
