"""Init"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

from hvs.models import Base, Region, DeepExploration, ResourceTrack, ResourceStat


load_dotenv()

# database
engine = create_engine(os.environ["DATABASE_URI"])
Session = sessionmaker(bind=engine)

# scheduler
scheduler = BackgroundScheduler()
scheduler.add_jobstore('sqlalchemy', url=os.environ["DATABASE_URI"])
scheduler.start()

# api
BASE_URL = os.environ["API_URL"]
HEADERS = {
    'Authorization': os.environ["AUTHORIZATION"]
}
