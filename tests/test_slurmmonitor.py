# %%
import pytest

from unittest.mock import MagicMock, patch
from slurmmonitor.monitor.monitor_slurm import SlurmMonitor
from slurmmonitor.slackbot.messenger import SlackMessenger
from subprocess import CompletedProcess

# %%


# %%
# Set up unit tests
def test_get_job_pending():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="PENDING\n")
        monitor = SlurmMonitor("12345", "dummy_token")
        status = monitor.get_job_status()
        assert status == "PENDING"


def test_get_job_running():
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="")
        monitor = SlurmMonitor("12345", "dummy_token")
        status = monitor.get_job_status()
        assert status == "COMPLETED"


def test_monitor_triggers_slack_message():
    with (
        patch.object(SlackMessenger, "send_message") as mock_send,
        patch.object(
            SlurmMonitor,
            "get_job_status",
            side_effect=["PENDING", "RUNNING", "COMPLETED"],
        ),
    ):
        monitor = SlurmMonitor("12345", "dummy_token")
        monitor.monitor(poll_interval=0)
        assert mock_send.call_count == 3
