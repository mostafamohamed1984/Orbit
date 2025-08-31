# Copyright (c) 2025, Smart Vision Group and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OutsourcePayment(Document):
	def on_submit(self):
		doc = self
		default_company = None
		try:
			if doc.company:
				default_company = doc.company
		except Exception:
			pass
		if not default_company:
			try:
				user_defaults = frappe.db.get_value("User Permission", {"user": frappe.session.user, "allow": "Company"}, "for_value")
				if user_defaults:
					default_company = user_defaults
			except Exception:
				pass
		if not default_company:
			try:
				default_company = frappe.db.get_single_value("Global Defaults", "default_company")
			except Exception:
				pass
		if not default_company:
			try:
				orbit_company = frappe.db.get_value("Company", {"name": "Orbit"}, "name")
				if orbit_company:
					default_company = orbit_company
			except Exception:
				pass
		if not default_company:
			try:
				companies = frappe.get_all("Company", limit=1)
				if companies:
					default_company = companies[0].name
			except Exception:
				pass
		if not default_company:
			frappe.throw("No company found. Please create a company first.")
		frappe.log_error(f"Using company: {default_company} for Outsource Payment: {doc.name}", "Debug: Outsource Payment Company Selection")
		journal_entries_created = []
		for service_row in (doc.outsource_services_payment or []):
			try:
				je = frappe.new_doc("Journal Entry")
				je.company = default_company
				je.posting_date = doc.date
				je.user_remark = service_row.remark or f"Outsource payment for {service_row.item}"
				total_amount = (service_row.payment_amount or 0) + (service_row.payment_tax or 0)
				if service_row.supplier_account:
					row = je.append("accounts", {})
					row.account = service_row.supplier_account
					row.debit_in_account_currency = total_amount
					row.party_type = "Supplier"
					row.party = doc.supplier
					if service_row.invoice:
						row.reference_type = "Purchase Invoice"
						row.reference_name = service_row.invoice
					row.user_remark = service_row.remark or "Outsource payment"
				if doc.pay_from_account:
					row = je.append("accounts", {})
					row.account = doc.pay_from_account
					row.credit_in_account_currency = total_amount
					row.user_remark = service_row.remark or "Outsource payment made"
				je.save()
				je.submit()
				journal_entries_created.append(je.name)
				if getattr(service_row, "project_agreement", None):
					try:
						pa = frappe.get_doc("Project Agreement", service_row.project_agreement)
						row = pa.append("outsource_payment_log", {})
						row.date = doc.date
						row.engineer = doc.supplier
						row.item = service_row.item
						row.payment_amount = service_row.payment_amount or 0
						row.payment_tax = service_row.payment_tax or 0
						row.remark = service_row.remark or f"Outsource payment for {service_row.item}"
						row.reference = je.name
						total_paid = 0
						total_paid_taxes = 0
						for r in pa.outsource_payment_log:
							amt = r.payment_amount or 0
							tax = r.payment_tax or 0
							total_paid += amt
							total_paid_taxes += tax
						pa.total_paid = total_paid
						pa.total_paid_taxes = total_paid_taxes
						total_requested = pa.total_requested_services or 0
						pa.pending_to_pay = total_requested - total_paid - total_paid_taxes
						pa.save()
					except Exception as e:
						frappe.log_error(f"Error updating Project Agreement: {str(e)}", "Outsource Payment Agreement Update Error")
			except Exception as e:
				frappe.log_error(f"Error creating journal entry for outsource payment: {str(e)}", "Outsource Payment Service Error")
				frappe.throw(f"Error creating journal entry for outsource payment {service_row.item}: {str(e)}")
		if journal_entries_created:
			frappe.msgprint(f"Successfully created {len(journal_entries_created)} Journal Entry(ies) for Outsource Payment {doc.name}")
		else:
			frappe.msgprint("No journal entries were created.")
