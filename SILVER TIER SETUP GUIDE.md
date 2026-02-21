# Silver Tier Setup Guide

## Overview

This guide provides step-by-step instructions to set up the Silver Tier implementation of your Personal AI Employee. The Silver Tier builds upon the Bronze Tier foundation with enhanced automation, monitoring, and business generation capabilities.

## Prerequisites

### Software Requirements
- Python 3.13 or higher
- Node.js v24+ LTS
- Claude Code (active subscription)
- Obsidian v1.10.6+ (free)
- Git (for cloning repositories)

### Hardware Requirements
- Minimum: 8GB RAM, 4-core CPU, 20GB free disk space
- Recommended: 16GB RAM, 8-core CPU, SSD storage
- Stable internet connection (10+ Mbps recommended)

### Skill Level
- Comfortable with command-line interfaces (terminal/bash)
- Understanding of file systems and folder structures
- Familiarity with APIs
- Experience with Claude Code
- Basic understanding of OAuth and API authentication

## Installation Steps

### 1. Clone or Download the Repository
```bash
git clone <repository-url>
# Or download and extract the zip file
cd Hackathon-0
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt

# For Gmail integration, install additional dependencies:
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# For web scraping (LinkedIn), install:
pip install beautifulsoup4 requests
```

### 3. Set Up the Obsidian Vault
The system will use the existing vault structure from Bronze Tier, but ensure the following folders exist:

```bash
mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,Done,Plans,Pending_Approval,Logs,Archive,Schedules,Tasks,Templates/Email}
```

## Configuration

### 1. Configure Gmail Watcher
To use the Gmail watcher, you need to set up Google API credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials JSON file
6. Save it as `credentials.json` in your project directory

### 2. Configure Email MCP Server
1. Run the email MCP server once to create the default configuration:
   ```bash
   python mcp_servers/email_mcp.py ./AI_Employee_Vault --test
   ```

2. Edit the generated `AI_Employee_Vault/email_config.json` file with your email settings:
   ```json
   {
     "smtp_server": "smtp.gmail.com",
     "smtp_port": 587,
     "sender_email": "your_email@gmail.com",
     "sender_password": "your_app_password",
     "use_tls": true
   }
   ```

**Note**: For Gmail, use an "App Password" instead of your regular password.

### 3. Verify Folder Structure
Ensure the complete folder structure exists:
```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Inbox/
├── Needs_Action/
├── Done/
├── Plans/
├── Pending_Approval/
├── Logs/
├── Archive/
├── Schedules/
├── Tasks/
└── Templates/
    └── Email/
```

## Running the System

### 1. Initialize the System
```bash
# Run the complete Silver Tier system
python ai_employee_coordinator.py ./AI_Employee_Vault silver
```

### 2. Set Up Scheduling
Register the automated tasks:
```bash
# This will create scheduled tasks for LinkedIn posting, Gmail checking, and daily reports
python scheduler.py ./AI_Employee_Vault
```

### 3. Start Individual Components
You can run individual components as needed:

#### Watchers
```bash
# File system watcher
python filesystem_watcher.py ./watch_folder ./AI_Employee_Vault

# Gmail watcher (requires credentials)
python gmail_watcher.py ./AI_Employee_Vault ./credentials.json

# LinkedIn watcher
python linkedin_watcher.py ./AI_Employee_Vault
```

#### Action Components
```bash
# LinkedIn poster (generates posts for approval)
python linkedin_poster.py ./AI_Employee_Vault
```

#### Skills
```bash
# Run individual skills
python skills/file_processor_skill.py ./AI_Employee_Vault
python skills/task_manager_skill.py ./AI_Employee_Vault
python skills/notification_skill.py ./AI_Employee_Vault
python skills/plan_generator_skill.py ./AI_Employee_Vault
```

## Configuring the LinkedIn Poster

The LinkedIn poster creates business posts automatically but requires human approval:

1. Posts are generated based on templates in the code
2. Approval requests are created in the `Pending_Approval` folder
3. Move approval files to the `Approved` folder to publish posts
4. Completed posts are moved to the `Done` folder

## Using the Plan Generator

The plan generator creates structured plans for complex tasks:

1. Place complex tasks in the `Needs_Action` folder
2. The system will detect tasks requiring planning
3. Plan.md files will be created in the `Plans` folder
4. Review and modify plans as needed
5. Move completed plans to the `Done` folder

## Managing Scheduled Tasks

### List Scheduled Tasks
```bash
python scheduler.py ./AI_Employee_Vault --list
```

### Run a Scheduled Task Immediately
```bash
python scheduler.py ./AI_Employee_Vault --run <task_name>
```

### Remove a Scheduled Task
```bash
python scheduler.py ./AI_Employee_Vault --remove <task_name>
```

## Testing the System

### 1. Test Watchers
1. Place a file in the monitored folder for the file system watcher
2. Verify a Gmail with "important" label exists for Gmail watcher testing
3. Check the `Needs_Action` folder for created action items

### 2. Test LinkedIn Posting
1. Run the LinkedIn poster
2. Check the `Plans` folder for post plans
3. Check the `Pending_Approval` folder for approval requests

### 3. Test Plan Generation
1. Create a complex task in the `Needs_Action` folder
2. Run the plan generator skill
3. Check the `Plans` folder for generated plans

### 4. Test MCP Server
1. Configure email settings
2. Test sending a simple email through the MCP server

## Monitoring and Maintenance

### Dashboard Updates
- Check `Dashboard.md` for system status and activity
- Recent activities are automatically updated
- System status reflects current operational state

### Log Files
- System logs are stored in the `Logs` folder
- Monitor logs for errors or unusual activity
- Email MCP logs are in `email_mcp_log_YYYY-MM-DD.json`

### Approval Workflows
- Monitor `Pending_Approval` folder for required actions
- Move files to `Approved` folder to authorize actions
- Move files to `Rejected` folder to deny actions

## Troubleshooting

### Common Issues

#### Gmail Authentication Errors
- Ensure credentials.json is properly formatted
- Verify that the Gmail API is enabled in Google Cloud Console
- Check that the account has proper permissions

#### LinkedIn Watcher Not Working
- LinkedIn has strict anti-bot measures
- The current implementation is a framework
- For production use, consider using the LinkedIn API or a more sophisticated approach

#### Email MCP Server Not Sending Emails
- Verify email configuration in `email_config.json`
- Check that your email provider supports SMTP
- For Gmail, ensure you're using an App Password

#### Scheduler Registration Failures
- On Windows, running as administrator may be required
- On Unix systems, ensure cron is running
- Check that the script paths are correct

#### File Permissions Issues
- Ensure Claude Code has read/write access to the vault
- Check that all directories have proper permissions
- On Windows, ensure no applications are locking files

### System Status Checks
- Check the Dashboard.md for current system status
- Review the Needs_Action folder for pending items
- Verify the Done folder for completed tasks
- Monitor the Logs folder for system events

## Security Considerations

### Credential Management
- Store email credentials separately in email_config.json
- Never commit credential files to version control
- Use environment variables for sensitive information
- Rotate credentials regularly

### Data Privacy
- The system keeps all data local in the Obsidian vault
- No external data transmission occurs without explicit configuration
- Maintain encryption for sensitive data as needed

### Human-in-the-Loop
- Critical actions require human approval
- The system creates approval files in Pending_Approval folder
- Only move files to Approved folder after human review

### API Limits
- Be aware of rate limits for external services (Gmail, LinkedIn)
- Implement appropriate delays to avoid being blocked
- Monitor for API quota usage

## Performance Optimization

### Resource Management
- Monitor system resources during operation
- Adjust scheduling intervals based on system capacity
- Consider running intensive tasks during off-peak hours

### Storage Management
- Regularly archive old files to prevent vault bloat
- Implement log rotation for maintenance
- Clean up completed tasks periodically

## Verification Checklist

Before declaring Silver Tier setup complete, verify:

- [ ] All Bronze Tier functionality working
- [ ] Gmail watcher configured and running (if using)
- [ ] LinkedIn watcher operational (framework in place)
- [ ] LinkedIn poster generating posts and approval requests
- [ ] Plan generator creating Plan.md files
- [ ] Email MCP server configured with valid credentials
- [ ] Scheduler registered all required tasks
- [ ] All skills operational and integrated
- [ ] Dashboard updating with Silver Tier activities
- [ ] Approval workflow functioning properly
- [ ] All files created in proper locations
- [ ] System running without errors

## Support

For issues with the Silver Tier setup:
1. Review the troubleshooting section
2. Check the system logs in the Logs folder
3. Verify all prerequisites are met
4. Ensure proper configuration of external services (Gmail, email)
5. Consult the Silver Tier Implementation documentation

## Next Steps

After completing Silver Tier setup, you can extend to:
### Gold Tier
- Integrate with accounting systems (Odoo)
- Add comprehensive social media posting (Twitter, Facebook, Instagram)
- Implement autonomous business auditing
- Add weekly CEO briefing generation
- Enhance error recovery mechanisms

---
*Setup guide for Silver Tier implementation - Personal AI Employee Hackathon*