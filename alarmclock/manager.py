"""Alarm creation, management, and scheduling."""
from datetime import datetime, timedelta
from typing import Optional

from .models import Alarm
from .notifications import alert_user


class AlarmManager:
    def __init__(self) -> None:
        self.alarms: list[Alarm] = []
        self.next_id = 1
        self.running = True

    def add_alarm(self, when: datetime, label: str = "Alarm", repeat_daily: bool = False) -> Alarm:
        if when <= datetime.now():
            raise ValueError("Choose a time in the future.")
        alarm = Alarm(self.next_id, when, label.strip() or "Alarm", repeat_daily)
        self.alarms.append(alarm)
        self.next_id += 1
        repeat = " (daily)" if repeat_daily else ""
        print(f"Added alarm #{alarm.alarm_id}: {when:%Y-%m-%d %H:%M}{repeat} — {alarm.label}")
        return alarm

    def get_alarm(self, alarm_id: int) -> Optional[Alarm]:
        return next((alarm for alarm in self.alarms if alarm.alarm_id == alarm_id), None)

    def list_alarms(self) -> None:
        if not self.alarms:
            print("No alarms set.")
            return
        now = datetime.now()
        print("\\nYour alarms")
        print("-" * 72)
        for alarm in self.alarms:
            next_when = alarm.next_time() if alarm.enabled else alarm.when
            if not alarm.enabled:
                status = "disabled"
            else:
                status = "daily" if alarm.repeat_daily else "once"
                if alarm.snooze_until:
                    status += ", snoozed"
            remaining = next_when - now
            if not alarm.enabled:
                delta = "—"
            elif remaining.total_seconds() > 0:
                delta = self._format_delta(int(remaining.total_seconds()))
            else:
                delta = "due"
            print(f"#{alarm.alarm_id:<3} {next_when:%Y-%m-%d %H:%M}  [{status}]  in {delta}  {alarm.label}")
        print("-" * 72)

    def delete_alarm(self, alarm_id: int) -> None:
        alarm = self.get_alarm(alarm_id)
        if alarm is None:
            print(f"No alarm found with ID #{alarm_id}.")
            return
        self.alarms.remove(alarm)
        print(f"Deleted alarm #{alarm_id}.")

    def enable_alarm(self, alarm_id: int, enabled: bool) -> None:
        alarm = self.get_alarm(alarm_id)
        if alarm is None:
            print(f"No alarm found with ID #{alarm_id}.")
            return
        alarm.enabled = enabled
        if enabled:
            alarm.fired_for = None
        print(f"Alarm #{alarm_id} {'enabled' if enabled else 'disabled'}.")

    @staticmethod
    def _format_delta(seconds: int) -> str:
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, _ = divmod(seconds, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes or not parts:
            parts.append(f"{minutes}m")
        return " ".join(parts)

    def check_alarms(self) -> None:
        now = datetime.now()
        for alarm in list(self.alarms):
            if not alarm.enabled:
                continue
            due = alarm.next_time()
            due_key = due.strftime("%Y-%m-%d %H:%M")
            if now < due or alarm.fired_for == due_key:
                continue

            alarm.fired_for = due_key
            alarm.snooze_until = None
            if alarm.repeat_daily:
                # Keep the daily schedule active before the notification begins.
                while alarm.when <= now:
                    alarm.when += timedelta(days=1)
            else:
                alarm.enabled = False
            alert_user(alarm, lambda: self.running)
