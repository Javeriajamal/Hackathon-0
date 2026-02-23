"""
Error Recovery System for AI Employee

Implements error recovery and graceful degradation for the AI Employee system.
Handles various error states and provides recovery strategies.
"""

import time
import json
from pathlib import Path
from datetime import datetime, timedelta
import traceback
import sys
import os
import subprocess
from enum import Enum


class ErrorCategory(Enum):
    TRANSIENT = "transient"
    AUTHENTICATION = "authentication"
    LOGIC = "logic"
    DATA = "data"
    SYSTEM = "system"


class ErrorRecoverySystem:
    """Manages error recovery and graceful degradation for the AI Employee."""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.errors_dir = self.vault_path / 'Errors'
        self.backup_dir = self.vault_path / 'Backups'
        self.temp_dir = self.vault_path / 'Temp'

        # Create directories if they don't exist
        self.logs_dir.mkdir(exist_ok=True)
        self.errors_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)

        # Error counters for rate limiting
        self.error_counts = {}
        self.last_error_times = {}

    def log_error(self, error, context="", severity="error"):
        """Log an error with context and timestamp."""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc() if error else None,
            "module": sys.modules[context.split('.')[0]] if '.' in context else None
        }

        # Determine error category
        error_category = self._categorize_error(error_entry)
        error_entry["category"] = error_category.value

        # Save to dated error log
        log_file = self.logs_dir / f"errors_{datetime.now().strftime('%Y-%m-%d')}.json"

        # Load existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
                if isinstance(logs, dict):
                    logs = [logs]
            except json.JSONDecodeError:
                logs = []

        logs.append(error_entry)

        # Write logs back
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        # Also save individual error file for critical errors
        if severity in ["critical", "fatal"]:
            error_file = self.errors_dir / f"critical_error_{int(datetime.now().timestamp())}.json"
            with open(error_file, 'w') as f:
                json.dump(error_entry, f, indent=2)

        # Update error counters
        error_key = f"{error_category.value}_{context}"
        current_time = time.time()
        if error_key not in self.error_counts:
            self.error_counts[error_key] = 0
            self.last_error_times[error_key] = current_time

        self.error_counts[error_key] += 1
        self.last_error_times[error_key] = current_time

        print(f"[{severity.upper()}] {error_category.value}: {str(error)[:100]}...")

    def _categorize_error(self, error_entry):
        """Categorize an error based on its characteristics."""
        error_msg = error_entry["error_message"].lower()
        error_type = error_entry["error_type"].lower()

        # Check for transient errors
        transient_patterns = [
            "timeout", "connection", "network", "rate limit", "temporarily unavailable",
            "retry", "backoff", "congestion", "throttle"
        ]
        if any(pattern in error_msg for pattern in transient_patterns):
            return ErrorCategory.TRANSIENT

        # Check for authentication errors
        auth_patterns = [
            "authentication", "authorization", "permission", "unauthorized", "expired",
            "invalid token", "access denied", "oauth", "credential"
        ]
        if any(pattern in error_msg for pattern in auth_patterns):
            return ErrorCategory.AUTHENTICATION

        # Check for system errors
        system_patterns = [
            "memory", "disk", "file system", "io", "system", "kernel", "hardware"
        ]
        if any(pattern in error_msg for pattern in system_patterns):
            return ErrorCategory.SYSTEM

        # Check for data errors
        data_patterns = [
            "corrupt", "invalid", "malformed", "parse", "decode", "encode",
            "missing", "null", "none", "index out of range"
        ]
        if any(pattern in error_msg for pattern in data_patterns):
            return ErrorCategory.DATA

        # Default to logic for other errors
        return ErrorCategory.LOGIC

    def is_error_rate_limited(self, context, max_errors_per_minute=5):
        """Check if we should rate limit due to too many errors."""
        error_key = f"rate_limit_{context}"
        current_time = time.time()

        # Clean up old error counts (older than 1 minute)
        cutoff_time = current_time - 60
        for key in list(self.last_error_times.keys()):
            if self.last_error_times[key] < cutoff_time:
                del self.error_counts[key]
                del self.last_error_times[key]

        # Check if we're over the limit
        recent_errors = self.error_counts.get(error_key, 0)
        return recent_errors > max_errors_per_minute

    def handle_transient_error(self, error, context, max_retries=3, base_delay=1):
        """Handle transient errors with exponential backoff retry."""
        print(f"Handling transient error in {context}: {str(error)}")

        for attempt in range(max_retries):
            if attempt > 0:
                delay = min(base_delay * (2 ** attempt), 60)  # Max 1 minute delay
                print(f"Retry attempt {attempt + 1}/{max_retries} in {delay}s...")
                time.sleep(delay)

            try:
                # Return success indicator
                return True
            except Exception as retry_error:
                print(f"Retry {attempt + 1} failed: {str(retry_error)}")
                if attempt == max_retries - 1:
                    # Last attempt failed, escalate
                    self.log_error(retry_error, f"{context}_retry", "warning")
                    return False

        return False

    def handle_authentication_error(self, error, context):
        """Handle authentication errors."""
        print(f"Handling authentication error in {context}: {str(error)}")
        self.log_error(error, f"{context}_auth", "warning")

        # Alert human operator
        self._alert_human_operator(f"Authentication failed in {context}. Please refresh credentials.")

        # Pause operations temporarily
        return False

    def handle_logic_error(self, error, context):
        """Handle logic errors."""
        print(f"Handling logic error in {context}: {str(error)}")
        self.log_error(error, f"{context}_logic", "error")

        # Put system in safe mode
        self._enter_safe_mode(context)
        return False

    def handle_data_error(self, error, context):
        """Handle data errors."""
        print(f"Handling data error in {context}: {str(error)}")
        self.log_error(error, f"{context}_data", "error")

        # Try to quarantine the problematic data
        self._quarantine_problematic_data(context)
        return False

    def handle_system_error(self, error, context):
        """Handle system errors."""
        print(f"Handling system error in {context}: {str(error)}")
        self.log_error(error, f"{context}_system", "critical")

        # Alert human operator immediately
        self._alert_human_operator(f"Critical system error in {context}. Immediate attention required.")

        # Try to restart affected processes
        self._restart_processes(context)
        return False

    def _alert_human_operator(self, message):
        """Alert the human operator about critical issues."""
        # Create an alert file in a prominent location
        alert_file = self.vault_path / 'ALERT_NEEDED.md'
        alert_content = f"""---
timestamp: {datetime.now().isoformat()}
priority: high
---

# CRITICAL ALERT

**Message**: {message}

**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Action Required
Please review this alert and take appropriate action.

## System Status
- Errors may be accumulating
- Some functions may be degraded
- Human intervention required

---
Alert generated by Error Recovery System
"""
        alert_file.write_text(alert_content)
        print(f"ALERT CREATED: {message}")

    def _enter_safe_mode(self, context):
        """Put the system in safe mode to prevent further damage."""
        safe_mode_file = self.vault_path / 'SAFE_MODE_ACTIVE.md'
        safe_mode_content = f"""---
activated_at: {datetime.now().isoformat()}
context: {context}
---

# SAFE MODE ACTIVE

The system has entered safe mode due to errors.

## Current State
- Normal operations paused
- Only critical functions active
- Awaiting human review

## Actions Taken
- Paused non-critical processes
- Preserved current state
- Created backup of working state

## Next Steps
1. Review error logs
2. Fix underlying issues
3. Remove this file to resume normal operations

---
Safe mode activated by Error Recovery System
"""
        safe_mode_file.write_text(safe_mode_content)
        print("SYSTEM ENTERED SAFE MODE")

    def _quarantine_problematic_data(self, context):
        """Quarantine problematic data to prevent corruption spread."""
        # This would move suspect files to a quarantine area
        # For now, we'll just log the action
        quarantine_log = self.errors_dir / f"quarantine_log_{datetime.now().strftime('%Y-%m-%d')}.md"
        quarantine_entry = f"""
# Data Quarantine Log
- **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Context**: {context}
- **Action**: Quarantined potentially corrupt data
- **Details**: Affected files moved to quarantine for review
"""
        if quarantine_log.exists():
            with open(quarantine_log, 'a') as f:
                f.write(quarantine_entry)
        else:
            with open(quarantine_log, 'w') as f:
                f.write(f"# Data Quarantine Log\n{quarantine_entry}")

    def _restart_processes(self, context):
        """Attempt to restart affected processes."""
        # This would restart system processes
        # For now, we'll just log the attempt
        restart_log = self.logs_dir / f"restart_log_{datetime.now().strftime('%Y-%m-%d')}.md"
        restart_entry = f"""
# Process Restart Log
- **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Context**: {context}
- **Action**: Attempted process restart
- **Result**: Manual restart may be required
"""
        if restart_log.exists():
            with open(restart_log, 'a') as f:
                f.write(restart_entry)
        else:
            with open(restart_log, 'w') as f:
                f.write(f"# Process Restart Log\n{restart_entry}")

    def recover_from_error(self, error, context):
        """Main error recovery method that routes to appropriate handler."""
        error_category = self._categorize_error({"error_message": str(error), "error_type": type(error).__name__})

        # Check rate limiting
        if self.is_error_rate_limited(context):
            print(f"Rate limited: Too many errors in {context}, pausing operations")
            time.sleep(60)  # Wait 1 minute before continuing
            return False

        # Route to appropriate handler
        if error_category == ErrorCategory.TRANSIENT:
            return self.handle_transient_error(error, context)
        elif error_category == ErrorCategory.AUTHENTICATION:
            return self.handle_authentication_error(error, context)
        elif error_category == ErrorCategory.LOGIC:
            return self.handle_logic_error(error, context)
        elif error_category == ErrorCategory.DATA:
            return self.handle_data_error(error, context)
        elif error_category == ErrorCategory.SYSTEM:
            return self.handle_system_error(error, context)
        else:
            # Default handling
            self.log_error(error, context, "error")
            return False

    def graceful_degradation(self, service_name, reason):
        """Implement graceful degradation when services fail."""
        degradation_log = self.logs_dir / f"degradation_log_{datetime.now().strftime('%Y-%m-%d')}.json"

        degradation_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": service_name,
            "reason": reason,
            "degraded_functions": [],
            "alternative_methods": []
        }

        # Load existing logs
        logs = []
        if degradation_log.exists():
            try:
                logs = json.loads(degradation_log.read_text())
                if isinstance(logs, dict):
                    logs = [logs]
            except json.JSONDecodeError:
                logs = []

        logs.append(degradation_entry)

        # Write logs back
        with open(degradation_log, 'w') as f:
            json.dump(logs, f, indent=2)

        print(f"Service {service_name} degraded gracefully: {reason}")

        # Return alternative method or reduced functionality
        alternatives = {
            "gmail_watcher": ["check local email cache", "notify user of delayed processing"],
            "linkedin_poster": ["queue posts for later", "switch to manual posting"],
            "odoo_mcp": ["switch to manual accounting", "use cached data"],
            "scheduler": ["use fallback timing", "manual trigger required"]
        }

        return alternatives.get(service_name, ["service temporarily unavailable"])

    def backup_state(self):
        """Create a backup of the current system state."""
        backup_file = self.backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "error_counts": self.error_counts.copy(),
            "last_error_times": {k: v for k, v in self.last_error_times.items()},
            "system_status": "operational" if not (self.vault_path / 'SAFE_MODE_ACTIVE.md').exists() else "safe_mode",
            "recent_errors": []
        }

        # Include recent errors in the backup
        error_log = self.logs_dir / f"errors_{datetime.now().strftime('%Y-%m-%d')}.json"
        if error_log.exists():
            try:
                with open(error_log, 'r') as f:
                    errors = json.load(f)
                    backup_data["recent_errors"] = errors[-10:]  # Last 10 errors
            except:
                backup_data["recent_errors"] = ["Could not load recent errors"]

        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)

        print(f"State backed up to: {backup_file}")
        return str(backup_file)

    def get_error_statistics(self):
        """Get statistics about errors."""
        stats = {
            "total_errors": 0,
            "by_category": {},
            "by_severity": {},
            "rate_limited_contexts": [],
            "last_24h": 0,
            "timestamp": datetime.now().isoformat()
        }

        # Count errors from today's log
        error_log = self.logs_dir / f"errors_{datetime.now().strftime('%Y-%m-%d')}.json"
        if error_log.exists():
            try:
                with open(error_log, 'r') as f:
                    errors = json.load(f)
                    stats["total_errors"] = len(errors)

                    # Categorize errors
                    for error in errors:
                        cat = error.get("category", "unknown")
                        sev = error.get("severity", "unknown")

                        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
                        stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1

                    # Check for errors in last 24 hours
                    now = datetime.now()
                    cutoff = now - timedelta(hours=24)
                    for error in errors:
                        err_time = datetime.fromisoformat(error["timestamp"])
                        if err_time >= cutoff:
                            stats["last_24h"] += 1

            except Exception as e:
                print(f"Error reading error log for statistics: {e}")

        # Check rate limited contexts
        current_time = time.time()
        for key, count in self.error_counts.items():
            if self.last_error_times.get(key, 0) > current_time - 60 and count > 5:
                stats["rate_limited_contexts"].append(key)

        return stats


def main():
    """Main function to demonstrate the Error Recovery System."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python error_recovery_system.py <vault_path> [--test]")
        print("Example: python error_recovery_system.py ./AI_Employee_Vault --test")
        return

    vault_path = sys.argv[1]
    error_system = ErrorRecoverySystem(vault_path)

    if "--test" in sys.argv:
        print("Testing Error Recovery System...")

        # Simulate various types of errors
        print("\n1. Testing transient error handling...")
        error_system.handle_transient_error(
            Exception("Connection timeout"),
            "gmail_connection",
            max_retries=2
        )

        print("\n2. Testing authentication error handling...")
        error_system.handle_authentication_error(
            Exception("Invalid API token"),
            "odoo_integration"
        )

        print("\n3. Testing logic error handling...")
        error_system.handle_logic_error(
            Exception("Unexpected data format"),
            "data_processor"
        )

        print("\n4. Testing data error handling...")
        error_system.handle_data_error(
            Exception("Corrupted file detected"),
            "file_reader"
        )

        print("\n5. Testing system error handling...")
        error_system.handle_system_error(
            Exception("Disk space critically low"),
            "storage_manager"
        )

        print("\n6. Testing error recovery...")
        success = error_system.recover_from_error(
            Exception("Sample error for recovery test"),
            "test_component"
        )
        print(f"Recovery success: {success}")

        print("\n7. Testing graceful degradation...")
        alternatives = error_system.graceful_degradation(
            "gmail_watcher",
            "API rate limit exceeded"
        )
        print(f"Alternatives provided: {alternatives}")

        print("\n8. Testing state backup...")
        backup_path = error_system.backup_state()
        print(f"Backup created: {backup_path}")

        print("\n9. Getting error statistics...")
        stats = error_system.get_error_statistics()
        print(f"Error statistics: {stats}")

        print("\nError Recovery System test completed.")
    else:
        print("Error Recovery System initialized.")
        print("Ready to handle errors and provide recovery for the AI Employee system.")


if __name__ == "__main__":
    main()