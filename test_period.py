import datetime


def find_start_period(
        target_day: int,
        current_day: datetime = datetime.datetime.utcnow()) -> datetime:
    """Возвращает datetime прошлонедельного заданного дня недели"""
    delta_to_day = target_day - current_day.weekday()
    if delta_to_day > 0:
        res_delta_day = 7 - delta_to_day
    else:
        res_delta_day = delta_to_day
    result_day = current_day + datetime.timedelta(days=res_delta_day)
    result_day = result_day.replace(hour=0, minute=0, second=0, microsecond=0)
    # return result_day
    return current_day.date()


x = find_start_period(0)
print(x)