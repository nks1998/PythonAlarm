import unittest
from unittest.mock import patch

from alarmclock.cli import AlarmCLI


class AlarmCLITests(unittest.TestCase):
    def setUp(self):
        self.cli = AlarmCLI()

    def test_quit_stops_manager(self):
        with patch("builtins.print"):
            self.cli.handle_command("quit")
        self.assertFalse(self.cli.manager.running)

    def test_invalid_id_is_reported(self):
        with patch("builtins.print") as mocked_print:
            self.cli.handle_command("delete abc")
        self.assertIn("integer", mocked_print.call_args.args[0])

    def test_command_without_required_id_shows_usage(self):
        with patch("builtins.print") as mocked_print:
            self.cli.handle_command("off")
        self.assertIn("Usage", mocked_print.call_args.args[0])

    def test_unknown_command_is_reported(self):
        with patch("builtins.print") as mocked_print:
            self.cli.handle_command("launch")
        self.assertIn("Unknown command", mocked_print.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
