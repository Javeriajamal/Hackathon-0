# BRONZE TIER SETUP GUIDE

## Overview
This guide provides step-by-step instructions to set up the Bronze Tier implementation of your Personal AI Employee. This system creates a foundational AI employee with core automation capabilities as defined in the hackathon requirements.

## Prerequisites

### Software Requirements
- Python 3.13 or higher
- Node.js v24+ LTS
- Claude Code (active subscription)
- Obsidian v1.10.6+ (free)

### Hardware Requirements
- Minimum: 8GB RAM, 4-core CPU, 20GB free disk space
- Recommended: 16GB RAM, 8-core CPU, SSD storage
- Stable internet connection (10+ Mbps recommended)

### Skill Level
- Comfortable with command-line interfaces (terminal/bash)
- Understanding of file systems and folder structures
- Familiarity with APIs
- Experience with Claude Code

## Installation Steps

### 1. Clone or Download the Repository
```bash
git clone <repository-url>
# Or download and extract the zip file
```

### 2. Install Dependencies
```bash
cd Hackathon-0
pip install -r requirements.txt
```

### 3. Create the Obsidian Vault
The system creates an Obsidian vault structure automatically, but you can also create it manually:

```bash
mkdir AI_Employee_Vault
cd AI_Employee_Vault
```

## Folder Structure Setup

The system creates the following folder structure automatically:

```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Inbox/
├── Needs_Action/
├── Done/
├── Plans/
├── Pending_Approval/
└── Logs/
```

If creating manually:
```bash
mkdir Inbox Needs_Action Done Plans Pending_Approval Logs Archive
```

## Configuration

### 1. Dashboard.md
Contains the main dashboard for monitoring system status. The system creates this automatically with:
- System status indicators
- Recent activity tracking
- Quick statistics
- Next action items

### 2. Company_Handbook.md
Contains rules of engagement and communication guidelines. This file defines:
- Core principles
- Communication guidelines
- Approval thresholds
- Response time expectations
- Working hours
- Emergency protocols
- Data handling procedures

## Running the System

### 1. Start the File System Watcher
The file system watcher monitors a designated folder for new files and creates action items.

```bash
# Terminal 1: Start the watcher
python filesystem_watcher.py <watch_folder> <vault_path>

# Example:
python filesystem_watcher.py ./watch_folder ./AI_Employee_Vault
```

### 2. Monitor the System
The watcher will:
- Monitor the specified folder for new files
- Create action items in the Needs_Action folder
- Add appropriate metadata to each action item
- Categorize files by type (document, image, audio, etc.)

### 3. Process Action Items
Claude Code will process items in the Needs_Action folder by:
- Reading the files
- Applying business logic based on Company_Handbook.md
- Creating output files in the appropriate folders
- Updating status as tasks are completed

### 4. Demonstrate the Workflow
Run the vault interaction demo to see the complete workflow:

```bash
python vault_interaction_demo.py
```

This will:
- Create a sample task in Needs_Action
- Process the task according to system rules
- Move the completed task to the Done folder
- Add processing notes to track the action

## Testing the System

### 1. Test File Monitoring
1. Place a file in the monitored folder:
   ```bash
   echo "Test file" > watch_folder/test.txt
   ```
2. Observe the creation of an action file in Needs_Action
3. Check the Inbox folder for the copied file

### 2. Test Manual Task Processing
1. Create a manual task in Needs_Action folder
2. Run the vault interaction demo to process it
3. Verify it appears in the Done folder with processing notes

### 3. Test Inbox Processing
1. Place a file in the Inbox folder
2. Create an appropriate action file in Needs_Action
3. Process according to Company Handbook guidelines
4. Move completed tasks to Done folder

## Troubleshooting

### Common Issues

#### File Watcher Not Starting
- Ensure the watch folder exists before starting the watcher
- Check that you have read/write permissions to both the watch folder and vault
- Verify Python dependencies are installed

#### Files Not Being Processed
- Check that the vault folder structure is correctly created
- Verify Claude Code has access to read and write files in the vault
- Confirm the Company_Handbook.md file exists and is readable

#### Dashboard Not Updating
- Ensure you're updating the Dashboard.md file after processing tasks
- Check file permissions for the Dashboard.md file
- Verify the proper format is maintained in the markdown file

### System Status Checks
- Check the Dashboard.md for current system status
- Review the Needs_Action folder for pending items
- Verify the Done folder for completed tasks
- Monitor the Logs folder for system events

## Security Considerations

### Credential Management
- Store credentials separately in environment variables
- Never commit sensitive information to version control
- Use secure credential management tools for production deployment

### Data Privacy
- The system keeps all data local in the Obsidian vault
- No external data transmission occurs in the basic implementation
- Maintain encryption for sensitive data as needed

### Human-in-the-Loop
- Critical actions require human approval
- The system creates approval files in Pending_Approval folder
- Only move files to Approved folder after human review

## Verification Checklist

Before declaring Bronze Tier complete, verify:

- [x] Obsidian vault created with Dashboard.md and Company_Handbook.md
- [x] File system watcher running and creating action items
- [x] Claude Code can read from and write to the vault
- [x] Folder structure exists: Inbox, Needs_Action, Done, Plans, Pending_Approval, Logs
- [x] Agent Skills implemented: File Processing, Task Management, and Notification skills
- [x] Main coordinator module integrating all skills
- [x] Sample tasks processed successfully
- [x] Dashboard updated with recent activities
- [x] All files created in proper locations

## Next Steps

After completing Bronze Tier, you can extend to:

### Silver Tier
- Add Gmail and WhatsApp watchers
- Implement MCP servers for external actions
- Create Plan.md files for complex tasks
- Add scheduling capabilities

### Gold Tier
- Integrate with accounting systems
- Add social media posting capabilities
- Implement autonomous business auditing
- Enhance error recovery mechanisms

## Support

For issues with the Bronze Tier setup:
1. Review the troubleshooting section
2. Check the system logs in the Logs folder
3. Verify all prerequisites are met
4. Consult the hackathon documentation

---
*Setup guide for Bronze Tier implementation - Personal AI Employee Hackathon*