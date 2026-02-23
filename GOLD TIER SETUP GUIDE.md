# Gold Tier Setup Guide

## Overview

This guide provides step-by-step instructions to set up the Gold Tier implementation of your Personal AI Employee. The Gold Tier adds advanced business intelligence, accounting integration, social media management, error recovery, and autonomous operation capabilities.

## Prerequisites

### Software Requirements
- Python 3.13 or higher
- Node.js v24+ LTS
- Claude Code (active subscription)
- Obsidian v1.10.6+ (free)
- Git (for cloning repositories)
- Odoo Community Edition 19+ (for accounting integration)

### Hardware Requirements
- Recommended: 16GB RAM, 8-core CPU, SSD storage
- Stable internet connection (10+ Mbps recommended)

### Skill Level
- Advanced understanding of APIs and authentication
- Experience with database systems
- Familiarity with social media platform APIs
- Basic system administration skills

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

# For Odoo integration:
pip install requests

# For social media integration:
pip install requests

# For additional processing:
pip install beautifulsoup4
```

### 3. Set Up the Obsidian Vault
Ensure the complete folder structure exists:

```bash
mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,Done,Plans,Pending_Approval,Logs,Archive,Schedules,Tasks,Templates/Email,Briefings,Accounting,Errors,Backups,Temp}
```

## Configuration

### 1. Configure Odoo Integration
To use the Odoo accounting system:

1. Install Odoo Community Edition 19+ locally or access a hosted instance
2. Create a database and user account
3. Set environment variables:

```bash
export ODOO_URL=http://localhost:8069
export ODOO_USERNAME=your_username
export ODOO_PASSWORD=your_password
export ODOO_DATABASE=your_database_name
```

### 2. Configure Social Media Integration
For social media posting capabilities, set up API access:

#### Facebook/Instagram Configuration:
1. Create a Facebook Developer account
2. Create an app in the Facebook Developer Portal
3. Set up a Facebook Page and Instagram Business Account
4. Get the necessary access tokens and account IDs
5. Set environment variables:

```bash
export FACEBOOK_ACCESS_TOKEN=your_access_token
export FACEBOOK_PAGE_ID=your_page_id
export INSTAGRAM_ACCESS_TOKEN=your_instagram_token
export INSTAGRAM_ACCOUNT_ID=your_instagram_account_id
```

#### Twitter/X Configuration:
1. Apply for a Twitter Developer account
2. Create a new app in the Twitter Developer Portal
3. Get API keys and tokens
4. Set environment variables:

```bash
export TWITTER_BEARER_TOKEN=your_bearer_token
export TWITTER_ACCESS_TOKEN=your_access_token
export TWITTER_ACCESS_SECRET=your_access_secret
export TWITTER_USERNAME=your_username
```

### 3. Verify Folder Structure
Ensure the complete Gold Tier folder structure exists:
```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── Inbox/
├── Needs_Action/
├── Done/
├── Plans/
├── Pending_Approval/
├── Logs/
├── Archive/
├── Schedules/
├── Tasks/
├── Templates/Email/
├── Briefings/
├── Accounting/
├── Errors/
├── Backups/
└── Temp/
```

## Running the System

### 1. Initialize the System
```bash
# Run the complete Gold Tier system
python ai_employee_coordinator.py ./AI_Employee_Vault gold
```

### 2. Run Individual Gold Tier Components
```bash
# Run CEO briefing generator
python ceo_briefing_generator.py ./AI_Employee_Vault

# Run Ralph Wiggum loop for autonomous tasks
python ralph_wiggum_loop.py ./AI_Employee_Vault

# Run error recovery system
python error_recovery_system.py ./AI_Employee_Vault

# Run Odoo MCP server
python mcp_servers/odoo_mcp.py ./AI_Employee_Vault

# Run social media MCP server
python mcp_servers/social_media_mcp.py ./AI_Employee_Vault
```

### 3. Set Up Automated Audits
The system will automatically generate weekly CEO briefings. To manually trigger:

```bash
# Generate weekly audit and briefing
python ceo_briefing_generator.py ./AI_Employee_Vault
```

## Configuring Gold Tier Features

### 1. Business Goals Configuration
Update `Business_Goals.md` with your specific business targets:

```markdown
# Business Goals

## Revenue Target
- Monthly goal: $10,000
- Current MTD: $4,500

## Key Metrics to Track
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Client response time | < 24 hours | > 48 hours |
| Invoice payment rate | > 90% | < 80% |
| Software costs | < $500/month | > $600/month |
```

### 2. MCP Server Configuration
Each MCP server has its own configuration requirements:

#### Email MCP
Configure `AI_Employee_Vault/email_config.json` with SMTP settings

#### Odoo MCP
Set environment variables as described above

#### Social Media MCP
Set environment variables as described above

### 3. Scheduling Gold Tier Tasks
Register Gold Tier automated tasks:

```bash
# The scheduler will automatically include Gold Tier tasks
python scheduler.py ./AI_Employee_Vault
```

## Testing the System

### 1. Test Odoo Integration
```bash
python mcp_servers/odoo_mcp.py ./AI_Employee_Vault --test
```

### 2. Test Social Media Integration
```bash
python mcp_servers/social_media_mcp.py ./AI_Employee_Vault --test
```

### 3. Test CEO Briefing Generation
```bash
python ceo_briefing_generator.py ./AI_Employee_Vault --test
```

### 4. Test Ralph Wiggum Loop
```bash
python ralph_wiggum_loop.py ./AI_Employee_Vault --demo
```

### 5. Test Error Recovery
```bash
python error_recovery_system.py ./AI_Employee_Vault --test
```

## Monitoring and Maintenance

### 1. CEO Briefings
- Check `Briefings/` folder for weekly CEO briefings
- Review financial summaries and recommendations
- Follow up on identified bottlenecks

### 2. Accounting Reports
- Check `Accounting/` folder for financial statements
- Review P&L statements and transaction analysis
- Monitor subscription costs and optimization opportunities

### 3. Error Monitoring
- Monitor `Errors/` folder for critical error files
- Check `Logs/` for daily operation logs
- Review `Backups/` for system state backups

### 4. Social Media Activity
- Monitor social media accounts for posted content
- Review engagement metrics
- Check for approval requests in `Pending_Approval/`

## Troubleshooting

### Common Issues

#### Odoo Connection Errors
- Verify Odoo server is running
- Check network connectivity to Odoo server
- Confirm database name and credentials are correct
- Ensure appropriate modules are installed in Odoo

#### Social Media API Errors
- Verify access tokens are still valid
- Check API rate limits
- Confirm page/account IDs are correct
- Review app permissions in developer portals

#### Error Recovery System Activation
- Check for `SAFE_MODE_ACTIVE.md` file
- Review error logs in `Logs/` folder
- Address issues before resuming normal operations
- Remove safe mode file to resume operations

#### Ralph Wiggum Loop Not Completing Tasks
- Check task progress in `Tasks/` and `In_Progress/` folders
- Verify max iteration settings
- Review task definitions for completeness

### System Status Checks
- Check Dashboard.md for overall system status
- Monitor Briefings/ folder for weekly reports
- Review Logs/ for system events
- Check Errors/ for critical issues

## Security Considerations

### Credential Management
- Store all API keys and tokens securely
- Never commit credentials to version control
- Rotate tokens regularly
- Use environment variables or secure vaults

### Data Privacy
- The system keeps sensitive business data local
- Social media content is posted externally but controlled locally
- Maintain audit logs for compliance

### Access Control
- Limit access to the vault directory
- Secure Odoo instance with proper authentication
- Protect social media account credentials

## Performance Optimization

### Resource Management
- Monitor system resources during operation
- Adjust audit frequency based on system capacity
- Consider running intensive tasks during off-peak hours

### Data Management
- Regularly archive old briefings and reports
- Implement log rotation for maintenance
- Clean up completed tasks periodically

## Verification Checklist

Before declaring Gold Tier setup complete, verify:

- [ ] All Silver Tier functionality working
- [ ] Odoo MCP server configured and tested
- [ ] Social media MCP server configured and tested
- [ ] CEO Briefing Generator operational
- [ ] Ralph Wiggum Loop functioning
- [ ] Error Recovery System operational
- [ ] Weekly audit reports generating
- [ ] All MCP servers registered
- [ ] Business Goals configured
- [ ] All environment variables set
- [ ] All files created in proper locations
- [ ] System running without errors

## Support

For issues with the Gold Tier setup:
1. Review the troubleshooting section
2. Check the system logs in the Logs folder
3. Verify all prerequisites are met
4. Ensure proper configuration of external services (Odoo, social media)
5. Consult the Gold Tier Implementation documentation

## Next Steps

After completing Gold Tier setup, you can extend to:
### Platinum Tier
- Deploy to cloud with 24/7 operation
- Work-zone specialization (cloud/local)
- Advanced synchronization mechanisms
- Production-ready monitoring

---
*Setup guide for Gold Tier implementation - Personal AI Employee Hackathon*