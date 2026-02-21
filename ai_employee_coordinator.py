"""
Main module to coordinate all AI Employee skills.

This module provides a unified interface to all the individual skills
and coordinates their operation according to the Bronze Tier requirements.
"""

import os
from pathlib import Path
from datetime import datetime

from skills.file_processor_skill import FileProcessingSkill
from skills.task_manager_skill import TaskManagementSkill
from skills.notification_skill import NotificationSkill
from skills.plan_generator_skill import PlanGeneratorSkill


class AIEmployeeSkillsCoordinator:
    """
    Coordinator class that brings together all the individual skills
    to operate as a unified AI Employee system.
    """

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.file_processor = FileProcessingSkill(vault_path)
        self.task_manager = TaskManagementSkill(vault_path)
        self.notification = NotificationSkill(vault_path)
        self.plan_generator = PlanGeneratorSkill(vault_path)

    def run_bronze_tier_workflow(self):
        """
        Execute the complete Bronze Tier workflow:
        1. Process any items in the Inbox
        2. Process any pending tasks in Needs_Action
        3. Update the dashboard with status
        """
        print("Starting Bronze Tier workflow...")

        # Process Inbox items
        inbox_processed = self.task_manager.process_inbox_items()
        if inbox_processed:
            self.notification.send_notification(
                f"Processed {len(inbox_processed)} inbox items",
                priority="normal",
                category="task_processing"
            )

        # Process Needs Action items
        processed_files = self.file_processor.process_needs_action_items()
        if processed_files:
            self.notification.send_notification(
                f"Processed {len(processed_files)} action items",
                priority="normal",
                category="file_processing"
            )

        # Update system status
        file_proc_status = self.file_processor.get_status()
        task_mng_status = self.task_manager.get_status()

        self.notification.update_system_status(
            status="Operational",
            active_watchers=1,  # File system watcher is active
            pending_actions=task_mng_status['needs_action_pending'],
            tasks_completed=task_mng_status['tasks_completed']
        )

        self.notification.send_notification(
            "Bronze Tier workflow completed successfully",
            priority="normal",
            category="system"
        )

        return {
            'inbox_processed': len(inbox_processed),
            'action_items_processed': len(processed_files),
            'timestamp': datetime.now().isoformat()
        }

    def run_silver_tier_workflow(self):
        """
        Execute the complete Silver Tier workflow:
        1. Run Bronze Tier workflow
        2. Generate plans for complex tasks
        3. Process any planning needs
        4. Update the dashboard with extended status
        """
        print("Starting Silver Tier workflow...")

        # First run the Bronze Tier workflow
        bronze_result = self.run_bronze_tier_workflow()

        # Generate plans for tasks that need planning
        planned_tasks = self.plan_generator.process_needs_action_for_planning()
        if planned_tasks:
            self.notification.send_notification(
                f"Created {len(planned_tasks)} plans for complex tasks",
                priority="normal",
                category="planning"
            )

        # Update system status with additional Silver Tier metrics
        file_proc_status = self.file_processor.get_status()
        task_mng_status = self.task_manager.get_status()
        plan_gen_status = self.plan_generator.get_status()

        self.notification.update_system_status(
            status="Operational",
            active_watchers=1,  # File system watcher is active
            pending_actions=task_mng_status['needs_action_pending'],
            tasks_completed=task_mng_status['tasks_completed']
        )

        # Add Silver Tier specific notifications
        self.notification.send_notification(
            f"Generated {plan_gen_status['plans_created']} plans",
            priority="normal",
            category="planning"
        )

        self.notification.send_notification(
            "Silver Tier workflow completed successfully",
            priority="normal",
            category="system"
        )

        return {
            'bronze_result': bronze_result,
            'plans_created': len(planned_tasks),
            'timestamp': datetime.now().isoformat()
        }

    def run_continuous_monitoring(self, interval_seconds=60):
        """
        Run continuous monitoring loop (simulated for Bronze Tier).
        In a real implementation, this would run indefinitely.
        """
        import time

        print(f"Starting continuous monitoring (interval: {interval_seconds}s)...")

        try:
            for i in range(5):  # Simulate 5 cycles for demo
                result = self.run_bronze_tier_workflow()
                print(f"Cycle {i+1} completed: {result}")

                if i < 4:  # Don't sleep after the last iteration
                    print(f"Waiting {interval_seconds}s until next cycle...")
                    time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")

    def get_overall_status(self):
        """Get the overall status of all skills."""
        return {
            'file_processing': self.file_processor.get_status(),
            'task_management': self.task_manager.get_status(),
            'notifications': self.notification.get_status(),
            'planning': self.plan_generator.get_status(),
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Main function to run the AI Employee skills coordinator."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ai_employee_coordinator.py <vault_path> [tier]")
        print("Example: python ai_employee_coordinator.py ./AI_Employee_Vault")
        print("Example: python ai_employee_coordinator.py ./AI_Employee_Vault bronze")
        print("Example: python ai_employee_coordinator.py ./AI_Employee_Vault silver")
        return

    vault_path = sys.argv[1]
    tier = sys.argv[2] if len(sys.argv) > 2 else "silver"  # Default to silver tier

    print(f"Initializing AI Employee with vault: {vault_path}")
    print(f"Running {tier.capitalize()} Tier workflow...")

    # Create the coordinator
    coordinator = AIEmployeeSkillsCoordinator(vault_path)

    # Run the appropriate tier workflow
    if tier.lower() == "bronze":
        print("\nRunning Bronze Tier workflow...")
        result = coordinator.run_bronze_tier_workflow()
    elif tier.lower() == "silver":
        print("\nRunning Silver Tier workflow...")
        result = coordinator.run_silver_tier_workflow()
    else:
        print(f"Unknown tier: {tier}. Defaulting to Silver Tier.")
        print("\nRunning Silver Tier workflow...")
        result = coordinator.run_silver_tier_workflow()

    print(f"Workflow result: {result}")

    # Display overall status
    status = coordinator.get_overall_status()
    print(f"\nOverall system status: {status}")


if __name__ == "__main__":
    main()