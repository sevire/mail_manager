import reportitemmanager
import datetime

parser = reportitemmanager.ReportItemManager()

date_time = datetime.datetime.now()
date = date_time.date()
time = date_time.time()
parser.parse_string(date, time, "item:bottom val1:2")