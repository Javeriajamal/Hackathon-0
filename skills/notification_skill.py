"""
Notification Skill for AI Employee

This skill handles notifications and alerts for important events,
updating the dashboard and creating alert files when needed.
"""

import os
from pathlib import Path
from datetime import datetime


class NotificationSkill:
    """Skill to handle notifications and alerts in the AI Employee system."""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.dashboard_path = self.vault_path / 'Dashboard.md'
        self.alerts_dir = self.vault_path / 'Alerts'
        self.logs_dir = self.vault_path / 'Logs'

        # Ensure directories exist
        self.alerts_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        # Create dashboard if it doesn't exist
        if not self.dashboard_path.exists():
            self._create_default_dashboard()

    def _create_default_dashboard(self):
        """Create a default dashboard if one doesn't exist."""
        default_content = f"""# AI Employee Dashboard

Welcome to your Personal AI Employee Dashboard. This serves as the central hub for monitoring your automated assistant's activities.

## Current Status
- **System Status**: Operational
- **Last Check**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Active Watchers**: 0
- **Pending Actions**: 0
- **Tasks Completed Today**: 0

## Recent Activity
- [ ] No recent activity recorded

## Alerts
- [ ] No alerts at this time

## Quick Stats
- Inbox Items: 0
- Pending Actions: 0
- Completed Tasks: 0

## Next Actions
- [ ] Configure watchers
- [ ] Set up initial tasks
- [ ] Define company handbook rules

---
*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        self.dashboard_path.write_text(default_content)

    def send_notification(self, message, priority="normal", category="info"):
        """Send a notification by updating the dashboard and creating log entry."""
        print(f"[{priority.upper()}] {category.title()}: {message}")

        # Add to dashboard
        self._update_dashboard_with_notification(message, priority, category)

        # Create log entry
        self._create_log_entry(message, priority, category)

        # Create alert if high priority
        if priority.lower() in ['high', 'critical', 'urgent']:
            self._create_alert_file(message, priority, category)

    def _update_dashboard_with_notification(self, message, priority, category):
        """Update the dashboard with the notification."""
        if self.dashboard_path.exists():
            content = self.dashboard_path.read_text(encoding='utf-8')

            # Find the Recent Activity section
            lines = content.split('\n')
            updated_lines = []
            activity_section_found = False

            for line in lines:
                if line.startswith('## Recent Activity'):
                    activity_section_found = True
                    updated_lines.append(line)
                    updated_lines.append(f'- [x] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [{priority.upper()}] {category.title()}: {message}')
                elif activity_section_found and line.startswith('- [ ] No recent activity recorded'):
                    # Replace the placeholder
                    updated_lines.append(f'- [x] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [{priority.upper()}] {category.title()}: {message}')
                    activity_section_found = False  # Reset flag so we don't add multiple entries
                elif activity_section_found and line.startswith('## ') and not line.startswith('## Recent Activity'):
                    # End of activity section, add our entry before this header
                    updated_lines.append(f'- [x] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [{priority.upper()}] {category.title()}: {message}')
                    updated_lines.append('')
                    updated_lines.append(line)
                    activity_section_found = False
                else:
                    updated_lines.append(line)

            # If we never found the activity section, append to the end
            if activity_section_found and all(not line.startswith('## ') or line.startswith('## Recent Activity') for line in updated_lines[-5:]):
                updated_lines.append(f'- [x] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - [{priority.upper()}] {category.title()}: {message}')

            # Update stats section if needed
            updated_content = '\n'.join(updated_lines)
            updated_content = self._update_stats_in_dashboard(updated_content, priority)

            self.dashboard_path.write_text(updated_content, encoding='utf-8')

    def _update_stats_in_dashboard(self, content, priority):
        """Update the stats in the dashboard."""
        lines = content.split('\n')
        updated_lines = []

        for line in lines:
            if line.startswith('- Tasks Completed Today:'):
                # Increment the task counter
                parts = line.split(': ')
                if len(parts) > 1:
                    try:
                        current_count = int(parts[1])
                        line = f'- Tasks Completed Today: {current_count + 1}'
                    except ValueError:
                        pass
            elif line.startswith('- Pending Actions:'):
                # For now, just keep the same value, but in a real system this would be dynamic
                pass
            elif line.startswith('- Inbox Items:'):
                # For now, just keep the same value, but in a real system this would be dynamic
                pass
            updated_lines.append(line)

        return '\n'.join(updated_lines)

    def _create_log_entry(self, message, priority, category):
        """Create a log entry for the notification."""
        log_filename = f"log_{datetime.now().strftime('%Y-%m-%d')}.json"
        log_path = self.logs_dir / log_filename

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "priority": priority,
            "category": category,
            "source": "NotificationSkill"
        }

        # Append to existing log or create new one
        import json
        log_entries = []
        if log_path.exists():
            try:
                content = log_path.read_text(encoding='utf-8')
                if content.strip():
                    log_entries = json.loads(content) if content.strip() != "" else []
                    if isinstance(log_entries, dict):  # If single object, wrap in list
                        log_entries = [log_entries]
            except json.JSONDecodeError:
                log_entries = []

        log_entries.append(log_entry)

        log_path.write_text(json.dumps(log_entries, indent=2), encoding='utf-8')

    def _create_alert_file(self, message, priority, category):
        """Create an alert file for high priority notifications."""
        alert_filename = f"ALERT_{category}_{int(datetime.now().timestamp())}.md"
        alert_path = self.alerts_dir / alert_filename

        alert_content = f"""---
priority: {priority}
category: {category}
created: {datetime.now().isoformat()}
status: active
---

# ALERT: {category.title()}

## Message
{message}

## Details
- **Priority**: {priority}
- **Category**: {category}
- **Timestamp**: {datetime.now().isoformat()}

## Action Required
Review this alert and take appropriate action.

---
Alert generated by Notification Skill
"""

        alert_path.write_text(alert_content, encoding='utf-8')

    def update_system_status(self, status, active_watchers=None, pending_actions=None, tasks_completed=None):
        """Update the system status on the dashboard."""
        if self.dashboard_path.exists():
            content = self.dashboard_path.read_text(encoding='utf-8')

            lines = content.split('\n')
            updated_lines = []

            for line in lines:
                if line.startswith('- **System Status**:'):
                    updated_lines.append(f'- **System Status**: {status}')
                elif line.startswith('- **Active Watchers**:') and active_watchers is not None:
                    updated_lines.append(f'- **Active Watchers**: {active_watchers}')
                elif line.startswith('- **Pending Actions**:') and pending_actions is not None:
                    updated_lines.append(f'- **Pending Actions**: {pending_actions}')
                elif line.startswith('- **Tasks Completed Today**:') and tasks_completed is not None:
                    updated_lines.append(f'- **Tasks Completed Today**: {tasks_completed}')
                elif line.startswith('*Last updated:') or line.startswith('- **Last Check**:'):
                    # Update the timestamp
                    if line.startswith('- **Last Check**:'):
                        updated_lines.append(f'- **Last Check**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)

            self.dashboard_path.write_text('\n'.join(updated_lines), encoding='utf-8')

    def get_status(self):
        """Get current status of the skill."""
        alerts_count = len(list(self.alerts_dir.glob("*.md")))
        logs_count = len(list(self.logs_dir.glob("*.json")))

        return {
            'alerts_generated': alerts_count,
            'logs_created': logs_count,
            'dashboard_exists': self.dashboard_path.exists(),
            'last_update': datetime.now().isoformat()
        }


def main():
    """Main function to demonstrate the skill."""
    import sys

    if len(sys.argv) != 2:
        print("Usage: python notification_skill.py <vault_path>")
        return

    vault_path = sys.argv[1]
    skill = NotificationSkill(vault_path)

    # Send a test notification
    skill.send_notification(
        "System initialized successfully",
        priority="normal",
        category="system"
    )

    # Update system status
    skill.update_system_status(
        status="Operational",
        active_watchers=1,
        pending_actions=0,
        tasks_completed=2
    )

    status = skill.get_status()
    print(f"Status: {status}")


if __name__ == "__main__":
    main()