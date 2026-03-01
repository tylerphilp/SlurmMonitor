# %%
import pytest
import threading
import sys

sys.path.append(".")

from unittest.mock import MagicMock, patch
from slurmmonitor import SlurmMonitor, SlackMessenger
from subprocess import CompletedProcess


# %%
# Set up unit tests
def test_get_job_pending():
    """
    Check whether a pending response will be returned
    """
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="PENDING\n")
        monitor = SlurmMonitor("12345")
        status = monitor.get_job_status()
        assert status == "PENDING"


def test_get_job_running():
    """
    Check whether a job is running
    """
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="")
        monitor = SlurmMonitor("12345")
        status = monitor.get_job_status()
        assert status == "COMPLETED"


def test_monitor_triggers_slack_message():
    """
    Check whether the message is actually sent
    """
    with (
        patch.object(SlackMessenger, "send_message") as mock_send,
        patch.object(
            SlurmMonitor,
            "get_job_status",
            side_effect=["PENDING", "RUNNING", "COMPLETED"],
        ),
    ):
        monitor = SlurmMonitor("12345")
        monitor.monitor(poll_interval=0)
        assert (
            mock_send.call_count == 4
        )  # For the initialisation, then 3 types of follow up call


def test_runs_background():
    """
    Confirms this bad boi runs in the background, not the main thread
    """
    with (
        patch.object(SlackMessenger, "send_message"),
        patch.object(SlurmMonitor, "get_job_status", return_value="RUNNING"),
    ):
        monitor = SlurmMonitor("12345")
        thread = threading.Thread(target=monitor.monitor, kwargs={"poll_interval": 0})
        thread.start()
        assert thread.is_alive()

        monitor._stop()
        thread.join(timeout=2)
        assert not thread.is_alive()
