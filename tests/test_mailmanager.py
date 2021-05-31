from unittest import TestCase
from ddt import ddt, data, unpack
from mailmanager import MailManager
from tests.private_test_data import test_connection_details


@ddt
class TestMailManager(TestCase):
    @data(*test_connection_details)
    @unpack
    def test_connect(self, host, username, password):
        manager = MailManager(host=host, username=username, password=password)
        try:
            manager.connect()
        except Exception as e:
            self.fail(f"Connect failed, host={host}, user={username}, password={password}")

    @data(test_connection_details[0])
    @unpack
    def test_get_mails(self, host, username, password):
        manager = MailManager(host=host, username=username, password=password)
        manager.connect()

        num_emails = manager.get_num_mails()
        id_list = manager.get_mail_ids()
        from_val, subject, parts = manager.get_message_by_id(id_list[-3])

        self.assertEqual(9, num_emails)
