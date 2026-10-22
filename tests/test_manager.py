import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from alarmclock.manager import AlarmManager
from alarmclock.models import Alarm


class AlarmManagerTests(unittest.TestCase):
    def setUp(self):
        self.manager = AlarmManager()

    def test_add_alarm_assigns_incrementing_ids_and_strips_label(self):
        future = datetime.now() + timedelta(hours=1)
        with patch("builtins.print"):
            first = self.manager.add_alarm(future, "  Wake up  ")
            second = self.manager.add_alarm(future + timedelta(minutes=1), "Work")

        self.assertEqual(first.alarm_id, 1)
        self.assertEqual(first.label, "Wake up")
        self.assertEqual(second.alarm_id, 2)
        self.assertEqual(len(self.manager.alarms), 2)

    def test_blank_label_uses_default(self):
        with patch("builtins.print"):
            alarm = self.manager.add_alarm(datetime.now() + timedelta(hours=1), "   ")
        self.assertEqual(alarm.label, "Alarm")

    def test_add_alarm_rejects_past_time(self):
        with self.assertRaisesRegex(ValueError, "future"):
            self.manager.add_alarm(datetime.now() - timedelta(minutes=1))

    def test_get_alarm_returns_matching_alarm_or_none(self):
        alarm = Alarm(1, datetime.now() + timedelta(hours=1))
        self.manager.alarms.append(alarm)
        self.assertIs(self.manager.get_alarm(1), alarm)
        self.assertIsNone(self.manager.get_alarm(99))

    def test_delete_alarm_removes_existing_alarm(self):
        alarm = Alarm(1, datetime.now() + timedelta(hours=1))
        self.manager.alarms.append(alarm)
        with patch("builtins.print"):
            self.manager.delete_alarm(1)
        self.assertEqual(self.manager.alarms, [])

    def test_enable_and_disable_alarm(self):
        alarm = Alarm(1, datetime.now() + timedelta(hours=1), enabled=False)
        self.manager.alarms.append(alarm)
        with patch("builtins.print"):
            self.manager.enable_alarm(1, True)
        self.assertTrue(alarm.enabled)
        with patch("builtins.print"):
            self.manager.enable_alarm(1, False)
        self.assertFalse(alarm.enabled)

    def test_due_one_time_alarm_fires_and_is_disabled(self):
        due = datetime(2030, 1, 1, 8, 0)
        alarm = Alarm(1, due, "One time")
        self.manager.alarms.append(alarm)
        with patch("alarmclock.manager.datetime") as mocked_datetime, \
             patch("alarmclock.manager.alert_user") as mocked_alert:
            mocked_datetime.now.return_value = due + timedelta(seconds=1)
            self.manager.check_alarms()

        self.assertFalse(alarm.enabled)
        self.assertEqual(alarm.fired_for, "2030-01-01 08:00")
        mocked_alert.assert_called_once_with(alarm, unittest.mock.ANY)

    def test_due_daily_alarm_moves_to_next_day(self):
        due = datetime(2030, 1, 1, 8, 0)
        alarm = Alarm(1, due, "Daily", repeat_daily=True)
        self.manager.alarms.append(alarm)
        with patch("alarmclock.manager.datetime") as mocked_datetime, \
             patch("alarmclock.manager.alert_user") as mocked_alert:
            mocked_datetime.now.return_value = due + timedelta(seconds=1)
            self.manager.check_alarms()

        self.assertTrue(alarm.enabled)
        self.assertEqual(alarm.when, due + timedelta(days=1))
        mocked_alert.assert_called_once()

    def test_disabled_alarm_does_not_fire(self):
        due = datetime(2030, 1, 1, 8, 0)
        alarm = Alarm(1, due, enabled=False)
        self.manager.alarms.append(alarm)
        with patch("alarmclock.manager.datetime") as mocked_datetime, \
             patch("alarmclock.manager.alert_user") as mocked_alert:
            mocked_datetime.now.return_value = due + timedelta(seconds=1)
            self.manager.check_alarms()
        mocked_alert.assert_not_called()


if __name__ == "__main__":
    unittest.main()
