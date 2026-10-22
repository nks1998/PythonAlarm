import unittest
from datetime import datetime, timedelta

from alarmclock.models import Alarm


class AlarmModelTests(unittest.TestCase):
    def test_next_time_returns_scheduled_time_by_default(self):
        scheduled = datetime(2030, 1, 1, 8, 30)
        alarm = Alarm(1, scheduled, "Wake up")
        self.assertEqual(alarm.next_time(), scheduled)

    def test_next_time_returns_snooze_time_when_present(self):
        scheduled = datetime(2030, 1, 1, 8, 30)
        snooze_until = scheduled + timedelta(minutes=5)
        alarm = Alarm(1, scheduled, "Wake up", snooze_until=snooze_until)
        self.assertEqual(alarm.next_time(), snooze_until)


if __name__ == "__main__":
    unittest.main()
