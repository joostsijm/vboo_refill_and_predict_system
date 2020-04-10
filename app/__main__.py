"""Main app"""

import time
import sys

from app import SCHEDULER, LOGGER, RESOURCE_NAMES, job_storage, jobs


def add_telegram_update_job(state_id, telegram_id, resource_type):
    """Add telegram update job"""
    SCHEDULER.add_job(
        jobs.send_telegram_update,
        'cron',
        args=[state_id, telegram_id, resource_type],
        id='{}_send_telegram_update_{}'.format(state_id, resource_type),
        replace_existing=True,
        minute='5'
    )

if __name__ == '__main__':
    # jobs.refill_resource(3304, 4004, 0, True)
    # jobs.refill_resource(3261, 200062, 0, False)
    # jobs.check_resources(2788, 4002, 0, True) # VN
    # jobs.check_resources(2620, 4002, 0, False) # Zeelandiae
    # app.graph()
    # get_resources(4001, datetime.now(), 0)
    # jobs.send_telegram_update(2788, '@vn_resources', 'gold')
    # jobs.send_telegram_update(2788, '@vn_uranium_resources', 'uranium')
    # sys.exit()

    JOBS = job_storage.get_jobs()
    for job in JOBS:
        LOGGER.info(
            'Add check for "%s", resource "%s" at "%s", alt "%s"',
            job['state_id'],
            job['resource_type'],
            job['minutes'],
            job['alt']
        )
        SCHEDULER.add_job(
            jobs.check_resources,
            'cron',
            args=[
                job['state_id'],
                job['capital_id'],
                RESOURCE_NAMES[job['resource_type']],
                job['refill'],
                job['alt']
            ],
            id='{}_check_{}'.format(job['state_id'], job['resource_type']),
            replace_existing=True,
            minute=job['minutes']
        )

    add_telegram_update_job(2788, '@vn_resources', 'gold')
    add_telegram_update_job(2788, '@vn_uranium_resources', 'uranium')

    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        LOGGER.info('Exiting application')
        SCHEDULER.shutdown()
        sys.exit()
