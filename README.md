# Python CLI Alarm Clock

A small terminal-only alarm clock built with the Python standard library.

## Requirements
- Python 3.9+
- No third-party packages

## Run
```bash
python3 main.py
```

Keep the process running for alarms to fire. Alarms are stored in memory and are cleared when the program exits.

## Commands
- `add` — create an alarm
- `list` — list alarms and time remaining
- `on ID` — enable an alarm
- `off ID` — disable an alarm
- `delete ID` — delete an alarm
- `help` — show commands
- `quit` — exit

Alarm time format: `YYYY-MM-DD HH:MM` (24-hour clock).
When an alarm rings, enter `s` to snooze for five minutes or `d` to dismiss.
