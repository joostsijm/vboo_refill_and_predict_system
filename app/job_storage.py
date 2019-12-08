"""store and read jobs"""

import json

from app import LOGGER


def get_jobs():
    """Read jobs"""
    LOGGER.info('Read stored jobs')
    try:
        with open('jobs.json', 'r') as jobs_file:
            jobs = json.load(jobs_file)
            LOGGER.info('found "%s" job(s) in job storage', len(jobs))
            return jobs
    except FileNotFoundError:
        LOGGER.error('job storage file "jobs.json" not found')
    return []
