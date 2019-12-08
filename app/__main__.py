"""Main app"""

import time
import sys

from app import SCHEDULER, LOGGER, RESOURCE_NAMES, job_storage, jobs


if __name__ == '__main__':
    # jobs.refill_resource(2788, 4002, 0)
    # jobs.check_resources(2788, 4002, 0, True) # VN
    # jobs.check_resources(2620, 4002, 0, False) # Zeelandiae
    # graph()
    # get_resources(4001, datetime.now(), 0)

    JOBS = job_storage.get_jobs()
    for job in JOBS:
        LOGGER.info(
            'Add check for "%s", resource "%s" at "%s"',
            job['state_id'],
            job['resource_type'],
            job['minutes']
        )
        SCHEDULER.add_job(
            jobs.check_resources,
            'cron',
            args=[
                job['state_id'],
                job['capital_id'],
                RESOURCE_NAMES[job['resource_type']],
                job['refill']
            ],
            id='{}_check_{}'.format(job['state_id'], job['resource_type']),
            replace_existing=True,
            minute=job['minutes']
        )

    SCHEDULER.add_job(
        jobs.send_telegram_update,
        'cron',
        args=[2788, '@vn_resources', 0],
        id='send_telegram_update',
        replace_existing=True,
        minute='5'
    )

    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        LOGGER.info('Exiting application')
        SCHEDULER.shutdown()
        sys.exit()
