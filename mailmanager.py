import imaplib
import email
import datetime
import dateutil
import dateutil.parser


class MailManager(object):
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.mail = None
        self.id_list = None
        self.mail_pointer = None

    def connect(self):
        self.mail = imaplib.IMAP4_SSL(self.host)
        self.mail.login(self.username, self.password)
        self.mail.select("inbox")  # connect to inbox.

    def init_mail_pointer(self):
        self.mail_pointer = len(self.id_list)-1

    def get_mails(self):
        mail_type, data = self.mail.search(None, 'ALL')
        mail_ids = data[0]
        self.id_list = mail_ids.split()
        self.init_mail_pointer()

    def get_next_mail_data(self):
        if self.mail_pointer < 0:
            return None, None, None
        else:
            mail_id = self.id_list[self.mail_pointer]
            try:
                typ, data = self.mail.fetch(mail_id, '(RFC822)')
                self.mail_pointer -= 1

                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_string(response_part[1])
                        email_subject = msg['subject']
                        date_time = msg['date']
                        datetime_object2 = dateutil.parser.parse(date_time)
                        date = datetime_object2.date()
                        time = datetime_object2.time()
                        return date, time, email_subject
            except Exception, e:
                print str(e)

