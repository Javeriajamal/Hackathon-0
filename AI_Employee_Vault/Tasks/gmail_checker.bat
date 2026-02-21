@echo off
cd C:\Users\Ahamed Jamal\OneDrive\Documents\GitHub\Hackathon-0
echo Running scheduled task: gmail_checker >> AI_Employee_Vault\Logs/scheduler_log_2026-02-21.log
python C:\Users\Ahamed Jamal\OneDrive\Documents\GitHub\Hackathon-0/gmail_watcher.py AI_Employee_Vault --test
echo Task gmail_checker completed at %date% %time% >> AI_Employee_Vault\Logs/scheduler_log_2026-02-21.log
