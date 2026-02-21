@echo off
cd C:\Users\Ahamed Jamal\OneDrive\Documents\GitHub\Hackathon-0
echo Running scheduled task: daily_report >> AI_Employee_Vault\Logs/scheduler_log_2026-02-21.log
python C:\Users\Ahamed Jamal\OneDrive\Documents\GitHub\Hackathon-0/ai_employee_coordinator.py AI_Employee_Vault
echo Task daily_report completed at %date% %time% >> AI_Employee_Vault\Logs/scheduler_log_2026-02-21.log
