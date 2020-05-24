from unittest.mock import MagicMock

from app.handlers.util.reports import ReportsSender
from tests.base import BaseTestCase


class TestReports(BaseTestCase):
    def test_no_sender_no_crash(self):
        ReportsSender.instance = None
        ReportsSender.forward_user_message(MagicMock())
