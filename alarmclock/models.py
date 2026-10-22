"""Alarm data model."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Alarm:
    alarm_id: int
    when: datetime
    label: str = "Alarm"
    repeat_daily: bool = False
    enabled: bool = True
    snooze_until: Optional[datetime] = None
    fired_for: Optional[str] = None

    def next_time(self) -> datetime:
        """Return the next scheduled time, including a pending snooze."""
        return self.snooze_until or self.when
