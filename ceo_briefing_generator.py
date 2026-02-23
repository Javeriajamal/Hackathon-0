"""
CEO Briefing Generator for AI Employee

Generates weekly business and accounting audits with CEO briefings
based on data from various sources including Odoo accounting system.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
import os
import calendar


class CEObriefingGenerator:
    """Generates weekly CEO briefings with business and accounting audits."""

    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.briefings_dir = self.vault_path / 'Briefings'
        self.accounting_dir = self.vault_path / 'Accounting'
        self.logs_dir = self.vault_path / 'Logs'
        self.company_handbook_path = self.vault_path / 'Company_Handbook.md'

        # Create directories if they don't exist
        self.briefings_dir.mkdir(parents=True, exist_ok=True)
        self.accounting_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        # Load company goals if available
        self.business_goals_path = self.vault_path / 'Business_Goals.md'
        self.business_goals = self._load_business_goals()

    def _load_business_goals(self):
        """Load business goals from Business_Goals.md if it exists."""
        if self.business_goals_path.exists():
            try:
                content = self.business_goals_path.read_text(encoding='utf-8')
                # This would parse the Business_Goals.md file
                # For now, returning a basic structure
                return {
                    "revenue_target": 10000,
                    "current_mtd": 4500,
                    "metrics": {
                        "response_time": {"target": "<24", "threshold": ">48"},
                        "payment_rate": {"target": ">90%", "threshold": "<80%"},
                        "software_costs": {"target": "<$500", "threshold": ">$600"}
                    }
                }
            except Exception as e:
                print(f"Error loading business goals: {e}")
                return {}
        return {}

    def _load_company_handbook(self):
        """Load company handbook for reference."""
        if self.company_handbook_path.exists():
            try:
                content = self.company_handbook_path.read_text(encoding='utf-8')
                return content
            except Exception as e:
                print(f"Error loading company handbook: {e}")
                return ""
        return ""

    def get_odoo_data(self):
        """Simulate getting data from Odoo system."""
        # In a real implementation, this would connect to the Odoo MCP
        # For now, we'll simulate the data
        return {
            "revenue": 2450,
            "expenses": 850,
            "profit": 1600,
            "unpaid_invoices": 3,
            "total_unpaid_amount": 1250,
            "new_customers": 2,
            "active_projects": [
                {"name": "Project Alpha", "due_date": "Jan 15", "budget": 2000},
                {"name": "Project Beta", "due_date": "Jan 30", "budget": 3500}
            ]
        }

    def get_transaction_data(self):
        """Get transaction data for the audit."""
        # In a real implementation, this would come from accounting system
        # For now, we'll simulate the data
        return [
            {"description": "Client A Payment", "amount": 1200, "date": "2026-02-20", "type": "revenue"},
            {"description": "Software Subscription", "amount": -50, "date": "2026-02-19", "type": "expense"},
            {"description": "Client B Payment", "amount": 1250, "date": "2026-02-18", "type": "revenue"},
        ]

    def analyze_transactions(self, transactions):
        """Analyze transactions to identify patterns."""
        # Analyze transactions to identify subscription patterns, etc.
        subscriptions = []
        for transaction in transactions:
            desc_lower = transaction['description'].lower()
            if any(pattern in desc_lower for pattern in ['netflix', 'spotify', 'adobe', 'notion', 'slack']):
                subscriptions.append(transaction)

        return {
            "subscriptions": subscriptions,
            "monthly_recurring": sum(s['amount'] for s in subscriptions if s['amount'] < 0),
            "potential_optimization": [s for s in subscriptions if s['amount'] < 0 and abs(s['amount']) > 20]
        }

    def identify_bottlenecks(self):
        """Identify potential business bottlenecks."""
        # In a real implementation, this would analyze task completion times
        # For now, we'll simulate some potential bottlenecks
        return [
            {
                "task": "Client B proposal",
                "expected_duration": "2 days",
                "actual_duration": "5 days",
                "delay": "+3 days"
            }
        ]

    def generate_subscription_audit(self, analysis_results):
        """Generate subscription audit based on transaction analysis."""
        suggestions = []
        for sub in analysis_results['potential_optimization']:
            suggestions.append({
                "name": sub['description'],
                "cost": abs(sub['amount']),
                "action": "Consider cancellation?",
                "folder": "/Pending_Approval"
            })
        return suggestions

    def generate_ceo_briefing(self, period_start=None, period_end=None):
        """Generate the CEO briefing for the specified period."""
        if not period_start:
            # Default to last week
            last_monday = datetime.now() - timedelta(days=datetime.now().weekday() + 7)
            period_start = last_monday.date()
        if not period_end:
            # End on the Sunday of the previous week
            last_sunday = datetime.now() - timedelta(days=datetime.now().weekday() + 1)
            period_end = last_sunday.date()

        # Get data for the briefing
        odoo_data = self.get_odoo_data()
        transactions = self.get_transaction_data()
        transaction_analysis = self.analyze_transactions(transactions)
        bottlenecks = self.identify_bottlenecks()
        subscription_audit = self.generate_subscription_audit(transaction_analysis)

        # Calculate period info
        period_str = f"{period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}"

        # Generate the briefing content
        briefing_content = f"""---
generated: {datetime.now().isoformat()}
period: {period_str}
---

# Monday Morning CEO Briefing

## Executive Summary
Strong week with revenue ahead of target. One bottleneck identified.

## Revenue
- **This Week**: ${odoo_data['revenue']:,}
- **MTD**: ${self.business_goals.get('current_mtd', 4500):,} (45% of ${self.business_goals.get('revenue_target', 10000):,} target)
- **Trend**: On track

## Expenses
- **This Week**: ${abs(odoo_data['expenses']):,}
- **Net Profit**: ${odoo_data['profit']:,}

## Completed Tasks
- [x] Client A invoice sent and paid
- [x] Project Alpha milestone 2 delivered
- [x] Weekly social media posts scheduled

## Active Projects
{chr(10).join([f"- {project['name']} - Due {project['due_date']} - Budget ${project['budget']:,}" for project in odoo_data['active_projects']])}

## Outstanding Items
- **Unpaid Invoices**: {odoo_data['unpaid_invoices']} totaling ${odoo_data['total_unpaid_amount']:,}
- **New Customers This Period**: {odoo_data['new_customers']}

## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
{chr(10).join([f"| {b['task']} | {b['expected_duration']} | {b['actual_duration']} | {b['delay']} |" for b in bottlenecks]) if bottlenecks else "| No bottlenecks identified | - | - | - |"}

## Transaction Analysis
- **Total Transactions**: {len(transactions)}
- **Revenue Transactions**: {len([t for t in transactions if t['type'] == 'revenue'])}
- **Expense Transactions**: {len([t for t in transactions if t['type'] == 'expense'])}

## Subscription Audit
- **Monthly Recurring Costs**: ${transaction_analysis['monthly_recurring']:.2f}
- **Potential Optimizations**: {len(subscription_audit)}

### Cost Optimization
{chr(10).join([f"- **{s['name']}**: Cost: ${s['cost']:.2f}. {s['action']} Move to {s['folder']}." for s in subscription_audit]) if subscription_audit else "- No cost optimization opportunities identified."}

## Upcoming Deadlines
{chr(10).join([f"- {project['name']} final delivery: {project['due_date']} ({(datetime.strptime(project['due_date'], '%b %d').replace(year=datetime.now().year) - datetime.now()).days + 1} days)" for project in odoo_data['active_projects']])}

## Recommendations
- Follow up on {odoo_data['unpaid_invoices']} unpaid invoices totaling ${odoo_data['total_unpaid_amount']:,}
- Investigate delay in Client B proposal
- Review subscription costs for optimization opportunities

---
*Generated by AI Employee v1.0 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Create the briefing file
        briefing_filename = f"{period_end.strftime('%Y-%m-%d')}_Monday_Briefing.md"
        briefing_path = self.briefings_dir / briefing_filename
        briefing_path.write_text(briefing_content)

        print(f"Generated CEO briefing: {briefing_path}")

        return str(briefing_path)

    def generate_weekly_audit(self):
        """Generate the weekly business audit."""
        # This would normally coordinate with other systems to get comprehensive data
        # For now, we'll call the CEO briefing generator which includes audit information
        return self.generate_ceo_briefing()

    def create_accounting_reports(self, period_start=None, period_end=None):
        """Create accounting reports for the period."""
        if not period_start:
            last_monday = datetime.now() - timedelta(days=datetime.now().weekday() + 7)
            period_start = last_monday.date()
        if not period_end:
            last_sunday = datetime.now() - timedelta(days=datetime.now().weekday() + 1)
            period_end = last_sunday.date()

        # Generate a basic P&L statement
        odoo_data = self.get_odoo_data()

        pl_statement = f"""---
period: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}
generated: {datetime.now().isoformat()}
---

# Profit & Loss Statement
## Period: {period_start.strftime('%B %d, %Y')} to {period_end.strftime('%B %d, %Y')}

### Revenue
- Total Revenue: ${odoo_data['revenue']:,}

### Expenses
- Total Expenses: ${abs(odoo_data['expenses']):,}

### Net Income
- Net Income: ${odoo_data['profit']:,}

### Key Metrics
- Revenue Growth (YoY): TBD
- Expense Ratio: {abs(odoo_data['expenses'])/odoo_data['revenue']*100:.2f}%
- Net Profit Margin: {odoo_data['profit']/odoo_data['revenue']*100:.2f}%

---
*Generated by AI Employee Accounting System*
"""

        pl_filename = f"PnL_{period_end.strftime('%Y-%m-%d')}.md"
        pl_path = self.accounting_dir / pl_filename
        pl_path.write_text(pl_statement)

        print(f"Generated P&L statement: {pl_path}")

        return str(pl_path)

    def run_complete_audit_cycle(self):
        """Run the complete weekly audit cycle."""
        print("Running complete weekly audit cycle...")

        # Generate CEO briefing
        briefing_path = self.generate_weekly_audit()
        print(f"CEO Briefing generated: {briefing_path}")

        # Generate accounting reports
        report_path = self.create_accounting_reports()
        print(f"Accounting report generated: {report_path}")

        # Log the audit completion
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "weekly_audit",
            "result": "completed",
            "briefing_file": briefing_path,
            "report_file": report_path
        }

        log_file = self.logs_dir / f"audit_log_{datetime.now().strftime('%Y-%m')}.json"
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
                if isinstance(logs, dict):
                    logs = [logs]
            except json.JSONDecodeError:
                logs = []

        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

        print("Weekly audit cycle completed successfully.")
        return {
            "briefing": briefing_path,
            "report": report_path,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Main function to demonstrate the CEO Briefing Generator."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ceo_briefing_generator.py <vault_path> [--test]")
        print("Example: python ceo_briefing_generator.py ./AI_Employee_Vault --test")
        return

    vault_path = sys.argv[1]
    generator = CEObriefingGenerator(vault_path)

    if "--test" in sys.argv:
        print("Testing CEO Briefing Generator...")

        # Run a complete audit cycle
        result = generator.run_complete_audit_cycle()
        print(f"Audit cycle result: {result}")

        print("CEO Briefing Generator test completed.")
    else:
        print("CEO Briefing Generator initialized.")
        print("Ready to generate weekly business and accounting audits.")


if __name__ == "__main__":
    main()