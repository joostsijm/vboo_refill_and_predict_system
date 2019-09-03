"""Main app"""

from datetime import datetime, timedelta
import random
import time

from hvs import scheduler
from hvs.app import download_resources, need_refill, max_refill_seconds, refill, \
    save_resources, print_resources


def job_check_resources(state_id, capital_id, resource_id):
    """Check resources and refill if necessary"""
    regions = download_resources(state_id, resource_id)
    save_resources(state_id, regions, resource_id)
    print_resources(regions)
    if need_refill(regions, 25):
        max_seconds = max_refill_seconds(regions, 25, 900)
        random_seconds = random.randint(0, max_seconds)
        random_time_delta = timedelta(seconds=random_seconds)
        scheduled_date = datetime.now() + random_time_delta
        job_id = 'refill_{}_{}'.format(capital_id, resource_id)
        print('refill resource: {} at {} ({} minutes)'.format(
            resource_id,
            scheduled_date,
            round(random_time.seconds / 60)
        ))
        job = scheduler.get_job(job_id)
        if not job:
            scheduler.add_job(
                job_refill_resource,
                'date',
                args=[state_id, capital_id, resource_id],
                id=job_id,
                run_date=scheduled_date
            )

def job_refill_resource(state_id, capital_id, resource_id):
    """Execute refill job"""
    refill(state_id, capital_id, resource_id)

if __name__ == '__main__':
    # jobs
    # job_refill_resource(2788, 4002, 0)
    # job_check_resources(2788, 4002, 0)
    VN_CHECK_GOLD_JOB = scheduler.get_job('vn_check_gold')
    if not VN_CHECK_GOLD_JOB:
        scheduler.add_job(
            job_check_resources,
            'cron',
            args=[2788, 4002, 0],
            id='vn_check_gold',
            minute='0,15,30,45'
        )
    VN_CHECK_URANIUM_JOB = scheduler.get_job('vn_check_uranium')
    if not VN_CHECK_URANIUM_JOB:
        scheduler.add_job(
            job_check_resources,
            'cron',
            args=[2788, 4002, 11],
            id='vn_check_uranium',
            minute='0'
        )

    while True:
        time.sleep(100)
