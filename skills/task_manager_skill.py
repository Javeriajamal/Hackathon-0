"""
Task Management Skill for AI Employee

This skill handles managing tasks in the system, including updating status,
moving files between folders, and creating action items.
"""

import os
from pathlib import Path
from datetime import datetime
import shutil
import yaml


class TaskManagementSkill:
    """Skill to manage tasks in the AI Employee system."""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.needs_action_dir = self.vault_path / 'Needs_Action'
        self.done_dir = self.vault_path / 'Done'
        self.inbox_dir = self.vault_path / 'Inbox'
        self.plans_dir = self.vault_path / 'Plans'
        self.pending_approval_dir = self.vault_path / 'Pending_Approval'

        # Ensure directories exist
        self.needs_action_dir.mkdir(exist_ok=True)
        self.done_dir.mkdir(exist_ok=True)
        self.inbox_dir.mkdir(exist_ok=True)
        self.plans_dir.mkdir(exist_ok=True)
        self.pending_approval_dir.mkdir(exist_ok=True)

    def create_task_from_inbox(self, inbox_file_path, task_type="general", priority="medium"):
        """Create a task from an inbox item."""
        inbox_path = Path(inbox_file_path)

        # Read the content of the inbox file
        content = inbox_path.read_text(encoding='utf-8')

        # Create a new task file in Needs_Action
        task_filename = f"TASK_FROM_INBOX_{inbox_path.stem}_{int(datetime.now().timestamp())}.md"
        task_path = self.needs_action_dir / task_filename

        # Add YAML frontmatter and task structure
        task_content = f"""---
type: {task_type}
original_file: {inbox_path.name}
source_folder: Inbox
priority: {priority}
assigned_to: ai_employee
status: pending
created: {datetime.now().isoformat()}
---

# Inbox Item Processing Task

## Original Content
{content}

## Objective
Process the incoming item from the Inbox folder according to Company Handbook guidelines.

## Actions Required
- [ ] Read the incoming item from Inbox
- [ ] Refer to Company Handbook for guidelines
- [ ] Create appropriate response or action
- [ ] Update task status as actions are completed
- [ ] Move this completed task to Done folder

## Next Steps
Process this task according to the Company Handbook rules.

---
Created by Task Management Skill
"""

        task_path.write_text(task_content, encoding='utf-8')
        print(f"Created task from inbox item: {task_path.name}")

        # Move original file to archive or keep in inbox depending on requirements
        # For now, we'll leave it in inbox as it might need manual review

        return str(task_path)

    def update_task_status(self, task_file_path, new_status):
        """Update the status of a task."""
        task_path = Path(task_file_path)

        # Read the current content
        content = task_path.read_text(encoding='utf-8')

        # Update the status in the YAML frontmatter
        lines = content.split('\n')
        updated_lines = []
        in_frontmatter = False
        frontmatter_end_idx = -1

        for i, line in enumerate(lines):
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    in_frontmatter = False
                    frontmatter_end_idx = i
                    break

            if in_frontmatter and line.startswith('status:'):
                updated_lines.append(f'status: {new_status}')
            else:
                updated_lines.append(line)

        # Combine the updated frontmatter with the rest of the content
        new_content = '\n'.join(updated_lines) + '\n' + '\n'.join(lines[frontmatter_end_idx + 1:])

        task_path.write_text(new_content, encoding='utf-8')
        print(f"Updated task status to: {new_status}")

        return True

    def move_task_to_done(self, task_file_path):
        """Move a completed task to the Done folder."""
        task_path = Path(task_file_path)

        # Update status to completed
        self.update_task_status(task_path, 'completed')

        # Read the content and add completion notes
        content = task_path.read_text(encoding='utf-8')
        completion_notes = f"""

## Completion Notes
- **Completed by**: Task Management Skill
- **Completed at**: {datetime.now().isoformat()}
- **Status**: Task moved to Done folder

---
*Task completed by AI Employee*
"""

        updated_content = content + completion_notes

        # Move to Done folder
        done_file_path = self.done_dir / f"DONE_{task_path.name}"
        done_file_path.write_text(updated_content, encoding='utf-8')

        # Remove the original file
        task_path.unlink()

        print(f"Moved task to Done: {done_file_path.name}")
        return str(done_file_path)

    def process_inbox_items(self):
        """Process all items in the Inbox folder."""
        inbox_files = list(self.inbox_dir.glob("*"))

        if not inbox_files:
            print("No items in Inbox to process.")
            return []

        created_tasks = []
        for inbox_file in inbox_files:
            # Skip if it's not a file we want to process
            if inbox_file.is_dir():
                continue

            # Create a task for each inbox item
            task_path = self.create_task_from_inbox(inbox_file)
            created_tasks.append(task_path)

        return created_tasks

    def get_status(self):
        """Get current status of the skill."""
        needs_action_count = len(list(self.needs_action_dir.glob("*.md")))
        done_count = len(list(self.done_dir.glob("*.md")))
        inbox_count = len(list(self.inbox_dir.glob("*")))
        pending_approval_count = len(list(self.pending_approval_dir.glob("*.md")))

        return {
            'needs_action_pending': needs_action_count,
            'tasks_completed': done_count,
            'inbox_items': inbox_count,
            'pending_approval': pending_approval_count,
            'last_update': datetime.now().isoformat()
        }


def main():
    """Main function to demonstrate the skill."""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python task_manager_skill.py <vault_path>")
        return

    vault_path = sys.argv[1]
    skill = TaskManagementSkill(vault_path)

    print("Processing Inbox items...")
    created_tasks = skill.process_inbox_items()

    print(f"Created {len(created_tasks)} tasks from Inbox items.")

    status = skill.get_status()
    print(f"Status: {status}")


if __name__ == "__main__":
    main()