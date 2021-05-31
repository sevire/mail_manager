import re
import datetime
import reportingitem

RE_PARSESTRING = r'(date|time|item|val):([^\s]+)'


class ReportItemManager(object):
    def __init__(self):
        self.item = None
        self.date = None
        self.time = None
        self.value = None

    # Used to reset before parsing each token in each email
    def reset(self):
        self.__init__()

    # Parses item string. Date and Time passed in from email header as default values to use where required.
    def parse_string(self, date, time, parse_string):
        # Initialise date and time fields from email
        self.reset()
        self.date = date
        self.time = time

        lowercase_parse_string = parse_string.lower()
        match_array = re.findall(RE_PARSESTRING, lowercase_parse_string)
        if match_array:
            for i in range(0, len(match_array)):
                key_name = match_array[i][0]
                value = match_array[i][1]
                self.parse_token(key_name, value)
        item_object = reportingitem.ReportingItem(self.item, self.date, self.time, self.value)
        return item_object

    def parse_token(self, key, value):
        parsed = False
        if key == 'date':
            match = False
            format_string = "%Y-%m-%d"
            try:
                self.date = datetime.datetime.strptime(value, format_string).date()
                match = True
                parsed = True
            except:
                print(f'No match for date with format {format_string}')
            if not match:
                format_string = "%Y/%m/%d"
                try:
                    self.date = datetime.datetime.strptime(value, format_string).date()
                    match = True
                    parsed = True
                except:
                    print(f'No match for date with format {format_string}')
        elif key == 'time':
            match = False
            format_string = "%H:%M"
            try:
                self.time = datetime.datetime.strptime(value, format_string).time()
                match = True
                parsed = True
            except:
                print(f'No match for time with format {format_string}')
        elif key == 'item':
            if reportingitem.ReportingItem.is_valid_item(value):
                self.item = value
                parsed = True
            else:
                self.item = '###invalid###'
        elif key == 'val':
            self.value = value
            parsed = True
