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

        # Hande timeouts and kill signal
        signal.signal(signal.SIGTERM, self.handle_termination)

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

    def monitor(self, poll_interval=900):  # Poll every 15
        while True:
            status = self.get_job_status()
            if status != self.last_status:
                self.messenger.send_message(f"⏳ Job {self.job_id} status: {status}")
                self.last_status = status
                if status == "COMPLETED":
                    self.messenger.send_message(f"🎉 Job {self.job_id} {status}")
                    break

            time.sleep(poll_interval)

        # Need to add some logic for when the job is killed (since this is initialised in the job)

    def handle_termination(self, signum, frame):
        self.messenger.send_message(
            f"❌ Job {self.job_id} was terminated (signal {signum}). Likely killed or timed out."
        )
        sys.exit(0)
