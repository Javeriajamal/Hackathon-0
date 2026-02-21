# Personal AI Employee - Complete Hackathon Implementation

This project implements the Personal AI Employee Hackathon requirements, progressing through multiple tiers from Bronze to Silver. The AI Employee is a local-first, agent-driven system that proactively manages personal and business affairs 24/7.

## Project Structure

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

## Bronze Tier Implementation

### Requirements Fulfilled

1. ✅ **Obsidian vault with Dashboard.md and Company_Handbook.md**
   - Created `AI_Employee_Vault` directory
   - Created `Dashboard.md` with system status and activity tracking
   - Created `Company_Handbook.md` with rules of engagement

2. ✅ **One working Watcher script (File system monitoring)**
   - Created `filesystem_watcher.py` that monitors a folder for new files
   - Creates action items in `Needs_Action` folder when new files are detected
   - Handles different file types with appropriate metadata

3. ✅ **Claude Code successfully reading from and writing to the vault**
   - Created demonstration script `vault_interaction_demo.py`
   - Shows how Claude would process files from `Needs_Action` to `Done`
   - Includes sample task creation and processing

4. ✅ **Basic folder structure: /Inbox, /Needs_Action, /Done**
   - Created all required folders: `Inbox`, `Needs_Action`, `Done`, `Plans`, `Pending_Approval`, `Logs`, `Archive`
   - Folders are properly structured for the AI Employee workflow

5. ✅ **All AI functionality should be implemented as Agent Skills**
   - Created actual executable agent skill modules:
     - `skills/file_processor_skill.py`: File processing operations
     - `skills/task_manager_skill.py`: Task management operations
     - `skills/notification_skill.py`: Notification and dashboard updates
   - Created `ai_employee_coordinator.py`: Main coordinator module integrating all skills
   - Created `Agent_Skills_Documentation.md` with comprehensive documentation

## Silver Tier Implementation

### Requirements Fulfilled

1. ✅ **All Bronze Tier requirements** (inherited from Bronze Tier)
2. ✅ **Two or more Watcher scripts** (Gmail + LinkedIn + File system monitoring)
   - Created `gmail_watcher.py` that monitors Gmail for important emails
   - Created `linkedin_watcher.py` that monitors LinkedIn for business opportunities
   - Enhanced `filesystem_watcher.py` from Bronze Tier
3. ✅ **Automatically Post on LinkedIn about business to generate sales**
   - Created `linkedin_poster.py` that automatically generates and posts business updates
   - Implements human-in-the-loop approval workflow
   - Uses templates for consistent messaging
4. ✅ **Claude reasoning loop that creates Plan.md files**
   - Created `skills/plan_generator_skill.py` that generates structured Plan.md files
   - Processes Needs_Action items to identify tasks requiring planning
   - Integrates with Company Handbook guidelines
5. ✅ **One working MCP server for external action**
   - Created `mcp_servers/email_mcp.py` for sending emails
   - Secure credential handling and attachment support
   - Logging and tracking of email activities
6. ✅ **Human-in-the-loop approval workflow for sensitive actions**
   - Enhanced approval system in all components
   - Pending_Approval folder for sensitive actions
   - Explicit approval workflow for LinkedIn posts
7. ✅ **Basic scheduling via cron or Task Scheduler**
   - Created `scheduler.py` with cross-platform scheduling
   - Automatically registers LinkedIn posting, Gmail checking, and daily reports
8. ✅ **All AI functionality should be implemented as Agent Skills**
   - Extended agent skills framework with planning capabilities
   - Integrated all new functionality into the skills architecture

## Skills Structure
```
skills/
├── file_processor_skill.py
├── task_manager_skill.py
├── notification_skill.py
├── plan_generator_skill.py
└── __init__.py
```

## MCP Servers Structure
```
mcp_servers/
└── email_mcp.py
```

## How to Run the Implementation

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# For Gmail integration, install additional dependencies:
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# For web scraping (LinkedIn), install:
pip install beautifulsoup4 requests
```

### 2. Run the Complete AI Employee System
```bash
# Run the complete Silver Tier coordinated system
python ai_employee_coordinator.py ./AI_Employee_Vault silver

# Run Bronze Tier workflow (backward compatibility)
python ai_employee_coordinator.py ./AI_Employee_Vault bronze
```

### 3. Run Individual Components
```bash
# Run file system watcher
python filesystem_watcher.py ./test_drop_folder ./AI_Employee_Vault

# Run Gmail watcher
python gmail_watcher.py ./AI_Employee_Vault ./credentials.json

# Run LinkedIn watcher
python linkedin_watcher.py ./AI_Employee_Vault

# Run LinkedIn poster
python linkedin_poster.py ./AI_Employee_Vault

# Run individual skills
python skills/file_processor_skill.py ./AI_Employee_Vault
python skills/task_manager_skill.py ./AI_Employee_Vault
python skills/notification_skill.py ./AI_Employee_Vault
python skills/plan_generator_skill.py ./AI_Employee_Vault

# Run the vault interaction demo
python vault_interaction_demo.py

# Run the scheduler
python scheduler.py ./AI_Employee_Vault
```

### 4. Configure MCP Servers
```bash
# Set up email MCP server (creates default config file)
python mcp_servers/email_mcp.py ./AI_Employee_Vault --test
# Then edit email_config.json with your credentials
```

## Features

### Bronze Tier Features
- **File Monitoring**: The filesystem watcher monitors a specified folder for new files
- **Automatic Action Creation**: When files are detected, action items are created in the Needs_Action folder
- **Vault Integration**: Claude Code can read from and write to the vault structure
- **Actual Agent Skills**: Fully implemented executable skills modules, not just documentation
- **Coordinated Operation**: Main coordinator module integrates all skills for unified operation
- **Dashboard Updates**: Automatic updates to Dashboard.md with system status and activity
- **Security Conscious**: Designed with privacy and security considerations

### Silver Tier Features
- **Enhanced Monitoring**: Three watcher scripts (File system, Gmail, LinkedIn)
- **Business Generation**: Automatic LinkedIn posting to generate sales
- **Planning System**: Claude reasoning that creates structured Plan.md files
- **External Actions**: MCP server for email and other external actions
- **Human-in-the-Loop**: Approval workflow for sensitive actions
- **Scheduling**: Cross-platform task scheduling system
- **Advanced Coordination**: Silver Tier workflow integrating all components

## Next Steps for Higher Tiers

- **Gold Tier**: Add accounting integration, social media posting, autonomous workflows
- **Platinum Tier**: Deploy to cloud with 24/7 operation

## Security Notes

- Credentials should be stored separately in environment variables
- The vault structure keeps sensitive data local
- Human-in-the-loop approval system for sensitive actions
- MCP servers follow security best practices
- All data remains local in the Obsidian vault