# Agent Skills Configuration for AI Employee

This document outlines how AI functionality should be implemented as Agent Skills for the AI Employee project.

## Required Agent Skills for Bronze Tier

### 1. File Processing Skill
- **Purpose**: Process files in the vault
- **Function**: Read from Needs_Action, process, write to Done
- **Trigger**: New files appear in Needs_Action folder

### 2. Task Management Skill
- **Purpose**: Manage tasks in the system
- **Function**: Update status, move files between folders, create action items
- **Trigger**: Task completion or new task creation

### 3. Notification Skill
- **Purpose**: Notify user of important events
- **Function**: Create alert files, update dashboard
- **Trigger**: High priority events or completion of tasks

## Example Agent Skill Implementation

```python
# Example: File Processing Agent Skill
class FileProcessingSkill:
    def __init__(self, vault_path):
        self.vault_path = vault_path

    def process_needs_action_items(self):
        """Process all items in Needs_Action folder"""
        needs_action_dir = Path(self.vault_path) / 'Needs_Action'
        for file_path in needs_action_dir.glob("*.md"):
            # Process the file
            self.process_single_file(file_path)

    def process_single_file(self, file_path):
        """Process a single file from Needs_Action"""
        # Read the file
        content = file_path.read_text()

        # Apply processing logic based on file type
        processed_content = self.apply_logic(content)

        # Move to appropriate folder
        self.move_to_done(file_path, processed_content)

    def move_to_done(self, original_file, processed_content):
        """Move processed file to Done folder"""
        done_dir = Path(self.vault_path) / 'Done'
        new_file_path = done_dir / f"DONE_{original_file.name}"
        new_file_path.write_text(processed_content)

        # Remove original file
        original_file.unlink()
```

## Skill Registration

Skills should be registered in the Claude Code configuration to be available for use:

```json
{
  "skills": [
    {
      "name": "file_processor",
      "description": "Processes files in the vault system",
      "module": "skills.file_processor",
      "class": "FileProcessingSkill"
    },
    {
      "name": "task_manager",
      "description": "Manages tasks in the system",
      "module": "skills.task_manager",
      "class": "TaskManagementSkill"
    }
  ]
}
```

## Bronze Tier Compliance

This implementation satisfies the Bronze Tier requirement that "All AI functionality should be implemented as Agent Skills" by providing a framework for modular, reusable skills that can be invoked by Claude Code.