import imaplib
import email
import os
import webbrowser
from email.header import decode_header


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
        self.mail.select("INBOX")  # connect to inbox.

    def get_num_mails(self):
        if self.id_list is None:
            self.get_mail_ids()
        return len(self.id_list)

    def get_mail_ids(self):
        mail_type, data = self.mail.search(None, 'ALL')
        mail_ids = data[0]
        self.id_list = mail_ids.split()

        return self.id_list

    def get_message_by_id(self, msg_id):
        typ, data = self.mail.fetch(msg_id, '(RFC822)')
        response = data[0]  # Only expecting 1 reply as only asked for one email

        parts = None
        subject = None
        from_val = None

        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])

            # decode the email subject
            coded_subject, encoding = decode_header(msg["Subject"])[0]

            if isinstance(coded_subject, bytes):
                subject = coded_subject.decode(encoding)
            else:
                subject = coded_subject  # Wasn't encoded so just copy over

            # decode email sender
            coded_from, encoding = decode_header(msg.get("From"))[0]
            if isinstance(coded_from, bytes):
                from_val = coded_from.decode(encoding)
            else:
                from_val = coded_from  # Wasn't encoded so just copy over

            if msg.is_multipart():
                parts = self.process_multi_part_msg(msg, subject)
            else:
                parts = self.process_single_part_msg(msg)
        else:
            print(f"Not a tuple (I don't know why!!)")
        return from_val, subject, parts

    def process_html_msg(self, body, subject):
        # if it's HTML, create a new HTML file and open it in browser
        folder_name = self._clean(subject)
        if not os.path.isdir(folder_name):
            # make a folder for this email (named after the subject)
            os.mkdir(folder_name)
        filename = "index.html"
        filepath = os.path.join(folder_name, filename)
        # write the file
        open(filepath, "w").write(body)
        # open in the default browser
        webbrowser.open(filepath)

    @staticmethod
    def process_single_part_msg(msg):
        # extract content type of email
        content_type = msg.get_content_type()
        # get the email body
        body = msg.get_payload(decode=True).decode()
        if content_type == "text/plain":
            # print only text email parts
            print(body)
        return [(body, content_type)]  # Only one part but return as list for compatibility with multi-part

    def process_multi_part_msg(self, msg, subject):
        # iterate over email parts
        parts = []
        for part in msg.walk():
            # extract content type of email
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            body = part.get_payload(decode=True).decode()
            if content_type == "text/plain" and "attachment" not in content_disposition:
                # print text/plain emails and skip attachments
                print(body)
            elif "attachment" in content_disposition:
                # download attachment
                filename = part.get_filename()
                if filename:
                    folder_name = self._clean(subject)
                    if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        os.mkdir(folder_name)
                    filepath = os.path.join(folder_name, filename)
                    # download attachment and save it
                    open(filepath, "wb").write(part.get_payload(decode=True))
            parts.append((body, content_type))
        return parts

    @staticmethod
    def _clean(text):
        # clean text for creating a folder
        return "".join(c if c.isalnum() else "_" for c in text)
