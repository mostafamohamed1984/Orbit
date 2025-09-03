# Copyright (c) 2025, Smart Vision Group and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectPayment(Document):
	pass
# 	def on_submit(self):
# 		doc = self
# 		# Resolve default company
# 		default_company = None
# 		try:
# 			if doc.company:
# 				default_company = doc.company
# 		except Exception:
# 			pass
# 		if not default_company:
# 			try:
# 				user_defaults = frappe.db.get_value(
# 					"User Permission",
# 					{"user": frappe.session.user, "allow": "Company"},
# 					"for_value",
# 				)
# 				if user_defaults:
# 					default_company = user_defaults
# 			except Exception:
# 				pass
# 		if not default_company:
# 			try:
# 				default_company = frappe.db.get_single_value("Global Defaults", "default_company")
# 			except Exception:
# 				pass
# 		if not default_company:
# 			try:
# 				orbit_company = frappe.db.get_value("Company", {"name": "Orbit"}, "name")
# 				if orbit_company:
# 					default_company = orbit_company
# 			except Exception:
# 				pass
# 		if not default_company:
# 			try:
# 				companies = frappe.get_all("Company", limit=1)
# 				if companies:
# 					default_company = companies[0].name
# 			except Exception:
# 				pass
# 		if not default_company:
# 			frappe.throw("No company found. Please create a company first.")
# 		frappe.log_error(
# 			f"Using company: {default_company} for Project Payment: {doc.name}",
# 			"Debug: Project Payment Company Selection",
# 		)

# 		journal_entries_created = []
# 		# Determine customer_type
# 		try:
# 			customer_type = doc.customer_type if doc.customer_type else "Customer"
# 		except Exception:
# 			customer_type = "Customer"

# 		# Process Service Payment Details -> create Journal Entries
# 		for service_row in (doc.service_payment_details or []):
# 			try:
# 				je = frappe.new_doc("Journal Entry")
# 				je.company = default_company
# 				je.posting_date = doc.date
# 				je.user_remark = service_row.remark or f"Service payment for {service_row.item}"
# 				total_amount = (service_row.payment_amount or 0) + (service_row.payment_tax or 0)
# 				payment_amount = service_row.payment_amount or 0
# 				payment_tax = service_row.payment_tax or 0

# 				# Party Account Credit
# 				if doc.party_account:
# 					invoice_customer = None
# 					if service_row.invoice:
# 						try:
# 							invoice_doc = frappe.get_doc("Sales Invoice", service_row.invoice)
# 							invoice_customer = invoice_doc.customer
# 						except Exception:
# 							invoice_customer = None
# 					party = je.append("accounts", {})
# 					party.account = doc.party_account
# 					party.credit_in_account_currency = total_amount
# 					party.party_type = "Customer"
# 					party.party = doc.customer
# 					if invoice_customer and invoice_customer == doc.customer and service_row.invoice:
# 						party.reference_type = "Sales Invoice"
# 						party.reference_name = service_row.invoice
# 					party.user_remark = service_row.remark or "Service payment"

# 				# Receiving Account Debit
# 				if doc.receiving_account:
# 					recv = je.append("accounts", {})
# 					recv.account = doc.receiving_account
# 					recv.debit_in_account_currency = total_amount
# 					recv.user_remark = service_row.remark or "Service payment received"

# 				# Unearned Debit
# 				if service_row.unearned_account and payment_amount > 0:
# 					unearned = je.append("accounts", {})
# 					unearned.account = service_row.unearned_account
# 					unearned.debit_in_account_currency = payment_amount
# 					unearned.user_remark = service_row.remark or "Unearned revenue"

# 				# Revenue Credit
# 				if service_row.revenue_account and payment_amount > 0:
# 					revenue = je.append("accounts", {})
# 					revenue.account = service_row.revenue_account
# 					revenue.credit_in_account_currency = payment_amount
# 					revenue.user_remark = service_row.remark or "Revenue recognition"

# 				# Tax split
# 				if payment_tax > 0:
# 					invoice_tax_account = None
# 					if service_row.invoice:
# 						try:
# 							invoice_doc = frappe.get_doc("Sales Invoice", service_row.invoice)
# 							if invoice_doc.taxes and len(invoice_doc.taxes) > 0:
# 								invoice_tax_account = invoice_doc.taxes[0].account_head
# 						except Exception:
# 							invoice_tax_account = None
# 					if invoice_tax_account:
# 						tax_debit = je.append("accounts", {})
# 						tax_debit.account = invoice_tax_account
# 						tax_debit.debit_in_account_currency = payment_tax
# 						tax_debit.user_remark = service_row.remark or "Tax payment"
# 					if doc.tax_account:
# 						tax_credit = je.append("accounts", {})
# 						tax_credit.account = doc.tax_account
# 						tax_credit.credit_in_account_currency = payment_tax
# 						tax_credit.user_remark = service_row.remark or "Tax liability"

# 				je.save()
# 				je.submit()
# 				journal_entries_created.append(je.name)

# 				# Update Project Agreement logs (Customer vs Contractor)
# 				if service_row.project_agreement_reference:
# 					try:
# 						pa = frappe.get_doc("Project Agreement", service_row.project_agreement_reference)
# 						if customer_type == "Customer":
# 							row = pa.append("payment_log", {})
# 							row.date = doc.date
# 							row.item = service_row.item
# 							row.payment_amount = service_row.payment_amount or 0
# 							row.payment_tax = service_row.payment_tax or 0
# 							row.transaction_type = "Payment"
# 							row.remark = service_row.remark or f"Service payment for {service_row.item}"
# 							row.reference = je.name
# 							total_received = 0
# 							received_tax = 0
# 							cancelled_amount = 0
# 							cancelled_taxes = 0
# 							for p in pa.payment_log:
# 								amt = p.payment_amount or 0
# 								tax = p.payment_tax or 0
# 								kind = p.transaction_type or ""
# 								if kind in ["Payment", "Allocation"]:
# 									total_received += amt
# 									received_tax += tax
# 								elif kind in ["Return", "Cancel Due", "Discount"]:
# 									cancelled_amount += amt
# 									cancelled_taxes += tax
# 							pa.total_received = total_received
# 							pa.received_tax = received_tax
# 							pa.cancelled_amount = cancelled_amount
# 							pa.cancelled_taxes = cancelled_taxes
# 							total_services_amount = pa.total_services_amount or 0
# 							pa.unclaimed_amount = total_services_amount - total_received - cancelled_amount
# 						elif customer_type == "Contractor":
# 							row = pa.append("contractors_payment_log", {})
# 							row.contractor = doc.customer
# 							row.date = doc.date
# 							row.payment_amount = service_row.payment_amount or 0
# 							row.payment_tax = service_row.payment_tax or 0
# 							row.item = service_row.item
# 							row.remark = service_row.remark or f"Contractor payment for {service_row.item}"
# 							row.reference = je.name
# 							total_paid = 0
# 							total_paid_taxes = 0
# 							for r in pa.contractors_payment_log:
# 								amt = r.payment_amount or 0
# 								tax = r.payment_tax or 0
# 								total_paid += amt
# 								total_paid_taxes += tax
# 							pa.total_received_from_contractors = total_paid
# 							pa.total_received_taxes_from_contractors = total_paid_taxes
# 							total_contractors_services = pa.total_contractors_services or 0
# 							pa.total_unclaimed_from_contractors = total_contractors_services - total_paid - total_paid_taxes
# 						pa.save()
# 					except Exception as e:
# 						frappe.log_error(f"Error updating Project Agreement: {str(e)}", "Project Payment Service Agreement Update Error")
# 			except Exception as e:
# 				frappe.log_error(f"Error creating journal entry for service payment: {str(e)}", "Project Payment Service Error")
# 				frappe.throw(f"Error creating journal entry for service payment {service_row.item}: {str(e)}")

# 		# Government Fees (only for Customer payments)
# 		if customer_type == "Customer":
# 			for gov_fee_row in (doc.government_fees or []):
# 				try:
# 					je = frappe.new_doc("Journal Entry")
# 					je.company = default_company
# 					je.posting_date = doc.date
# 					je.user_remark = gov_fee_row.remark or "Government fee payment"
# 					if doc.advance_account:
# 						adv = je.append("accounts", {})
# 						adv.account = doc.advance_account
# 						adv.credit_in_account_currency = gov_fee_row.amount
# 						adv.party_type = "Customer"
# 						adv.party = doc.customer
# 						adv.is_advance = "Yes"
# 						adv.user_remark = gov_fee_row.remark or "Government fee advance"
# 					if doc.receiving_account:
# 						recv = je.append("accounts", {})
# 						recv.account = doc.receiving_account
# 						recv.debit_in_account_currency = gov_fee_row.amount
# 						recv.user_remark = gov_fee_row.remark or "Government fee received"
# 					je.save()
# 					je.submit()
# 					journal_entries_created.append(je.name)
# 					frappe.db.set_value("Government Fees Payment", gov_fee_row.name, "journal_entry_reference", je.name)
# 					gov_fee_row.journal_entry_reference = je.name
# 					if getattr(gov_fee_row, "project_agreement", None):
# 						try:
# 							pa = frappe.get_doc("Project Agreement", gov_fee_row.project_agreement)
# 							new_row = pa.append("government_fees", {})
# 							new_row.date = doc.date
# 							new_row.payment_method = doc.mode_of_payment
# 							new_row.amount = gov_fee_row.amount
# 							new_row.remark = gov_fee_row.remark
# 							new_row.journal_entry_reference = je.name
# 							# Reconcile pending expenses against this fee
# 							if gov_fee_row.amount and gov_fee_row.amount > 0:
# 								pending = [row for row in pa.pending_expenses if not row.paid]
# 								pending.sort(key=lambda x: x.idx)
# 								remaining = float(gov_fee_row.amount)
# 								for prow in pending:
# 									if remaining <= 0:
# 										break
# 									p_amt = float(prow.amount or 0)
# 									col = float(prow.collected_amount or 0)
# 									out = p_amt - col
# 									if out <= 0:
# 										continue
# 									if remaining >= out:
# 										prow.collected_amount = p_amt
# 										prow.paid = 1
# 										remaining = remaining - out
# 									else:
# 										prow.collected_amount = col + remaining
# 										remaining = 0
# 							# Recalc totals
# 							total_gov = 0
# 							for r in pa.government_fees:
# 								total_gov += (r.amount or 0)
# 							pa.total_government_fees = total_gov
# 							total_services_amount = pa.total_services_amount or 0
# 							pa.total_project_amount = total_gov + total_services_amount
# 							current_expense_amount = pa.expense_amount or 0
# 							pa.advance_balance = total_gov - current_expense_amount
# 							pending_total = 0
# 							for prow in pa.pending_expenses:
# 								if not prow.paid:
# 									row_amount = float(prow.amount or 0)
# 									row_collected = float(prow.collected_amount or 0)
# 									pending_total += (row_amount - row_collected)
# 							pa.pending_amount = pending_total
# 							pa.save()
# 						except Exception as e:
# 							frappe.log_error(f"Error updating Project Agreement: {str(e)}", "Project Payment Gov Fee Update Error")
# 				except Exception as e:
# 					frappe.log_error(f"Error creating journal entry for government fee: {str(e)}", "Project Payment Gov Fee Error")
# 					frappe.throw(f"Error creating journal entry for government fee: {str(e)}")

# 		# Trust Fees (only for Customer payments)
# 		try:
# 			trust_fees_exist = doc.trust_fees_payment and len(doc.trust_fees_payment) > 0
# 		except Exception:
# 			trust_fees_exist = False
# 		if trust_fees_exist and customer_type == "Customer":
# 			for trust_fee_row in doc.trust_fees_payment:
# 				try:
# 					je = frappe.new_doc("Journal Entry")
# 					je.company = default_company
# 					je.posting_date = doc.date
# 					je.user_remark = trust_fee_row.remark or "Trust fee payment"
# 					if doc.trust_account:
# 						acc = je.append("accounts", {})
# 						acc.account = doc.trust_account
# 						acc.credit_in_account_currency = trust_fee_row.amount
# 						acc.party_type = "Customer"
# 						acc.party = doc.customer
# 						acc.is_advance = "Yes"
# 						acc.user_remark = trust_fee_row.remark or "Trust fee advance"
# 					if doc.receiving_account:
# 						recv = je.append("accounts", {})
# 						recv.account = doc.receiving_account
# 						recv.debit_in_account_currency = trust_fee_row.amount
# 						recv.user_remark = trust_fee_row.remark or "Trust fee received"
# 					je.save()
# 					je.submit()
# 					journal_entries_created.append(je.name)
# 					frappe.db.set_value("Trust Fees Payment", trust_fee_row.name, "journal_entry_reference", je.name)
# 					trust_fee_row.journal_entry_reference = je.name
# 					if getattr(trust_fee_row, "project_agreement", None):
# 						try:
# 							pa = frappe.get_doc("Project Agreement", trust_fee_row.project_agreement)
# 							row = pa.append("trust_fees", {})
# 							row.date = doc.date
# 							row.payment_method = doc.mode_of_payment
# 							row.amount = trust_fee_row.amount
# 							row.remark = trust_fee_row.remark
# 							row.journal_entry_reference = je.name
# 							total_trust_fees = 0
# 							for r in pa.trust_fees:
# 								total_trust_fees += (r.amount or 0)
# 							pa.total_trust_fees = total_trust_fees
# 							total_claimed_trust_fees = pa.total_claimed_trust_fees or 0
# 							pa.trust_fees_balance = total_trust_fees - total_claimed_trust_fees
# 							pa.save()
# 						except Exception as e:
# 							frappe.log_error(f"Error updating Project Agreement trust fees: {str(e)}", "Project Payment Trust Fee Update Error")
# 				except Exception as e:
# 					frappe.log_error(f"Error creating journal entry for trust fee: {str(e)}", "Project Payment Trust Fee Error")
# 					frappe.throw(f"Error creating journal entry for trust fee: {str(e)}")

# 		# Done (remaining Government/Trust fees handled in next edits)
# 		if journal_entries_created:
# 			frappe.msgprint(f"Successfully created {len(journal_entries_created)} Journal Entry(ies) for Project Payment {doc.name}")
# 		else:
# 			frappe.msgprint("No journal entries were created.")
