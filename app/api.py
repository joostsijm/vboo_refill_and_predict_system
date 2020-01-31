"""Main application"""

import re

import requests
from bs4 import BeautifulSoup

from app import BASE_URL, HEADERS, LOGGER, RESOURCE_IDS


def download_resources(state_id, resource_id):
    """Download the resource list"""
    # return read_resources()
    response = requests.get(
        '{}listed/stateresources/{}/{}'.format(BASE_URL, state_id, RESOURCE_IDS[resource_id]),
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
            'region_name': re.sub('Factories: .*$', '', columns[1].text),
            'explored': float(columns[2].string),
            'maximum': int(float(columns[3].string)),
            'deep_exploration': int(columns[4].string),
            'limit_left': int(columns[5].string),
        }
    return regions

def refill(state_id, capital_id, resource_id, alt):
    """Main function"""
    # Check location
    # response = requests.get(
    #     '{}main/content'.format(BASE_URL),
    #     headers=HEADERS
    # )
    # soup = BeautifulSoup(response.text, 'html.parser')
    # state_div = soup.find_all('div', {'class': 'index_case_50'})[1]
    # action = state_div.findChild()['action']
    # current_state_id = int(re.sub('.*/', '', action))
    # LOGGER.info('Current state %s', current_state_id)

    params = {}
    # if current_state_id != state_id:
    #     params['alt'] = True
    if alt:
        params['alt'] = True

    json_data = {
        'tmp_gov': resource_id
    }

    requests.post(
        '{}parliament/donew/42/{}/0'.format(BASE_URL, resource_id),
        headers=HEADERS,
        params=params,
        json=json_data
    )

    response = requests.get(
        '{}parliament/index/{}'.format(BASE_URL, capital_id),
        headers=HEADERS
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    active_laws = soup.find('div', {'id': 'parliament_active_laws'})
    resource_name = RESOURCE_IDS[resource_id]
    exploration_laws = active_laws.findAll(
        text='Resources exploration: state, {} resources'.format(resource_name)
    )
    LOGGER.info('Resources exploration: state, %s resources', resource_name)
    for exploration_law in exploration_laws:
        action = exploration_law.parent.parent['action']
        action = action.replace('law', 'votelaw')
        result = requests.post(
            '{}{}/pro'.format(BASE_URL, action),
            params=params,
            headers=HEADERS
        )
        LOGGER.info('Response: %s', result.text)
