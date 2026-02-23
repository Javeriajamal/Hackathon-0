"""
Odoo MCP (Model Context Protocol) Server for AI Employee

This MCP server enables Claude to interact with Odoo Community Edition
for accounting and business management tasks using Odoo's JSON-RPC APIs.
"""

import json
import requests
from pathlib import Path
from datetime import datetime
import os
from urllib.parse import urljoin


class OdooMCP:
    """Odoo MCP Server implementation using JSON-RPC APIs."""

    def __init__(self, vault_path, odoo_url=None, username=None, password=None, database=None):
        self.vault_path = Path(vault_path)
        self.odoo_url = odoo_url or os.getenv('ODOO_URL', 'http://localhost:8069')
        self.username = username or os.getenv('ODOO_USERNAME')
        self.password = password or os.getenv('ODOO_PASSWORD')
        self.database = database or os.getenv('ODOO_DATABASE', 'odoo_db')
        self.uid = None

        self.logs_dir = self.vault_path / 'Logs'
        self.logs_dir.mkdir(exist_ok=True)

        # Initialize connection
        self.authenticate()

    def authenticate(self):
        """Authenticate with Odoo using JSON-RPC."""
        try:
            # Authentication endpoint
            auth_url = urljoin(self.odoo_url, '/jsonrpc')

            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "common",
                    "method": "authenticate",
                    "args": [self.database, self.username, self.password, {}]
                },
                "id": 1
            }

            response = requests.post(auth_url, json=payload)
            result = response.json()

            if 'result' in result and result['result']:
                self.uid = result['result']
                print(f"Successfully authenticated with Odoo as user ID: {self.uid}")
                return True
            else:
                print(f"Authentication failed: {result.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"Error authenticating with Odoo: {e}")
            return False

    def _make_request(self, model, method, args=None, kwargs=None):
        """Make a generic request to Odoo using JSON-RPC."""
        if not self.uid:
            if not self.authenticate():
                return {"error": "Not authenticated with Odoo"}

        try:
            url = urljoin(self.odoo_url, '/jsonrpc')

            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": method,
                    "args": [self.database, self.uid, self.password, model] + (args or [])
                },
                "id": int(datetime.now().timestamp())
            }

            # Add kwargs if provided (for methods that support them)
            if kwargs:
                # For methods like search_read that accept domain and fields
                if method == 'search_read':
                    domain = kwargs.get('domain', [])
                    fields = kwargs.get('fields', [])
                    offset = kwargs.get('offset', 0)
                    limit = kwargs.get('limit', 80)
                    order = kwargs.get('order', '')

                    payload["params"]["args"].extend([domain, fields, offset, limit, order])
                else:
                    payload["params"]["args"].append(kwargs)

            response = requests.post(url, json=payload)
            result = response.json()

            if 'result' in result:
                return result['result']
            else:
                error_msg = result.get('error', {}).get('data', {}).get('message', 'Unknown error')
                print(f"Odoo API error: {error_msg}")
                return {"error": error_msg}

        except Exception as e:
            print(f"Error making request to Odoo: {e}")
            return {"error": str(e)}

    def search_records(self, model, domain=None, fields=None, limit=80):
        """Search for records in Odoo."""
        kwargs = {
            'domain': domain or [],
            'fields': fields or [],
            'limit': limit
        }
        return self._make_request(model, 'search_read', kwargs=kwargs)

    def create_record(self, model, values):
        """Create a new record in Odoo."""
        args = [values]
        return self._make_request(model, 'create', args=args)

    def update_record(self, model, record_id, values):
        """Update an existing record in Odoo."""
        args = [record_id] if isinstance(record_id, int) else record_id
        if isinstance(args, list):
            args.append(values)
        else:
            args = [args, values]
        return self._make_request(model, 'write', args=args)

    def delete_record(self, model, record_id):
        """Delete a record in Odoo."""
        args = [record_id] if isinstance(record_id, int) else record_id
        return self._make_request(model, 'unlink', args=[args])

    def get_record(self, model, record_id, fields=None):
        """Get a specific record from Odoo."""
        domain = [['id', '=', record_id]]
        kwargs = {
            'domain': domain,
            'fields': fields or []
        }
        result = self._make_request(model, 'search_read', kwargs=kwargs)

        if isinstance(result, list) and len(result) > 0:
            return result[0]
        return None

    # Specific business methods
    def create_invoice(self, partner_id, lines, journal_id=None, date=None):
        """Create a customer invoice in Odoo."""
        invoice_vals = {
            'partner_id': partner_id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, line) for line in lines],
            'invoice_date': date or datetime.now().strftime('%Y-%m-%d'),
        }

        if journal_id:
            invoice_vals['journal_id'] = journal_id

        return self.create_record('account.move', invoice_vals)

    def create_expense(self, expense_data):
        """Create an expense in Odoo."""
        expense_vals = {
            'name': expense_data.get('name', ''),
            'employee_id': expense_data.get('employee_id'),
            'date': expense_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'total_amount': expense_data.get('amount', 0.0),
            'description': expense_data.get('description', ''),
            'state': 'draft'  # Will need approval
        }

        return self.create_record('hr.expense', expense_vals)

    def get_account_balance(self, account_id):
        """Get the balance of a specific account."""
        account = self.get_record('account.account', account_id, ['name', 'balance'])
        return account

    def get_financial_summary(self, date_from=None, date_to=None):
        """Get financial summary for a period."""
        # This would typically involve multiple queries to get income/expense summary
        # For now, returning a basic structure
        summary = {
            'date_from': date_from or (datetime.now().replace(day=1)).strftime('%Y-%m-%d'),
            'date_to': date_to or datetime.now().strftime('%Y-%m-%d'),
            'income': 0,
            'expenses': 0,
            'profit_loss': 0
        }

        # Get income accounts
        income_accounts = self.search_records(
            'account.account',
            domain=[['user_type_id.name', 'ilike', 'Income']],
            fields=['id', 'name', 'balance']
        )

        if isinstance(income_accounts, list):
            summary['income'] = sum(acc.get('balance', 0) for acc in income_accounts)

        # Get expense accounts
        expense_accounts = self.search_records(
            'account.account',
            domain=[['user_type_id.name', 'ilike', 'Expense']],
            fields=['id', 'name', 'balance']
        )

        if isinstance(expense_accounts, list):
            summary['expenses'] = abs(sum(acc.get('balance', 0) for acc in expense_accounts))

        summary['profit_loss'] = summary['income'] - summary['expenses']
        return summary

    def get_customers(self):
        """Get list of customers."""
        return self.search_records('res.partner', domain=[['customer_rank', '>', 0]])

    def get_vendors(self):
        """Get list of vendors."""
        return self.search_records('res.partner', domain=[['supplier_rank', '>', 0]])

    def get_unpaid_invoices(self):
        """Get list of unpaid invoices."""
        return self.search_records(
            'account.move',
            domain=[
                ['move_type', '=', 'out_invoice'],
                ['state', '=', 'posted'],
                ['payment_state', '!=', 'paid']
            ],
            fields=['id', 'name', 'partner_id', 'amount_total', 'invoice_date', 'payment_state']
        )

    def _save_log(self, action, result, details=None):
        """Save action log to file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result,
            "details": details or {}
        }

        log_file = self.logs_dir / f"odoo_mcp_log_{datetime.now().strftime('%Y-%m-%d')}.json"

        # Load existing logs
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
                if isinstance(logs, dict):
                    logs = [logs]
            except json.JSONDecodeError:
                logs = []

        logs.append(log_entry)

        # Write logs back
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def generate_weekly_audit(self):
        """Generate weekly business and accounting audit."""
        # Get financial summary for the week
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')

        financial_summary = self.get_financial_summary(from_date, to_date)

        # Get unpaid invoices
        unpaid_invoices = self.get_unpaid_invoices()

        # Get new customers this week
        new_customers = self.search_records(
            'res.partner',
            domain=[
                ['customer_rank', '>', 0],
                ['create_date', '>=', from_date]
            ]
        )

        # Create audit report
        audit_report = {
            'report_date': datetime.now().isoformat(),
            'period_start': from_date,
            'period_end': to_date,
            'financial_summary': financial_summary,
            'unpaid_invoices_count': len(unpaid_invoices) if isinstance(unpaid_invoices, list) else 0,
            'new_customers_count': len(new_customers) if isinstance(new_customers, list) else 0,
            'total_unpaid_amount': sum(inv.get('amount_total', 0) for inv in unpaid_invoices if isinstance(unpaid_invoices, list)),
            'top_customers': [],  # Could be calculated based on recent activity
            'recommendations': [
                'Follow up on unpaid invoices',
                'Consider offering early payment discounts',
                'Review pricing for profitability'
            ]
        }

        return audit_report


def main():
    """Main function to demonstrate the Odoo MCP."""
    import sys
    from datetime import timedelta

    if len(sys.argv) < 2:
        print("Usage: python odoo_mcp.py <vault_path> [--test]")
        print("Example: python odoo_mcp.py ./AI_Employee_Vault --test")
        print("\nEnvironment variables needed:")
        print("  ODOO_URL=http://localhost:8069")
        print("  ODOO_USERNAME=admin")
        print("  ODOO_PASSWORD=yourpassword")
        print("  ODOO_DATABASE=odoo_db")
        return

    vault_path = sys.argv[1]
    odoo_mcp = OdooMCP(vault_path)

    if "--test" in sys.argv:
        print("Testing Odoo MCP Server...")

        # Test basic connectivity
        customers = odoo_mcp.get_customers()
        print(f"Retrieved {len(customers) if isinstance(customers, list) else 0} customers")

        # Test financial summary
        summary = odoo_mcp.get_financial_summary()
        print(f"Financial summary: {summary}")

        # Test getting unpaid invoices
        unpaid = odoo_mcp.get_unpaid_invoices()
        print(f"Unpaid invoices: {len(unpaid) if isinstance(unpaid, list) else 0}")

        # Test generating audit
        audit = odoo_mcp.generate_weekly_audit()
        print(f"Weekly audit generated: {audit.get('report_date')}")

        print("Odoo MCP test completed.")
    else:
        print("Odoo MCP Server initialized.")
        print(f"Connected to: {odoo_mcp.odoo_url}")
        print(f"Database: {odoo_mcp.database}")
        print("Ready to process Odoo requests from Claude.")


if __name__ == "__main__":
    main()