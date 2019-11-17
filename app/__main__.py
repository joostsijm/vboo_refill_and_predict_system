"""Main app"""

from datetime import datetime, timedelta
import random
import time

# libraries and data
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from pandas.plotting import register_matplotlib_converters

from telegram import ParseMode

from app import SCHEDULER, LOGGER, TELEGRAM_BOT
from app.api import download_resources, refill
from app.database import save_resources, get_resources, get_work_percentage
from app.app import need_refill, max_refill_seconds, print_resources


register_matplotlib_converters()

def job_check_resources(state_id, capital_id, resource_id, do_refill):
    """Check resources and refill if necessary"""
    regions = download_resources(state_id, resource_id)
    print_resources(regions)
    save_resources(state_id, regions, resource_id)
    if do_refill and need_refill(regions, 25):
        max_seconds = max_refill_seconds(regions, 25, 900)
        random_seconds = random.randint(0, max_seconds)
        random_time_delta = timedelta(seconds=random_seconds)
        scheduled_date = datetime.now() + random_time_delta
        job_id = 'refill_{}_{}'.format(capital_id, resource_id)
        LOGGER.info(
            'Refil resource %s at %s (%s minutes)',
            resource_id,
            scheduled_date,
            round(random_time_delta.seconds / 60)
        )
        job = SCHEDULER.get_job(job_id)
        if not job:
            SCHEDULER.add_job(
                job_refill_resource,
                'date',
                args=[state_id, capital_id, resource_id],
                id=job_id,
                run_date=scheduled_date
            )

def job_refill_resource(state_id, capital_id, resource_id):
    """Execute refill job"""
    refill(state_id, capital_id, resource_id)

def add_check_resources(state_id, capital_id, resource_id, do_refill, minute):
    """Add check resources job"""
    SCHEDULER.add_job(
        job_check_resources,
        'cron',
        args=[state_id, capital_id, resource_id, do_refill],
        id='{}_check_{}'.format(state_id, resource_id),
        replace_existing=True,
        minute=minute
    )

def job_send_telegram_update(state_id, group_id, resource_type):
    """Send telegram update"""
    message = get_work_percentage(state_id, resource_type, datetime.utcnow(), 1, 1)
    print(message)
    TELEGRAM_BOT.sendMessage(
        chat_id=group_id,
        text='```\n{}```'.format(message),
        parse_mode=ParseMode.MARKDOWN
    )


def graph():
    """make graph"""
    date = datetime.now()# + timedelta(1)
    region_4001 = get_resources(4001, date, 0)
    region_4002 = get_resources(4002, date, 0)
    region_4003 = get_resources(4003, date, 0)
    region_4004 = get_resources(4004, date, 0)
    region_4008 = get_resources(4008, date, 0)

    # resource_tmp = np.random.randn(2499)+range(2500, 1, -1)
    # Make a data frame
    data_frame = pd.DataFrame({
        # 'x': range(1, 2500),
        # '4001': resource_tmp,
        'x': list(region_4001.keys()),
        'Northern Netherlands': list(region_4001.values()),
        'Eastern Netherlands': list(region_4002.values()),
        'Western Netherlands': list(region_4003.values()),
        'Southern Netherlands': list(region_4004.values()),
        'Amsterdam': list(region_4008.values()),
    })

    major_fmt = mdates.DateFormatter('%m-%d %H:%M')

    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(major_fmt)
    fig.autofmt_xdate()
    end_date_time = date.replace(hour=19, minute=0, second=0, microsecond=0)
    start_date_time = end_date_time - timedelta(hours=24)
    ax.set_xlim([start_date_time, end_date_time])
    ax.set_ylim([0, 2700])

    # style
    plt.style.use('seaborn-darkgrid')

    # create a color palette
    palette = plt.get_cmap('Set1')

    # multiple line plot
    num = 0
    for column in data_frame.drop('x', axis=1):
        num += 1
        plt.plot(
            data_frame['x'],
            data_frame[column],
            marker='',
            color=palette(num),
            linewidth=1,
            alpha=0.9,
            label=column
        )

    # Add legend
    plt.legend(loc=3, ncol=1)
    # plt.setp(plt.xticks()[1], rotation=30, ha='right')

    # Add titles
    plt.title(
        'Resource limit left | {}'.format(date.strftime('%Y-%m-%d')),
        loc='left',
        fontsize=12,
        fontweight=1
    )
    plt.xlabel("Time")
    plt.ylabel("Resources")

    plt.savefig('foo.png')

if __name__ == '__main__':
    # job_refill_resource(2788, 4002, 0)
    # job_check_resources(2788, 4002, 0, False) # VN
    # job_check_resources(2620, 4002, 0, False) # Zeelandiae
    graph()
    exit()
    # get_resources(4001, datetime.now(), 0)

    # VN
    add_check_resources(2788, 4008, 0, True, '0,15,30,45')
    add_check_resources(2788, 4008, 11, True, '0')
    # Zeelandiae
    add_check_resources(2620, 0, 0, False, '50')
    # Belgium
    add_check_resources(2604, 0, 0, False, '40')

    SCHEDULER.add_job(
        job_send_telegram_update,
        'cron',
        args=[2788, '@vn_resources', 0],
        id='job_send_telegram_update',
        replace_existing=True,
        minute='5'
    )

    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt:
        LOGGER.info('Exiting application')
        SCHEDULER.shutdown()
        exit()
