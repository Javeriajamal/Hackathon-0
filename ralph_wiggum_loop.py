"""
Ralph Wiggum Loop for AI Employee

Implements the persistence pattern for autonomous multi-step task completion.
The loop keeps Claude working until a task is complete, intercepting exit attempts
and continuing the work if the task is not yet finished.
"""

import time
import json
from pathlib import Path
from datetime import datetime
import os
import sys


class RalphWiggumLoop:
    """
    Implements the Ralph Wiggum pattern: a Stop hook that intercepts Claude's exit
    and feeds the prompt back if the task is not complete.
    """

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.tasks_dir = self.vault_path / 'Tasks'
        self.in_progress_dir = self.vault_path / 'In_Progress'
        self.done_dir = self.vault_path / 'Done'
        self.needs_action_dir = self.vault_path / 'Needs_Action'
        self.logs_dir = self.vault_path / 'Logs'

        # Create directories if they don't exist
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.in_progress_dir.mkdir(parents=True, exist_ok=True)
        self.done_dir.mkdir(parents=True, exist_ok=True)
        self.needs_action_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    def create_task(self, task_description, steps, priority="medium", max_iterations=10):
        """Create a multi-step task for the Ralph Wiggum loop."""
        task_id = f"TASK_{int(datetime.now().timestamp())}_{priority}"

        task_content = f"""---
task_id: {task_id}
description: "{task_description}"
status: pending
priority: {priority}
created_at: {datetime.now().isoformat()}
max_iterations: {max_iterations}
current_iteration: 0
steps: {len(steps)}
completed_steps: 0
---

# Task: {task_description}

## Objective
{task_description}

## Steps to Complete
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(steps)])}

## Current Progress
- [ ] Task initiated

## Expected Outcome
Complete all steps in the task successfully.

## Instructions for Completion
1. Process each step sequentially
2. Update progress as you complete each step
3. Mark the task as complete when all steps are finished
4. Move the task file to the Done folder when complete

## Current Status
- Status: In Progress
- Iteration: 0/{max_iterations}
- Steps Completed: 0/{len(steps)}

---
Task created by Ralph Wiggum Loop Manager
"""

        task_filename = f"{task_id}.md"
        task_path = self.tasks_dir / task_filename
        task_path.write_text(task_content)

        print(f"Created task: {task_path.name}")
        return str(task_path)

    def claim_task(self, task_path):
        """Claim a task for processing."""
        task_path = Path(task_path)
        task_id = task_path.stem

        # Move task to In_Progress
        in_progress_path = self.in_progress_dir / task_path.name
        task_path.rename(in_progress_path)

        # Update task status
        self._update_task_status(in_progress_path, "in_progress")

        print(f"Claimed task for processing: {task_path.name}")
        return str(in_progress_path)

    def _update_task_status(self, task_path, status):
        """Update the status of a task."""
        content = task_path.read_text(encoding='utf-8')

        lines = content.split('\n')
        updated_lines = []
        in_frontmatter = False
        frontmatter_end_idx = -1

        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    updated_lines.append(line)
                else:
                    in_frontmatter = False
                    updated_lines.append(line)
                    frontmatter_end_idx = i
                    break
            elif in_frontmatter and line.startswith('status:'):
                updated_lines.append(f'status: {status}')
            elif in_frontmatter and line.startswith('current_iteration:'):
                # Increment iteration if status is in_progress
                if status == "in_progress":
                    try:
                        current_val = int(line.split(':')[1].strip())
                        updated_lines.append(f'current_iteration: {current_val + 1}')
                    except:
                        updated_lines.append(f'current_iteration: 1')
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

        # Combine the updated frontmatter with the rest of the content
        if frontmatter_end_idx >= 0:
            new_content = '\n'.join(updated_lines) + '\n' + '\n'.join(lines[frontmatter_end_idx + 1:])
        else:
            # If no frontmatter found, add it at the beginning
            new_content = f"""---
status: {status}
---
""" + content

        task_path.write_text(new_content, encoding='utf-8')

    def update_task_progress(self, task_path, step_completed=None, additional_notes=None):
        """Update task progress with completed step."""
        task_path = Path(task_path)
        content = task_path.read_text(encoding='utf-8')

        # Update the progress section
        if step_completed:
            # Count existing completed steps
            lines = content.split('\n')
            completed_count = sum(1 for line in lines if line.strip().startswith('- [x] '))

            # Add the completed step to progress
            progress_marker = f"- [x] {step_completed}"

            # Find where to insert the progress update
            updated_lines = []
            progress_section_found = False

            for line in lines:
                if line.strip() == "## Current Progress":
                    progress_section_found = True
                    updated_lines.append(line)
                    updated_lines.append(progress_marker)
                elif progress_section_found and line.startswith('- [ ] Task initiated'):
                    # Replace the initial placeholder
                    updated_lines.append(progress_marker)
                elif line.startswith('- [ ] Task initiated') and not progress_section_found:
                    # If we didn't find the progress section, add it before this line
                    updated_lines.append("## Current Progress")
                    updated_lines.append(progress_marker)
                    updated_lines.append(line)
                else:
                    updated_lines.append(line)

            content = '\n'.join(updated_lines)

            # Update the status line
            lines = content.split('\n')
            updated_lines = []
            for line in lines:
                if line.startswith('- Steps Completed:'):
                    total_steps = len([l for l in content.split('\n') if l.strip().startswith('1.') or l.strip().startswith('2.') or l.strip().startswith('3.') or l.strip().startswith('4.') or l.strip().startswith('5.') or l.strip().startswith('6.') or l.strip().startswith('7.') or l.strip().startswith('8.') or l.strip().startswith('9.')])
                    updated_lines.append(f'- Steps Completed: {completed_count + 1}/{total_steps}')
                else:
                    updated_lines.append(line)

            content = '\n'.join(updated_lines)

        if additional_notes:
            content += f"\n## Additional Notes\n{additional_notes}\n"

        task_path.write_text(content, encoding='utf-8')

    def check_completion_criteria(self, task_path):
        """Check if the task is completed based on its content."""
        content = task_path.read_text(encoding='utf-8')

        # Check if all steps are marked as completed in the progress section
        lines = content.split('\n')
        total_steps = 0
        completed_steps = 0

        # Count total steps in the main steps section
        for line in lines:
            if line.strip().startswith('1.') or line.strip().startswith('2.') or line.strip().startswith('3.') or \
               line.strip().startswith('4.') or line.strip().startswith('5.') or line.strip().startswith('6.') or \
               line.strip().startswith('7.') or line.strip().startswith('8.') or line.strip().startswith('9.'):
                total_steps += 1

        # Count completed steps in the progress section
        in_progress_section = False
        for line in lines:
            if line.strip() == "## Current Progress":
                in_progress_section = True
            elif line.strip().startswith('## ') and line.strip() != "## Current Progress":
                in_progress_section = False
            elif in_progress_section and line.strip().startswith('- [x] '):
                completed_steps += 1

        # Task is complete if all steps are marked as completed
        return completed_steps >= total_steps

    def complete_task(self, task_path):
        """Complete a task by moving it to the Done folder."""
        task_path = Path(task_path)

        # Update final status
        self._update_task_status(task_path, "completed")

        # Add completion notes
        content = task_path.read_text(encoding='utf-8')
        completion_notes = f"""

## Task Completion
- **Completed by**: Ralph Wiggum Loop
- **Completed at**: {datetime.now().isoformat()}
- **Status**: Task moved to Done folder

---
Task completed by AI Employee using Ralph Wiggum persistence pattern
"""
        content += completion_notes

        # Move to Done folder
        done_path = self.done_dir / f"DONE_{task_path.name}"
        done_path.write_text(content, encoding='utf-8')

        # Remove original file
        task_path.unlink()

        print(f"Task completed and moved to Done: {done_path.name}")
        return str(done_path)

    def process_task_iteration(self, task_path):
        """Process one iteration of a task."""
        task_path = Path(task_path)

        # Read the current task state
        content = task_path.read_text(encoding='utf-8')

        # Get current iteration count
        current_iteration = 0
        max_iterations = 10  # default

        lines = content.split('\n')
        for line in lines:
            if line.startswith('current_iteration:'):
                try:
                    current_iteration = int(line.split(':')[1].strip())
                except:
                    current_iteration = 0
            elif line.startswith('max_iterations:'):
                try:
                    max_iterations = int(line.split(':')[1].strip())
                except:
                    max_iterations = 10

        # Check if we've exceeded max iterations
        if current_iteration >= max_iterations:
            print(f"Max iterations ({max_iterations}) reached for task {task_path.name}")
            self._update_task_status(task_path, "failed_max_iterations")
            return False, "max_iterations_exceeded"

        # Check if task is already complete
        if self.check_completion_criteria(task_path):
            print(f"Task {task_path.name} is complete")
            return True, "completed"

        # Continue processing - return that task is not yet complete
        print(f"Iteration {current_iteration + 1} of {max_iterations} for task {task_path.name}")
        return False, "continue"

    def run_ralph_loop(self, task_path, max_iterations=10):
        """Run the Ralph Wiggum loop for a specific task."""
        task_path = Path(task_path)

        print(f"Starting Ralph Wiggum loop for task: {task_path.name}")
        print(f"Max iterations: {max_iterations}")

        iteration = 0
        while iteration < max_iterations:
            # Process one iteration
            is_complete, status = self.process_task_iteration(task_path)

            if is_complete:
                # Task is complete, finish it
                self.complete_task(task_path)
                print(f"Ralph Wiggum loop completed task: {task_path.name}")
                return True

            if status == "max_iterations_exceeded":
                print(f"Ralph Wiggum loop stopped - max iterations exceeded for task: {task_path.name}")
                return False

            iteration += 1

            # Simulate Claude working on the task
            # In a real implementation, this would be where Claude processes the task
            print(f"Continuing work on task... (iteration {iteration})")

            # Update iteration count in the task file
            content = task_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            updated_lines = []

            for line in lines:
                if line.startswith('current_iteration:'):
                    updated_lines.append(f'current_iteration: {iteration}')
                else:
                    updated_lines.append(line)

            task_path.write_text('\n'.join(updated_lines), encoding='utf-8')

            # Small delay to simulate work
            time.sleep(1)

        # If we get here, max iterations were reached without completion
        self._update_task_status(task_path, "failed_max_iterations")
        print(f"Ralph Wiggum loop failed - max iterations reached for task: {task_path.name}")
        return False

    def get_status(self):
        """Get the status of the Ralph Wiggum system."""
        tasks_count = len(list(self.tasks_dir.glob("*.md")))
        in_progress_count = len(list(self.in_progress_dir.glob("*.md")))
        done_count = len(list(self.done_dir.glob("*.md")))
        needs_action_count = len(list(self.needs_action_dir.glob("*.md")))

        return {
            "tasks_pending": tasks_count,
            "tasks_in_progress": in_progress_count,
            "tasks_completed": done_count,
            "needs_action_items": needs_action_count,
            "last_update": datetime.now().isoformat()
        }


def main():
    """Main function to demonstrate the Ralph Wiggum Loop."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ralph_wiggum_loop.py <vault_path> [--demo]")
        print("Example: python ralph_wiggum_loop.py ./AI_Employee_Vault --demo")
        print("Example: python ralph_wiggum_loop.py ./AI_Employee_Vault --create-task 'Process invoices' 'Send emails' 'Update records'")
        return

    vault_path = sys.argv[1]
    ralph_loop = RalphWiggumLoop(vault_path)

    if "--demo" in sys.argv:
        print("Running Ralph Wiggum Loop demo...")

        # Create a sample multi-step task
        steps = [
            "Review pending invoices in accounting system",
            "Verify invoice details and amounts",
            "Process payments for approved invoices",
            "Update accounting records with payment status",
            "Generate payment confirmation emails",
            "Send confirmation emails to clients",
            "Archive processed invoices"
        ]

        task_path = ralph_loop.create_task(
            "Process weekly invoices and payments",
            steps,
            priority="high",
            max_iterations=5
        )

        print(f"Created demo task: {task_path}")

        # Claim and start processing the task
        claimed_task = ralph_loop.claim_task(Path(task_path))

        # Run the Ralph Wiggum loop on the task
        success = ralph_loop.run_ralph_loop(claimed_task, max_iterations=5)

        if success:
            print("Demo completed successfully!")
        else:
            print("Demo ended without completing the task.")

        # Show final status
        status = ralph_loop.get_status()
        print(f"Final status: {status}")

    elif sys.argv[2:3] == ["--create-task"]:
        # Create a custom task from command line arguments
        if len(sys.argv) < 4:
            print("Usage: python ralph_wiggum_loop.py <vault_path> --create-task <description> [steps...]")
            return

        description = sys.argv[3]
        steps = sys.argv[4:] if len(sys.argv) > 4 else ["Perform the required actions"]

        task_path = ralph_loop.create_task(
            description,
            steps,
            priority="medium",
            max_iterations=10
        )

        print(f"Created custom task: {task_path}")

    else:
        print("Ralph Wiggum Loop initialized.")
        print("Use --demo to run a demonstration.")
        print("Use --create-task to create a new task.")


if __name__ == "__main__":
    main()