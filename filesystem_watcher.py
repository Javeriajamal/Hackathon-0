"""
File System Watcher for AI Employee

Monitors a designated folder for new files and creates action items
in the Needs_Action folder when new files are detected.
"""

import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import os
import sys


class DropFolderHandler(FileSystemEventHandler):
    """Handles file creation events in the monitored folder."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        # Create directories if they don't exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        source = Path(event.src_path)
        print(f"New file detected: {source.name}")

        # Copy file to inbox
        dest = self.inbox / source.name
        try:
            shutil.copy2(source, dest)
            print(f"Copied file to inbox: {dest}")
        except Exception as e:
            print(f"Error copying file: {e}")
            return

        # Create metadata file in Needs_Action
        self.create_metadata_file(source, dest)

    def create_metadata_file(self, source: Path, dest: Path):
        """Create a metadata file in Needs_Action folder."""
        timestamp = datetime.now().isoformat()

        # Determine file type based on extension
        extension = source.suffix.lower()
        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            file_type = 'image'
        elif extension in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
            file_type = 'document'
        elif extension in ['.csv', '.xlsx', '.xls']:
            file_type = 'spreadsheet'
        elif extension in ['.mp3', '.wav', '.flac']:
            file_type = 'audio'
        elif extension in ['.mp4', '.avi', '.mov']:
            file_type = 'video'
        else:
            file_type = 'other'

        # Create metadata content
        metadata_content = f"""---
type: file_drop
original_name: {source.name}
destination_path: {str(dest)}
size: {source.stat().st_size}
file_type: {file_type}
detected_at: {timestamp}
status: pending
priority: medium
---

# New File Received

A new file has been detected in the monitored folder.

## File Details
- **Name**: {source.name}
- **Size**: {source.stat().st_size} bytes
- **Type**: {file_type}
- **Detected**: {timestamp}

## Suggested Actions
- [ ] Review file content
- [ ] Determine appropriate response
- [ ] Process according to company handbook
- [ ] Move processed file to Done folder

## File Path
{str(dest)}

---
File processed by File System Watcher
"""

        # Create the action file
        action_filename = f"FILE_DROP_{source.stem}_{int(datetime.now().timestamp())}.md"
        action_file_path = self.needs_action / action_filename
        action_file_path.write_text(metadata_content)

        print(f"Created action file: {action_file_path}")


def main():
    """Main function to start the file system watcher."""
    if len(sys.argv) != 3:
        print("Usage: python filesystem_watcher.py <watch_folder> <vault_path>")
        print("Example: python filesystem_watcher.py ./watch_folder ./AI_Employee_Vault")
        return

    watch_folder = Path(sys.argv[1])
    vault_path = Path(sys.argv[2])

    # Validate paths
    if not watch_folder.exists():
        print(f"Watch folder does not exist: {watch_folder}")
        return

    if not vault_path.exists():
        print(f"Vault path does not exist: {vault_path}")
        return

    # Create handler and observer
    event_handler = DropFolderHandler(vault_path)
    observer = Observer()
    observer.schedule(event_handler, str(watch_folder), recursive=False)

    print(f"Starting file system watcher...")
    print(f"Monitoring: {watch_folder}")
    print(f"Vault path: {vault_path}")
    print("Press Ctrl+C to stop.")

    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping file system watcher...")

    observer.join()
    print("File system watcher stopped.")


if __name__ == "__main__":
    main()