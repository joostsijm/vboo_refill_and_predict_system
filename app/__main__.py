"""Main app"""

import time
import sys

from app import SCHEDULER, LOGGER, jobs


def add_check_resources(state_id, capital_id, resource_id, do_refill, minute):
    """Add check resources job"""
    SCHEDULER.add_job(
        jobs.check_resources,
        'cron',
        args=[state_id, capital_id, resource_id, do_refill],
        id='{}_check_{}'.format(state_id, resource_id),
        replace_existing=True,
        minute=minute
    )

if __name__ == '__main__':
    # jobs.refill_resource(2788, 4002, 0)
    # jobs.check_resources(2788, 4002, 0, False) # VN
    # jobs.check_resources(2620, 4002, 0, False) # Zeelandiae
    # graph()
    # get_resources(4001, datetime.now(), 0)

    # VN
    add_check_resources(2788, 4008, 0, True, '0,15,30,45')
    add_check_resources(2788, 4008, 11, True, '0')
    # Zeelandiae
    add_check_resources(2620, 0, 0, False, '50')
    # Belgium
    add_check_resources(2604, 0, 0, False, '40')

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
