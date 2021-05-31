import mailmanager
import reportitemmanager

mail_manager = mailmanager.MailManager('mail.genonline.co.uk', 'plreportcard@genonline.co.uk', 'SnowdonLuthi@r3141')
parser = reportitemmanager.ReportItemManager()

mail_manager.connect()
mails = mail_manager.get_emails()

date, time, subject = mail_manager.get_next_mail_data()
if subject is not None:
    stop = False
    while not stop:
        item_object = parser.parse_string(date, time, subject)
        item_object.print_fields()
        date, time, subject = mail_manager.get_next_mail_data()
        if subject is None:
            stop = True
