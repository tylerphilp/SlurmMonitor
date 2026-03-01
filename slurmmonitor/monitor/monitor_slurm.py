# Script for monitoring the slurm outputs
# and converting to a string for messenging

# Monitor the status of the job (pending, running, completed)
# Run every hour or so and report response
# %%
import subprocess
import time
import signal
import sys
from slurmmonitor.slackbot.messenger import SlackMessenger
import threading

# %%


class SlurmMonitor:
    def __init__(self, job_id):

        self._stop_event = threading.Event()

        self.job_id = job_id
        self.messenger = SlackMessenger()
        self.last_status = self.get_job_status()

        # Intialisation method
        self.messenger.send_message(
            f"✨ SlurmMonitor initialised for job: {self.job_id}. Current status: {self.last_status}"
        )

    def get_job_status(self):
        result = subprocess.run(
            ["squeue", "-j", str(self.job_id), "-h", "-o", "%T"],
            capture_output=True,
            text=True,
        )
        status = result.stdout.strip()
        return status if status else "COMPLETED"

    def _stop(self):
        # Signal the monitor loop directly & exit (call from any thread)
        self._stop_event.set()

    def monitor(
        self, poll_interval=900, stop_event=None, update_interval: int | None = None
    ):  # Poll every 15

        last_update_time = time.monotonic()

        while not self._stop_event.is_set():
            status = self.get_job_status()

            if status != self.last_status:
                self.messenger.send_message(f"⏳ Job {self.job_id} status: {status}")
                self.last_status = status

                if status == "COMPLETED":
                    self.messenger.send_message(f"🎉 Job {self.job_id} {status}")
                    break

            # Option for regular updates if the user wants
            elif update_interval is not None:
                elapsed = time.monotonic() - last_update_time
                if elapsed > update_interval:
                    self.messenger.send_message(
                        f"📊 Job {self.job_id} still {status}. Next update in: {update_interval} seconds"
                    )
                last_update_time = time.monotonic()

            # Use wait - it's responseive to any thread and will exit gracefully
            self._stop_event.wait(timeout=poll_interval)

            if self._stop_event.is_set():
                self.messenger.send_message(
                    f"🔪 SlurmMonitor for job {self.job_id} was stopped externally."
                )
