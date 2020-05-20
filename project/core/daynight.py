import datetime
import pytz
from flask_login import current_user
from flask import session

def eval_time():
    if session.get('daynight_pref'):
        if session['daynight_pref'] == "NIGHT":
            return "NIGHT"
        else:
            return "DAY"
    else:
        if current_user.is_authenticated:
            this_hour = datetime.datetime.now(tz=pytz.UTC).astimezone(pytz.timezone(current_user.preferences.timezone)).strftime('%H')
            if int(current_user.preferences.night_time_off) <= int(this_hour) < int(current_user.preferences.night_time_on):
                return "DAY"
            else:
                return "NIGHT"
        else:
            return "DAY"
