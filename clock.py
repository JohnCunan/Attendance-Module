import time
from datetime import date
import sys


def get_time():
    while True:
        return time.strftime('%I:%M:%S %p')


def get_date():
    while True:
        today = date.today()
        return today.strftime("%B %d, %Y")



