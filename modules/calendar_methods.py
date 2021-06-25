import datetime
import calendar


month_names = {
    1:"Январь",
    2:"Февраль",
    3:"Март",
    4:"Апрель",
    5:"Май",
    6:"Июнь",
    7:"Июль",
    8:"Август",
    9:"Сентябрь",
    10:"Октябрь",
    11:"Ноябрь",
    12:"Декабрь",

}

def _add_one_month(orig_date):
    """ Прибавляет месяц к дате """
    new_year = orig_date.year
    new_month = orig_date.month + 1
    if new_month > 12:
        new_year += 1
        new_month -= 12
    # last_day_of_month = calendar.monthrange(new_year, new_month)[1]
    # new_day = min(orig_date.day, last_day_of_month)
    return orig_date.replace(year=new_year, month=new_month, day=1)


def _get_days(entry_date, out_date) -> list:
    """ Возвращает дни месяца """
    days_range = range(abs((entry_date-out_date).days))
    day_list = [(entry_date + datetime.timedelta(days=day)) for day in days_range]
    return day_list


def get_months() -> list:
    this_day = datetime.datetime.now()
    first_month = this_day
    second_month = _add_one_month(first_month)
    third_monts = _add_one_month(second_month)
    month_list = [
        (first_month.month, first_month.year, month_names[first_month.month]),
        (second_month.month, second_month.year, month_names[second_month.month]),
        (third_monts.month, third_monts.year, month_names[third_monts.month])
        ]
    return month_list


def get_calendar_data(month_number:int) -> dict:
    """ Возвращает данные для календаря """
    this_day = datetime.datetime.now()
    first_month = this_day
    second_month = _add_one_month(first_month)
    third_monts = _add_one_month(second_month)
    fourth_month = _add_one_month(third_monts)
    if month_number == first_month.month:
        return {
            "name": month_names[first_month.month],
            "month": first_month.month,
            "year": first_month.year,
            "days": [i for i in _get_days(first_month, second_month) if i.day >= this_day.day],
            "full_date": first_month.date    }

    elif month_number == second_month.month:
        return {
            "name": month_names[second_month.month],
            "month": second_month.month,
            "year": second_month.year,
            "days": _get_days(second_month, third_monts),
            "full_date": second_month.date
        }

    elif month_number == third_monts.month:
        return {
            "name": month_names[third_monts.month],
            "month": third_monts.month,
            "year": third_monts.year,
            "days": _get_days(third_monts, fourth_month),
            "full_date": third_monts.date
        }


