"""Command-line interface and interactive loop."""
from datetime import datetime
import sys

from .manager import AlarmManager


HELP_TEXT = """Commands:
  add       Add an alarm (asks for date/time, label, repeat)
  list      List alarms and time remaining
  delete ID Delete an alarm
  off ID    Disable an alarm
  on ID     Enable an alarm
  help      Show commands
  quit      Stop the alarm clock

Time format: YYYY-MM-DD HH:MM (24-hour clock)."""


class AlarmCLI:
    def __init__(self) -> None:
        self.manager = AlarmManager()

    def print_help(self) -> None:
        print(HELP_TEXT)

    def prompt_add(self) -> None:
        raw = input("When? (YYYY-MM-DD HH:MM): ").strip()
        when = datetime.strptime(raw, "%Y-%m-%d %H:%M")
        if when <= datetime.now():
            raise ValueError("Choose a time in the future.")
        label = input("Label (optional): ").strip() or "Alarm"
        repeat = input("Repeat every day? [y/N]: ").strip().lower() == "y"
        self.manager.add_alarm(when, label, repeat)

    def handle_command(self, command: str) -> None:
        parts = command.split()
        if not parts:
            return
        action = parts[0].lower()
        if action == "help":
            self.print_help()
        elif action == "list":
            self.manager.list_alarms()
        elif action == "add":
            self.prompt_add()
        elif action in {"delete", "on", "off"}:
            if len(parts) != 2:
                print(f"Usage: {action} ID")
                return
            try:
                alarm_id = int(parts[1])
            except ValueError:
                print("Alarm ID must be an integer.")
                return
            if alarm_id < 1:
                print("Alarm ID must be a positive integer.")
                return
            if action == "delete":
                self.manager.delete_alarm(alarm_id)
            else:
                self.manager.enable_alarm(alarm_id, action == "on")
        elif action in {"quit", "exit"}:
            self.manager.running = False
            print("Alarm clock stopped.")
        else:
            print(f"Unknown command: {action!r}. Type 'help' for commands.")

    def run(self) -> None:
        print("\\n  ALARM CLOCK — terminal edition")
        print("  Alarms are stored in memory. Keep this program running.")
        print("  Type 'help' to see commands.\\n")
        self.print_help()
        if not sys.stdin.isatty():
            print("\\nInteractive terminal required to enter commands. Exiting.")
            return
        try:
            while self.manager.running:
                self.manager.check_alarms()
                try:
                    import select
                    ready, _, _ = select.select([sys.stdin], [], [], 1.0)
                    if not ready:
                        continue
                    command = sys.stdin.readline()
                    if not command:
                        break
                    self.handle_command(command.strip())
                except (ImportError, OSError):
                    self.handle_command(input("\\n> ").strip())
                except (ValueError, OverflowError) as exc:
                    print(f"Invalid input: {exc}")
        except KeyboardInterrupt:
            print("\\nGoodbye — alarm clock stopped.")
        finally:
            self.manager.running = False


def main() -> None:
    AlarmCLI().run()
