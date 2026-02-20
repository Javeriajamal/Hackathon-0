"""
File Processing Skill for AI Employee

This skill handles processing of files in the vault system.
It reads from Needs_Action, processes content, and moves files to appropriate folders.
"""

import os
from pathlib import Path
from datetime import datetime
import shutil


class FileProcessingSkill:
    """Skill to process files in the vault system."""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.needs_action_dir = self.vault_path / 'Needs_Action'
        self.done_dir = self.vault_path / 'Done'
        self.archive_dir = self.vault_path / 'Archive'

        # Ensure directories exist
        self.needs_action_dir.mkdir(exist_ok=True)
        self.done_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)

    def process_needs_action_items(self):
        """Process all items in the Needs_Action folder."""
        action_files = list(self.needs_action_dir.glob("*.md"))

        if not action_files:
            print("No files to process in Needs_Action folder.")
            return []

        processed_files = []
        for file_path in action_files:
            result = self.process_single_file(file_path)
            if result:
                processed_files.append(result)

        return processed_files

    def process_single_file(self, file_path):
        """Process a single file from Needs_Action."""
        try:
            # Read the file content
            content = file_path.read_text(encoding='utf-8')

            # Add processing notes to the content
            processed_content = self.add_processing_notes(content)

            # Create processed file in Done folder
            done_file_path = self.done_dir / f"DONE_{file_path.name}"
            done_file_path.write_text(processed_content, encoding='utf-8')

            # Archive the original file
            archived_file_path = self.archive_dir / f"ARCHIVED_{file_path.name}"
            shutil.move(str(file_path), str(archived_file_path))

            print(f"Processed file: {file_path.name}")
            return {
                'original': str(file_path),
                'done': str(done_file_path),
                'archived': str(archived_file_path),
                'status': 'completed'
            }
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return None

    def add_processing_notes(self, content):
        """Add processing notes to file content."""
        processing_notes = f"""

## Processing Notes
- **Processed by**: File Processing Skill
- **Processed at**: {datetime.now().isoformat()}
- **Status**: Completed
- **Next step**: File moved to Done folder

---
*Automatically processed by AI Employee*
"""
        return content + processing_notes

    def get_status(self):
        """Get current status of the skill."""
        needs_action_count = len(list(self.needs_action_dir.glob("*.md")))
        done_count = len(list(self.done_dir.glob("*.md")))
        archive_count = len(list(self.archive_dir.glob("*.md")))

        return {
            'needs_action_pending': needs_action_count,
            'files_processed': done_count,
            'files_archived': archive_count,
            'last_update': datetime.now().isoformat()
        }


def main():
    """Main function to demonstrate the skill."""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python file_processor_skill.py <vault_path>")
        return

    vault_path = sys.argv[1]
    skill = FileProcessingSkill(vault_path)

    print("Processing Needs_Action items...")
    results = skill.process_needs_action_items()

    print(f"Processed {len(results)} files.")

    status = skill.get_status()
    print(f"Status: {status}")


if __name__ == "__main__":
    main()