"""Terminal and operating-system alarm notifications."""
import os
import platform
import subprocess
import sys
from datetime import datetime, timedelta

from .models import Alarm


def play_sound() -> None:
    """Play a built-in OS sound when possible; otherwise use the terminal bell."""
    system = platform.system()
    try:
        if system == "Darwin":
            sound = "/System/Library/Sounds/Glass.aiff"
            if os.path.exists(sound):
                subprocess.Popen(
                    ["afplay", sound],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return
        elif system == "Linux":
            commands = (
                ["paplay", "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"],
                ["aplay", "/usr/share/sounds/alsa/Front_Center.wav"],
            )
            for command in commands:
                try:
                    subprocess.Popen(
                        command,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return
                except FileNotFoundError:
                    continue
    except OSError:
        pass
    print("\\a", end="", flush=True)


def alert_user(alarm: Alarm, running_check) -> None:
    """Ring until the user snoozes or dismisses the alarm."""
    print("\\n" + "=" * 56)
    print(f"⏰  ALARM #{alarm.alarm_id}: {alarm.label}")
    print(f"    {datetime.now():%A, %d %B %Y at %H:%M:%S}")
    print("=" * 56)
    print("Press [s] then Enter to snooze 5 minutes, [d] to dismiss.")

    try:
        import select

        if not sys.stdin.isatty():
            play_sound()
            print("Non-interactive terminal: alarm notification printed once.")
            return

        print("Choice [s/d]: ", end="", flush=True)
        while running_check():
            play_sound()
            ready, _, _ = select.select([sys.stdin], [], [], 2.0)
            if not ready:
                continue
            choice = sys.stdin.readline().strip().lower()
            if choice == "s":
                alarm.snooze_until = datetime.now() + timedelta(minutes=5)
                alarm.enabled = True
                print(f"Snoozed alarm #{alarm.alarm_id} until {alarm.snooze_until:%H:%M}.")
                return
            if choice == "d":
                print(f"Alarm #{alarm.alarm_id} dismissed.")
                return
            print("Enter 's' to snooze or 'd' to dismiss: ", end="", flush=True)
    except (ImportError, OSError):
        play_sound()
        try:
            choice = input("Choice [s/d]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return
        if choice == "s":
            alarm.snooze_until = datetime.now() + timedelta(minutes=5)
            alarm.enabled = True
            print(f"Snoozed alarm #{alarm.alarm_id} until {alarm.snooze_until:%H:%M}.")
        else:
            print("Alarm dismissed.")
