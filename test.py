from datetime import datetime
from croniter import croniter
import pytz


def get_current_date_time():
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz)


def test_cron(start_cron, stop_cron, machine_state="stop"):
    '''
        find stop and start region for current 24 hour current day
    '''

    current_datetime = get_current_date_time()
    start_cr = croniter(start_cron, ret_type=datetime, start_time=current_datetime)
    end_cr = croniter(stop_cron, ret_type=datetime, start_time=current_datetime)
    next_start = {
        "time": start_cr.get_next(),
        "type": "start"
    }
    previous_start = {
        "time": start_cr.get_prev(),
        "type": "start"
    }

    next_stop = {
        "time": end_cr.get_next(),
        "type": "stop"
    }

    previous_stop = {
        "time": end_cr.get_prev(),
        "type": "stop"
    }

    '''
        find start region   
    '''
    sorted_previous = sorted([previous_start, previous_stop], key=lambda k: k.get("time"))
    sorted_next = sorted([next_start, next_stop], key=lambda k: k.get("time"))

    print(sorted_previous[1].get("time"), sorted_previous[1].get("type"))
    print(sorted_next[0].get("time"), sorted_next[0].get("type"))

    last_state = sorted_previous[1].get("type")
    next_state = sorted_next[0].get("type")

    action = last_state
    if action != machine_state:
        print("perform action", action)
    else:
        print("no action needed")


test_cron("0 9 * * *", "0 21 * * *", "start")
