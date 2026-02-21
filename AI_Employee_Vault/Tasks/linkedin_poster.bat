@echo off
cd C:\Users\Ahamed Jamal\OneDrive\Documents\GitHub\Hackathon-0
echo Running scheduled task: linkedin_poster >> AI_Employee_Vault\Logs/scheduler_log_2026-02-21.log
python C:\Users\Ahamed Jamal\OneDrive\Documents\GitHub\Hackathon-0/linkedin_poster.py AI_Employee_Vault --test
echo Task linkedin_poster completed at %date% %time% >> AI_Employee_Vault\Logs/scheduler_log_2026-02-21.log
