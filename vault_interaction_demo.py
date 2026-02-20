"""
Test script to demonstrate Claude Code reading from and writing to the vault.

This script simulates how Claude Code would interact with the Obsidian vault
by reading files from the Needs_Action folder and writing processed files
to the Done folder.
"""

import os
import time
from pathlib import Path
from datetime import datetime
import shutil


def process_needs_action_files(vault_path):
    """Process files in the Needs_Action folder."""
    vault_path = Path(vault_path)
    needs_action_dir = vault_path / 'Needs_Action'
    done_dir = vault_path / 'Done'

    # Create directories if they don't exist
    needs_action_dir.mkdir(parents=True, exist_ok=True)
    done_dir.mkdir(parents=True, exist_ok=True)

    # Get all markdown files in Needs_Action
    action_files = list(needs_action_dir.glob("*.md"))

    if not action_files:
        print("No files to process in Needs_Action folder.")
        return

    print(f"Found {len(action_files)} files to process:")

    for file_path in action_files:
        print(f"Processing: {file_path.name}")

        # Read the file content
        content = file_path.read_text(encoding='utf-8')
        print(f"Content preview: {content[:200]}...")

        # Process the content (in a real scenario, this would involve Claude reasoning)
        processed_content = add_processing_note(content)

        # Write the processed content to a new file in the Done folder
        done_file_path = done_dir / f"DONE_{file_path.name}"
        done_file_path.write_text(processed_content, encoding='utf-8')

        # Move the original file to archive (simulate completion)
        archive_dir = vault_path / 'Archive'
        archive_dir.mkdir(exist_ok=True)
        archived_file_path = archive_dir / f"ARCHIVED_{file_path.name}"
        shutil.move(str(file_path), str(archived_file_path))

        print(f"Processed and moved {file_path.name} to Done")


def add_processing_note(content):
    """Add a processing note to the content."""
    footer = f"""

## Processing Notes
- **Processed by**: Claude Code Simulation
- **Processed at**: {datetime.now().isoformat()}
- **Status**: Completed
- **Next step**: File moved to Done folder

---
*Automatically processed by AI Employee*
"""
    return content + footer


def simulate_new_task(vault_path):
    """Simulate adding a new task to Needs_Action folder."""
    vault_path = Path(vault_path)
    needs_action_dir = vault_path / 'Needs_Action'

    # Create a sample task file
    task_content = f"""---
type: sample_task
priority: medium
assigned_to: ai_employee
status: pending
created: {datetime.now().isoformat()}
---

# Sample Task for Processing

This is a sample task to demonstrate how Claude Code reads from and writes to the vault.

## Objective
Process this sample task and move it to the Done folder.

## Instructions
1. Read this file from the Needs_Action folder
2. Process the content
3. Write a processed version to the Done folder
4. Update the status to completed

## Expected Outcome
This task should be completed and moved to the Done folder by the AI Employee.

---
Created as a test for Bronze Tier requirement fulfillment
"""

    task_file_path = needs_action_dir / f"sample_task_{int(datetime.now().timestamp())}.md"
    task_file_path.write_text(task_content)
    print(f"Created sample task: {task_file_path.name}")


def main():
    """Main function to demonstrate vault interaction."""
    vault_path = "./AI_Employee_Vault"

    print("Demonstrating Claude Code reading from and writing to the vault...")
    print(f"Vault path: {vault_path}")

    # Simulate adding a new task
    simulate_new_task(vault_path)

    # Wait a moment to simulate processing time
    time.sleep(1)

    # Process the files
    process_needs_action_files(vault_path)

    print("\nDemonstration complete!")
    print("Files have been processed from Needs_Action to Done folder.")


if __name__ == "__main__":
    main()