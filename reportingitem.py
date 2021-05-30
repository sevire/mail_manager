from datetime import datetime, timedelta, time as t


# Class to represent a single reporting item. May refactor into sub-classes, one for each type of item as they are
# treated differently.
class ReportingItem:
    # List of all items which are recognised, plus:
    # - Default value (0 --> there is no default, None means Value not required)
    # - Unit of supplied value (e.g. minutes)
    # - Unit of converted value (e.g. hours)
    # Default value of 0 means value must be supplied.
    # Default value of None means value not required for this item (e.g. up, bed where time is used).
    __ITEMS = dict(
        squirt=(1, 'occurrences', 'occurrences'),
        web=(15, 'minutes', 'hours'),
        fantasy=(1, 'occurrences', 'occurrences'),
        up=(None, 'time', 'hours'),
        bed=(None, 'time', 'hours'),
        ogle=(1, 'occurrences', 'occurrences'),
        play=(0, 'occurrences', 'occurrences'),
        water=(1, 'occurrences', 'occurrences'),
        mail_missed=(1, 'occurrences', 'occurrences'),
        mail_late=(1, 'occurrences', 'occurrences'),
        absent=(1, 'occurrences', 'occurrences'),
        wee=(1, 'occurrences', 'occurrences'),
        clothes=(1, 'occurrences', 'occurrences')
    )

    # Initialiser, must have values for item, date, time.  the property val may not need a value if the value is already
    # in the time or date field (e.g. item 'up' needs a date and time.
    # Returns False if invalid data supplied, True otherwise
    def __init__(self, item, date, time, val):
        print 'Initialising item <%s>...' % item
        self.__value = None
        abort = False
        if not self.is_valid_item(item):
            print 'invalid item <%s>, can\'t continue' % item
            abort = True
        else:
            self.__item = item

        if not abort and date is None:
            print 'date is None, must be supplied, can\'t continue' % item
            abort = True
        else:
            self.__date = date

        if not abort and time is None:
            print 'time is None, must be supplied, can\'t continue' % item
            abort = True
        else:
            self.__time = time

        # Process supplied value:
        # - Validate to check that value has been provided if required
        # - Allocate default value if none provided but default value exists
        # for some items, val not required and for some a default value is assumed if nothing supplied
        if not abort and val is None:

            # if default value set to zero then value should have been supplied so abort, otherwise use default value.
            if self.__ITEMS[self.__item] == 0:
                print 'Item <%s> needs a value, but none supplied, aborting' % self.__item
                abort = True
            else:
                self.__input_value = self.__ITEMS[self.__item][0]

        else:
            # value supplied so use it
            self.__input_value = val

        if not abort:
            # We now have all fields set, so we can calculated converted value if appropriate.
            if self.__ITEMS[self.__item][1] == 'occurrences' and self.__ITEMS[self.__item][2] == 'occurrences':
                # Just counting number of times a thing happened so no conversion
                self.__value = int(self.__input_value)
            elif self.__ITEMS[self.__item][1] == 'time' and self.__ITEMS[self.__item][2] == 'hours':
                # Work out number of minutes from cut off time and then convert to hours
                self.__value = self.time_to_minutes_after_cutoff(self.__date, self.__time, self.__item)
            else:
                # Combination not recognised so abort
                print 'Unit conversion <%s> --> <%s> not recognised, aborting' % \
                      (self.__ITEMS[self.__item][1],
                       self.__ITEMS[self.__item][2])
                abort = True

        if not abort:
            print "Item <%s> created" % self.__item

    def get_item(self):
        return self.__item

    def get_date(self):
        return self.__date

    def get_time(self):
        return self.__time

    # Note we don't expose the input value now it has been converted to true value
    def get_value(self):
        return self.__value

    def print_fields(self):
        print '\nPrinting item <%s>...' % self.__item
        print 'date:            %s' % self.__date
        print 'time:            %s' % self.__time
        print 'item:            %s' % self.__item
        print 'val:             %s' % str(self.__input_value)
        print 'converted val:   %s\n' % str(self.__value)

    @staticmethod
    def time_to_minutes_after_cutoff(date, time, item):
        """
        :param date:
        :param time:
        :param item:
        :return:

        Works out number of minutes after cutoff depending upon whether this is a bed or up item.
        Array of tuples which represent the up and bed cutoffs for each day of week.  Python weeks start on Monday=0

        For getting up the cases are simple as we can assume that the time will always be the same day as the item.
        For going to bed there are more cases as the time could be after midnight, so the item will be recorded on the
        following day.
        """
        __CUTOFF_BY_DAY = [
            ('Monday', '08:00', '23:59'),
            ('Tuesday', '08:00', '23:59'),
            ('Wednesday', '08:00', '23:59'),
            ('Thursday', '08:00', '23:59'),
            ('Friday', '08:00', '23:59'),
            ('Saturday', '10:00', '23:59'),
            ('Sunday', '10:00', '23:59'),
        ]
        __CUTOFF_DAY_THRESHOLD = datetime.strptime("18:00", "%H:%M").time()

        if item == 'up':
            cutoff_tuple_index = 1
        else:
            cutoff_tuple_index = 2

        # Need to work out whether the time is late on previous day or early on supplied day.  Use threshold.
        # Only applies to bedtime so if item is 'up', just set to same date as supplied.
        if item == 'bed' and time < __CUTOFF_DAY_THRESHOLD:
            item_date = date - timedelta(days=1)
        else:
            item_date = date

        item_weekday_index = item_date.weekday()
        cutoff_time = datetime.strptime(__CUTOFF_BY_DAY[item_weekday_index][cutoff_tuple_index], "%H:%M").time()

        if item == 'bed' and cutoff_time < __CUTOFF_DAY_THRESHOLD:
            cutoff_date = item_date + timedelta(days=1)
        else:
            cutoff_date = item_date

        item_date_time = datetime.combine(date, time)  # I think this is right but not sure!
        cutoff_date_time = datetime.combine(cutoff_date, cutoff_time)

        # We should now have adjusted datetime objects for both bedtime and cutoff time so can compare directly
        delta_date_time = item_date_time - cutoff_date_time

        # if actual time isn't beyond the threshold then we should just record zero.  Delta time days will be negative
        # so test for that and adjust accordingly.
        if delta_date_time.days < 0:
            minutes_over = 0
        else:
            minutes_over = delta_date_time.seconds/60

        return minutes_over

    @staticmethod
    def is_valid_item(item):
        return item in ReportingItem.__ITEMS
