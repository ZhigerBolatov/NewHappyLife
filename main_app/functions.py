from datetime import datetime


def datetime_serialize(datetime_str):
    datetime_obj = datetime.fromisoformat(datetime_str)
    result = {
        "date": datetime_obj.day,
        "month": datetime_obj.month,
        "year": datetime_obj.year,
        "time": datetime_obj.strftime("%H:%M")
    }
    return result
