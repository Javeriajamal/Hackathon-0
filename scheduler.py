"""
Scheduler for AI Employee

Implements basic scheduling functionality for the Silver Tier requirement.
Supports both cron-style scheduling on Unix-like systems and Task Scheduler on Windows.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timedelta
import json
import time
import threading


class Scheduler:
    """Cross-platform scheduler for the AI Employee."""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.schedules_dir = self.vault_path / 'Schedules'
        self.logs_dir = self.vault_path / 'Logs'
        self.tasks_dir = self.vault_path / 'Tasks'

        # Create directories if they don't exist
        self.schedules_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

        # Determine the platform
        self.platform = platform.system().lower()

    def create_schedule(self, task_name, command, schedule_expression, description=""):
        """Create a scheduled task."""
        schedule_data = {
            "task_name": task_name,
            "command": command,
            "schedule": schedule_expression,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "enabled": True,
            "platform": self.platform
        }

        schedule_file = self.schedules_dir / f"{task_name}_schedule.json"
        with open(schedule_file, 'w') as f:
            json.dump(schedule_data, f, indent=2)

        print(f"Created schedule: {schedule_file}")

        # Register the schedule based on platform
        if self.platform == "windows":
            self._register_windows_task(task_name, command, schedule_expression)
        else:
            self._register_unix_cron(task_name, command, schedule_expression)

        return str(schedule_file)

    def _register_windows_task(self, task_name, command, schedule_expression):
        """Register a task in Windows Task Scheduler."""
        # Convert cron-like expression to Windows Task Scheduler format
        # This is a simplified conversion - real implementation would be more complex

        # Example: Convert simple expressions
        if schedule_expression == "@daily":
            # Daily at 9 AM
            schedule_part = "DAILY /ST 09:00"
        elif schedule_expression == "@hourly":
            # Hourly (would need to create multiple tasks in reality)
            schedule_part = "ONSTART"
        elif "0 9 * * *" in schedule_expression:
            # Daily at 9 AM
            schedule_part = "DAILY /ST 09:00"
        elif "*/30 * * * *" in schedule_expression:
            # Every 30 minutes (approximation)
            schedule_part = "MINUTE /MO 30"
        else:
            # Default to daily
            schedule_part = "DAILY /ST 09:00"

        # Create a batch file to run the command
        batch_file = self.tasks_dir / f"{task_name}.bat"
        with open(batch_file, 'w') as f:
            f.write(f"@echo off\n")
            f.write(f"cd {os.getcwd()}\n")
            f.write(f"echo Running scheduled task: {task_name} >> {self.logs_dir}/scheduler_log_{datetime.now().strftime('%Y-%m-%d')}.log\n")
            f.write(f"{command}\n")
            f.write(f"echo Task {task_name} completed at %date% %time% >> {self.logs_dir}/scheduler_log_{datetime.now().strftime('%Y-%m-%d')}.log\n")

        # Register the task with Windows Task Scheduler
        try:
            cmd = [
                "schtasks",
                "/create",
                "/tn", f"AI_Employee_{task_name}",
                "/tr", f'"{batch_file}"',
                "/sc", schedule_part.split()[0],
                "/mo", schedule_part.split()[1] if len(schedule_part.split()) > 1 else "DAILY",
                "/f"  # Force overwrite if exists
            ]

            # Parse the schedule_part to extract time if it exists
            if "/ST" in schedule_part:
                time_part = schedule_part.split("/ST")[1].split()[0]
                cmd.extend(["/st", time_part])

            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Registered Windows task: AI_Employee_{task_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error registering Windows task: {e}")

    def _register_unix_cron(self, task_name, command, schedule_expression):
        """Register a task in Unix cron."""
        # Create a shell script to run the command
        script_file = self.tasks_dir / f"{task_name}.sh"
        with open(script_file, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write(f"# Scheduled task: {task_name}\n")
            f.write(f"cd {os.getcwd()}\n")
            f.write(f"echo 'Running scheduled task: {task_name}' >> {self.logs_dir}/scheduler_log_{datetime.now().strftime('%Y-%m-%d')}.log\n")
            f.write(f"{command}\n")
            f.write(f"echo 'Task {task_name} completed at $(date)' >> {self.logs_dir}/scheduler_log_{datetime.now().strftime('%Y-%m-%d')}.log\n")

        # Make the script executable
        os.chmod(script_file, 0o755)

        # Add to crontab
        try:
            # Get current crontab
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            current_crontab = result.stdout if result.returncode == 0 else ""

            # Create new crontab entry
            comment = f"# AI Employee task: {task_name}"
            new_entry = f"{schedule_expression} {script_file}\n"

            # Check if this task is already in crontab
            if new_entry.strip() not in current_crontab:
                # Add the new entry
                new_crontab = current_crontab + f"\n{comment}\n{new_entry}\n"

                # Write new crontab
                with open('/tmp/new_crontab', 'w') as f:
                    f.write(new_crontab)

                subprocess.run(["crontab", "/tmp/new_crontab"], check=True)
                print(f"Added to crontab: {task_name}")
            else:
                print(f"Task already exists in crontab: {task_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error adding to crontab: {e}")

    def list_scheduled_tasks(self):
        """List all scheduled tasks."""
        scheduled_tasks = []

        # List schedule files
        for schedule_file in self.schedules_dir.glob("*.json"):
            with open(schedule_file, 'r') as f:
                try:
                    data = json.load(f)
                    scheduled_tasks.append(data)
                except json.JSONDecodeError:
                    continue

        return scheduled_tasks

    def remove_schedule(self, task_name):
        """Remove a scheduled task."""
        schedule_file = self.schedules_dir / f"{task_name}_schedule.json"
        if schedule_file.exists():
            schedule_file.unlink()
            print(f"Removed schedule: {task_name}")

        # Remove from system scheduler
        if self.platform == "windows":
            try:
                subprocess.run(["schtasks", "/delete", "/tn", f"AI_Employee_{task_name}", "/f"],
                             check=True, capture_output=True)
                print(f"Removed Windows task: AI_Employee_{task_name}")
            except subprocess.CalledProcessError as e:
                print(f"Error removing Windows task: {e}")
        else:
            try:
                # Remove from crontab
                result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
                if result.returncode == 0:
                    current_crontab = result.stdout

                    # Remove the entry for this task
                    lines = current_crontab.split('\n')
                    filtered_lines = []

                    skip_next = False
                    for i, line in enumerate(lines):
                        if f"# AI Employee task: {task_name}" in line:
                            skip_next = True
                            continue
                        if skip_next and f"{self.tasks_dir}/{task_name}.sh" in line:
                            skip_next = False
                            continue
                        if skip_next:
                            skip_next = False
                            continue
                        filtered_lines.append(line)

                    new_crontab = '\n'.join(filtered_lines)

                    # Write back to crontab
                    with open('/tmp/new_crontab', 'w') as f:
                        f.write(new_crontab)

                    subprocess.run(["crontab", "/tmp/new_crontab"], check=True)
                    print(f"Removed from crontab: {task_name}")
            except subprocess.CalledProcessError as e:
                print(f"Error removing from crontab: {e}")

    def run_scheduled_task_now(self, task_name):
        """Run a scheduled task immediately."""
        schedule_file = self.schedules_dir / f"{task_name}_schedule.json"
        if not schedule_file.exists():
            print(f"Schedule file not found: {task_name}")
            return False

        with open(schedule_file, 'r') as f:
            try:
                data = json.load(f)
                command = data.get('command', '')

                if command:
                    print(f"Running scheduled task '{task_name}' now...")
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)

                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "task_name": task_name,
                        "command": command,
                        "return_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr
                    }

                    log_file = self.logs_dir / f"scheduler_execution_log_{datetime.now().strftime('%Y-%m-%d')}.json"

                    # Load existing logs
                    logs = []
                    if log_file.exists():
                        try:
                            logs = json.loads(log_file.read_text())
                            if isinstance(logs, dict):
                                logs = [logs]
                        except json.JSONDecodeError:
                            logs = []

                    logs.append(log_entry)

                    # Write logs back
                    with open(log_file, 'w') as log_f:
                        json.dump(logs, log_f, indent=2)

                    if result.returncode == 0:
                        print(f"Task '{task_name}' executed successfully")
                        return True
                    else:
                        print(f"Task '{task_name}' failed with return code {result.returncode}")
                        print(f"Error: {result.stderr}")
                        return False
            except json.JSONDecodeError as e:
                print(f"Error reading schedule file: {e}")
                return False

    def get_scheduler_status(self):
        """Get the status of the scheduler."""
        scheduled_tasks = self.list_scheduled_tasks()

        return {
            "platform": self.platform,
            "scheduled_tasks_count": len(scheduled_tasks),
            "scheduled_tasks": [task['task_name'] for task in scheduled_tasks],
            "schedules_directory": str(self.schedules_dir),
            "logs_directory": str(self.logs_dir),
            "tasks_directory": str(self.tasks_dir),
            "last_update": datetime.now().isoformat()
        }


def main():
    """Main function to demonstrate the scheduler."""
    if len(sys.argv) < 2:
        print("Usage: python scheduler.py <vault_path> [--list|--remove TASK_NAME|--run TASK_NAME]")
        print("Example: python scheduler.py ./AI_Employee_Vault")
        print("Example: python scheduler.py ./AI_Employee_Vault --list")
        print("Example: python scheduler.py ./AI_Employee_Vault --run linkedin_poster_daily")
        return

    vault_path = sys.argv[1]
    scheduler = Scheduler(vault_path)

    if len(sys.argv) > 2:
        if sys.argv[2] == "--list":
            tasks = scheduler.list_scheduled_tasks()
            print(f"Scheduled tasks ({len(tasks)}):")
            for task in tasks:
                print(f"  - {task['task_name']}: {task['command']} ({task['schedule']})")
        elif sys.argv[2] == "--remove" and len(sys.argv) > 3:
            task_name = sys.argv[3]
            scheduler.remove_schedule(task_name)
        elif sys.argv[2] == "--run" and len(sys.argv) > 3:
            task_name = sys.argv[3]
            scheduler.run_scheduled_task_now(task_name)
        else:
            print(f"Unknown command: {sys.argv[2]}")
    else:
        # Create some example schedules for the Silver Tier
        print("Creating example schedules for Silver Tier...")

        # Schedule LinkedIn posting (every 6 hours)
        scheduler.create_schedule(
            task_name="linkedin_poster",
            command=f"python {Path(__file__).parent}/linkedin_poster.py {vault_path} --test",
            schedule_expression="0 */6 * * *" if scheduler.platform != "windows" else "@hourly",
            description="Post business updates to LinkedIn to generate sales"
        )

        # Schedule Gmail checking (every 30 minutes)
        scheduler.create_schedule(
            task_name="gmail_checker",
            command=f"python {Path(__file__).parent}/gmail_watcher.py {vault_path} --test",
            schedule_expression="*/30 * * * *" if scheduler.platform != "windows" else "@hourly",
            description="Check Gmail for important emails"
        )

        # Schedule system status report (daily at 9 AM)
        scheduler.create_schedule(
            task_name="daily_report",
            command=f"python {Path(__file__).parent}/ai_employee_coordinator.py {vault_path}",
            schedule_expression="0 9 * * *" if scheduler.platform != "windows" else "DAILY /ST 09:00",
            description="Generate daily status report"
        )

        print("\nScheduler status:")
        status = scheduler.get_scheduler_status()
        for key, value in status.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()