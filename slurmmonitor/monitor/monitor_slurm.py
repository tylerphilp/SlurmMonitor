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

# %%


class SlurmMonitor:
    def __init__(self, job_id):
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

    def monitor(self, poll_interval=900, stop_event=None):  # Poll every 15
        while True:
            if stop_event and stop_event.is_set():
                self.messenger.send_message(f"🔪 SlurmMonitor killed by stop event.")
                break

            status = self.get_job_status()
            if status != self.last_status:
                self.messenger.send_message(f"⏳ Job {self.job_id} status: {status}")
                self.last_status = status
                if status == "COMPLETED":
                    self.messenger.send_message(f"🎉 Job {self.job_id} {status}")
                    break

            time.sleep(poll_interval)
