from app.mod_user.models import User
from datetime import datetime
import uuid, random, string
from random import randint

def string_datetime(value):
    year = value.year
    month = "%02d" % value.month
    day = "%02d" % value.day
    hour = "%02d" % value.hour
    minute = "%02d" % value.minute
    second = "%02d" % value.second
    result = "{}-{}-{} {}:{}:{}.001000".format(year, month, day, hour, minute, second)
    return result

def return_error(code, message):
    data_out = {
        'code': code,
        'status': message
    }
    return data_out, code

def generate_otp():
    return ''.join(str(randint(0, 9)) for _ in range(4))