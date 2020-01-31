"""General function module"""

import random
from datetime import datetime, timedelta

# libraries and data
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from pandas.plotting import register_matplotlib_converters

from telegram import ParseMode

from app import LOGGER, SCHEDULER, TELEGRAM_BOT, RESOURCE_NAMES, jobs, api, database


register_matplotlib_converters()

def check_resources(state_id, capital_id, resource_id, do_refill, alt):
    """Check resources and refill if necessary"""
    regions = api.download_resources(state_id, resource_id)
    print_resources(regions)
    refill_percentage = 25
    database.save_resources(state_id, regions, resource_id)
    if do_refill and need_refill(regions, refill_percentage):
        max_seconds = max_refill_seconds(regions, refill_percentage, 900)
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
                jobs.refill_resource,
                'date',
                args=[state_id, capital_id, resource_id, alt],
                id=job_id,
                run_date=scheduled_date
            )

def print_resources(regions):
    """print resources"""
    if regions:
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
    else:
        LOGGER.error('no region to print data')

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

def send_telegram_update(state_id, group_id, resource_name):
    """Send resource update to telegram"""
    date = datetime.now()
    # date = datetime.today().replace(hour=18, minute=5) - timedelta(1)
    resource_id = RESOURCE_NAMES[resource_name]
    message = database.get_work_percentage(state_id, resource_id, date, 1, 1)
    if message:
        print(message)
        TELEGRAM_BOT.sendMessage(
            chat_id=group_id,
            text='```\n{}```'.format(message),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        LOGGER.error('no data for Telegram message')

def graph():
    """make graph"""
    date = datetime.now() # - timedelta(1)
    region_4001 = database.get_resources(4001, date, 0)
    region_4002 = database.get_resources(4002, date, 0)
    region_4003 = database.get_resources(4003, date, 0)
    region_4004 = database.get_resources(4004, date, 0)
    region_4008 = database.get_resources(4008, date, 0)

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
    ax.set_ylim([0, 2500])

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
