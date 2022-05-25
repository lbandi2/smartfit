import re
from utils import get_days, to_english

class WorkingHours:
    def __init__(self, lst, language):
        self.language = language
        self.splitter = ' a '
        self.days = get_days(self.language, abbr=False)
        self.days_abbr = get_days(self.language, abbr=True)
        self.start_list = lst
        self.working_hours = self.get_working_hours()

    def _is_one_day(self, day):
        "Checks if there's more than one day in the string"
        day_list = get_days('es', abbr=True)

        regexp_test = f'({"|".join(day_list)})'
        return False if len(re.findall(regexp_test, day)) == 2 else True

    def _expand_list_of_days(self, day, hours):
        "Returns a list of days and time if string has more than one day"

        day_parts = day.split(self.splitter)
        day_list = get_days('es', abbr=True)

        if not self._is_one_day(day):
            days = [
                [day, hours] 
                for day in day_list [
                    day_list.index(day_parts[0]):day_list.index(day_parts[1])+1
                    ]
            ]
            return days

        return day, hours

    def get_days_and_hours(self, day, hours):
        day = self._expand_list_of_days(day, hours)

        schedule = []
        if type(day) is list:
            for x in day:
                schedule.append(x)
        else:
            schedule.append(list(day))
        return schedule

    def get_working_hours(self):
        "Gets fields corresponding to gym business hours"

        schedule = {}

        for item in self.start_list:
            day = item[0]
            hours = item[1].split(' - ')
            openning_time = int(hours[0].replace('h', ''))
            closing_time = int(hours[1].replace('h', ''))
            working_hours = [openning_time, closing_time]

            day = self.get_days_and_hours(day, working_hours)

            if type(day) is list:
                for item in day:
                    dow = item[0]
                    if self.language == 'en':
                        dow = to_english(dow, abbr=True)
                    hours = item[1]
                    schedule[dow] = hours
            else:
                day = list(day)
                dow = day[0]
                if self.language == 'en':
                    dow = to_english(dow, abbr=True)
                hours = day[1]
                schedule[dow] = hours

        return schedule

