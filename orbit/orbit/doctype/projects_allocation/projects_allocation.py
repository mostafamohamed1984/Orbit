# Copyright (c) 2025, Smart Vision Group and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectsAllocation(Document):
	def on_submit(self):
		doc = self
		# Resolve company
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
		frappe.log_error(f"Using company: {default_company} for Projects Allocation: {doc.name}", "Debug: Projects Allocation Company Selection")
		journal_entries_created = []
		for service_row in (doc.service_allocation or []):
			try:
				je = frappe.new_doc("Journal Entry")
				je.company = default_company
				je.posting_date = doc.date
				je.user_remark = service_row.remark or f"Service allocation for {service_row.item}"
				allocated_amount = service_row.allocated_amount or 0
				payment_amount = service_row.payment_amount or 0
				payment_tax = service_row.payment_tax or 0
				if service_row.customer_debit_to and allocated_amount > 0:
					row = je.append("accounts", {})
					row.account = service_row.customer_debit_to
					row.credit_in_account_currency = allocated_amount
					row.party_type = "Customer"
					row.party = doc.customer
					if service_row.invoice:
						row.reference_type = "Sales Invoice"
						row.reference_name = service_row.invoice
					row.user_remark = service_row.remark or "Service allocation"
				if service_row.advance_account and allocated_amount > 0:
					row = je.append("accounts", {})
					row.account = service_row.advance_account
					row.debit_in_account_currency = allocated_amount
					row.party_type = "Customer"
					row.party = doc.customer
					row.is_advance = "No"
					row.user_remark = service_row.remark or "Advance allocation"
				if service_row.unearned_account and payment_amount > 0:
					row = je.append("accounts", {})
					row.account = service_row.unearned_account
					row.debit_in_account_currency = payment_amount
					row.user_remark = service_row.remark or "Unearned revenue"
				if service_row.revenue_account and payment_amount > 0:
					row = je.append("accounts", {})
					row.account = service_row.revenue_account
					row.credit_in_account_currency = payment_amount
					row.user_remark = service_row.remark or "Revenue recognition"
				if payment_tax > 0:
					invoice_tax_account = None
					if service_row.invoice:
						try:
							invoice_doc = frappe.get_doc("Sales Invoice", service_row.invoice)
							if invoice_doc.taxes and len(invoice_doc.taxes) > 0:
								invoice_tax_account = invoice_doc.taxes[0].account_head
						except Exception:
							invoice_tax_account = None
					if invoice_tax_account:
						row = je.append("accounts", {})
						row.account = invoice_tax_account
						row.debit_in_account_currency = payment_tax
						row.user_remark = service_row.remark or "Tax allocation"
					if doc.tax_account:
						row = je.append("accounts", {})
						row.account = doc.tax_account
						row.credit_in_account_currency = payment_tax
						row.user_remark = service_row.remark or "Tax liability"
				je.save()
				je.submit()
				journal_entries_created.append(je.name)
				if service_row.project_agreement_reference:
					try:
						pa = frappe.get_doc("Project Agreement", service_row.project_agreement_reference)
						if service_row.allocate_from == "Gov. Fees":
							row = pa.append("expenses_log", {})
							row.date = doc.date
							row.amount = allocated_amount
							row.description = service_row.remark or f"Allocated From {doc.name}"
							row.transaction_type = "Allocated"
							# Recalc expenses
							exp_total = 0
							for r in pa.expenses_log:
								exp_total += (r.amount or 0)
							pa.expense_amount = exp_total
							total_gov = pa.total_government_fees or 0
							pa.advance_balance = total_gov - exp_total
						elif service_row.allocate_from == "Trust Fees":
							row = pa.append("trust_fees_log", {})
							row.date = doc.date
							row.amount = allocated_amount
							row.description = service_row.remark or f"Allocated From {doc.name}"
							row.transaction_type = "Allocated"
							total_claimed = 0
							for r in pa.trust_fees_log:
								total_claimed += (r.amount or 0)
							pa.total_claimed_trust_fees = total_claimed
							total_trust = pa.total_trust_fees or 0
							pa.trust_fees_balance = total_trust - total_claimed
						# Always append payment_log
						row = pa.append("payment_log", {})
						row.date = doc.date
						row.payment_amount = payment_amount
						row.payment_tax = payment_tax
						row.transaction_type = "Allocation"
						row.item = service_row.item
						row.remark = service_row.remark or f"Allocation payment for {service_row.item}"
						row.reference = je.name
						total_received = 0
						received_tax = 0
						for p in pa.payment_log:
							amt = p.payment_amount or 0
							tax = p.payment_tax or 0
							total_received += amt
							received_tax += tax
						pa.total_received = total_received
						pa.received_tax = received_tax
						total_services_amount = pa.total_services_amount or 0
						pa.unclaimed_amount = total_services_amount - total_received
						pa.save()
					except Exception as e:
						frappe.log_error(f"Error updating Project Agreement: {str(e)}", "Projects Allocation Agreement Update Error")
			except Exception as e:
				frappe.log_error(f"Error creating journal entry for service allocation: {str(e)}", "Projects Allocation Service Error")
				frappe.throw(f"Error creating journal entry for service allocation {service_row.item}: {str(e)}")
		if journal_entries_created:
			frappe.msgprint(f"Successfully created {len(journal_entries_created)} Journal Entry(ies) for Projects Allocation {doc.name}")
		else:
			frappe.msgprint("No journal entries were created.")
