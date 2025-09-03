# # Copyright (c) 2025, Smart Vision Group and contributors
# # For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProjectExpenses(Document):
	pass
# 	def on_submit(self):
# 		doc = self
# 		default_company = None
# 		try:
# 			if doc.company:
# 				default_company = doc.company
# 		except Exception:
# 			pass
# 		if not default_company:
# 			try:
# 				user_defaults = frappe.db.get_value("User Permission", {"user": frappe.session.user, "allow": "Company"}, "for_value")
# 			except Exception:
# 				user_defaults = None
# 			if user_defaults:
# 				default_company = user_defaults
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
# 		frappe.log_error("Using company: " + str(default_company) + " for Project Expenses: " + str(doc.name), "Debug: Project Expenses Company Selection")
# 		journal_entries_created = []
# 		# Expenses Items
# 		for expense_row in (doc.expenses_items or []):
# 			try:
# 				if not expense_row.amount or not expense_row.expense_account:
# 					continue
# 				je = frappe.new_doc("Journal Entry")
# 				je.company = default_company
# 				je.posting_date = expense_row.date or doc.posting_date
# 				je.user_remark = expense_row.description or ("Project expense for " + str(doc.project_agreement))
# 				allocated_for_this_expense = expense_row.allocated_amount or 0
# 				advances_to_process = []
# 				total_advance_allocated = 0
# 				for advance_row in (doc.advances or []):
# 					if advance_row.allocated_amount and advance_row.allocated_amount > 0:
# 						total_advance_allocated += advance_row.allocated_amount
# 				if total_advance_allocated > 0 and allocated_for_this_expense > 0:
# 					for advance_row in (doc.advances or []):
# 						if advance_row.allocated_amount and advance_row.allocated_amount > 0:
# 							proportion = advance_row.allocated_amount / total_advance_allocated
# 							advance_amount_for_this = round((allocated_for_this_expense * proportion), 2)
# 							try:
# 								emp_adv = frappe.get_doc("Employee Advance", advance_row.employee_advance)
# 								advance_account = emp_adv.advance_account
# 								employee = emp_adv.employee
# 								available_unclaimed = round((emp_adv.advance_amount or 0) - (emp_adv.return_amount or 0), 2)
# 								if advance_amount_for_this > available_unclaimed:
# 									advance_amount_for_this = available_unclaimed
# 								if advance_amount_for_this > 0:
# 									advances_to_process.append({
# 										"advance_account": advance_account,
# 										"allocated_amount": advance_amount_for_this,
# 										"employee_advance": advance_row.employee_advance,
# 										"employee": employee,
# 									})
# 							except Exception as e:
# 								frappe.log_error("Error getting advance details for " + str(advance_row.employee_advance) + ": " + str(e), "Project Expenses Advance Error")
# 				# Advances credit rows
# 				for info in advances_to_process:
# 					row = je.append("accounts", {})
# 					row.account = info["advance_account"]
# 					row.credit_in_account_currency = round(info["allocated_amount"], 2)
# 					row.party_type = "Employee"
# 					row.party = info["employee"]
# 					row.reference_type = "Employee Advance"
# 					row.reference_name = info["employee_advance"]
# 					row.user_remark = expense_row.description or "Advance allocation for expense"
# 				# Expense debit (allocated)
# 				if allocated_for_this_expense > 0:
# 					row = je.append("accounts", {})
# 					row.account = expense_row.expense_account
# 					row.debit_in_account_currency = allocated_for_this_expense
# 					row.user_remark = expense_row.description or "Project expense"
# 				# Customer advance debit (allocated)
# 				if doc.customer_advance_account and doc.customer and allocated_for_this_expense > 0:
# 					row = je.append("accounts", {})
# 					row.account = doc.customer_advance_account
# 					row.debit_in_account_currency = allocated_for_this_expense
# 					row.party_type = "Customer"
# 					row.party = doc.customer
# 					row.user_remark = expense_row.description or "Customer advance utilization"
# 				# Expense credit (allocated)
# 				if allocated_for_this_expense > 0:
# 					row = je.append("accounts", {})
# 					row.account = expense_row.expense_account
# 					row.credit_in_account_currency = allocated_for_this_expense
# 					row.user_remark = expense_row.description or "Project expense allocation"
# 				je.save()
# 				je.submit()
# 				journal_entries_created.append(je.name)
# 			except Exception as e:
# 				frappe.log_error("Error creating journal entry for expense: " + str(e), "Project Expenses Error")
# 				frappe.throw("Error creating journal entry for expense on " + str(expense_row.date) + ": " + str(e))
# 		# Trust Fees Expenses
# 		try:
# 			trust_fees_expenses_exist = doc.trust_fees_expenses and len(doc.trust_fees_expenses) > 0
# 		except Exception:
# 			trust_fees_expenses_exist = False
# 		if trust_fees_expenses_exist:
# 			for trow in doc.trust_fees_expenses:
# 				try:
# 					if not trow.amount:
# 						continue
# 					je = frappe.new_doc("Journal Entry")
# 					je.company = default_company
# 					je.posting_date = trow.date or doc.posting_date
# 					je.user_remark = trow.description or ("Trust fee expense for " + str(doc.project_agreement))
# 					trust_fee_amount = trow.amount
# 					if doc.expense_trust_fees_via_ == 'Employee Advance':
# 						allocated_amount = trow.allocated_amount or 0
# 						if allocated_amount > 0:
# 							advances_to_process = []
# 							total_advance_allocated = 0
# 							for advance_row in (doc.advances or []):
# 								if advance_row.allocated_amount and advance_row.allocated_amount > 0:
# 									total_advance_allocated += advance_row.allocated_amount
# 							if total_advance_allocated > 0 and allocated_amount > 0:
# 								for advance_row in (doc.advances or []):
# 									if advance_row.allocated_amount and advance_row.allocated_amount > 0:
# 										proportion = advance_row.allocated_amount / total_advance_allocated
# 										alloc = round(allocated_amount * proportion, 2)
# 										try:
# 											emp_adv = frappe.get_doc("Employee Advance", advance_row.employee_advance)
# 											advance_account = emp_adv.advance_account
# 											employee = emp_adv.employee
# 											available_unclaimed = round((emp_adv.advance_amount or 0) - (emp_adv.return_amount or 0), 2)
# 											if alloc > available_unclaimed:
# 												alloc = available_unclaimed
# 											if alloc > 0:
# 												advances_to_process.append({
# 													'advance_account': advance_account,
# 													'allocated_amount': alloc,
# 													'employee_advance': advance_row.employee_advance,
# 													'employee': employee
# 												})
# 										except Exception as e:
# 											frappe.log_error("Error getting advance details for trust fee expense " + str(advance_row.employee_advance) + ": " + str(e), "Trust Fee Expense Advance Error")
# 						for info in advances_to_process:
# 							row = je.append("accounts", {})
# 							row.account = info['advance_account']
# 							row.credit_in_account_currency = round(info['allocated_amount'], 2)
# 							row.party_type = "Employee"
# 							row.party = info['employee']
# 							row.reference_type = "Employee Advance"
# 							row.reference_name = info['employee_advance']
# 							row.user_remark = trow.description or "Trust fee advance allocation"
# 						if doc.trust_fees_account and (trow.allocated_amount or 0) > 0:
# 							row = je.append("accounts", {})
# 							row.account = doc.trust_fees_account
# 							row.debit_in_account_currency = trow.allocated_amount
# 							row.party_type = "Customer"
# 							row.party = doc.customer
# 							row.user_remark = trow.description or "Trust fee expense"
# 					elif doc.expense_trust_fees_via_ == 'Other':
# 						if doc.payment_account and doc.trust_fees_account and trust_fee_amount > 0:
# 							row = je.append("accounts", {})
# 							row.account = doc.payment_account
# 							row.credit_in_account_currency = trust_fee_amount
# 							row.user_remark = trow.description or "Trust fee payment"
# 							row = je.append("accounts", {})
# 							row.account = doc.trust_fees_account
# 							row.debit_in_account_currency = trust_fee_amount
# 							row.party_type = "Customer"
# 							row.party = doc.customer
# 							row.user_remark = trow.description or "Trust fee expense"
# 					else:
# 						# default like Employee Advance
# 						allocated_amount = trow.allocated_amount or 0
# 						if allocated_amount > 0:
# 							# reuse above logic (omitted)
# 							pass
# 					je.save()
# 					je.submit()
# 					journal_entries_created.append(je.name)
# 				except Exception as e:
# 					frappe.log_error("Error creating journal entry for trust fee expense: " + str(e), "Trust Fee Expense Error")
# 					frappe.throw("Error creating journal entry for trust fee expense on " + str(trow.date) + ": " + str(e))
# 		# Update Project Agreement totals and logs
# 		if doc.project_agreement:
# 			try:
# 				pa = frappe.get_doc("Project Agreement", doc.project_agreement)
# 				expenses_log_added = 0
# 				pending_expenses_added = 0
# 				for exp in (doc.expenses_items or []):
# 					if exp.allocated_amount and exp.allocated_amount > 0:
# 						row = pa.append("expenses_log", {})
# 						row.date = exp.date
# 						row.amount = exp.allocated_amount
# 						row.description = exp.description or "Project expense"
# 						row.reference = doc.name
# 						row.transaction_type = "Expense"
# 						expenses_log_added += 1
# 					if exp.pending_amount and exp.pending_amount > 0:
# 						row = pa.append("pending_expenses", {})
# 						row.amount = exp.pending_amount
# 						row.reference = doc.name
# 						row.paid = 0
# 						pending_expenses_added += 1
# 				current_expense_amount = pa.expense_amount or 0
# 				pa.expense_amount = current_expense_amount + (doc.total_expenses or 0)
# 				current_pending_amount = pa.pending_amount or 0
# 				pa.pending_amount = current_pending_amount + (doc.total_pending or 0)
# 				current_advance_balance = pa.advance_balance or 0
# 				pa.advance_balance = current_advance_balance - (doc.total_expenses or 0)
# 				trust_fees_log_added = 0
# 				try:
# 					trust_fees_expenses_exist = doc.trust_fees_expenses and len(doc.trust_fees_expenses) > 0
# 				except Exception:
# 					trust_fees_expenses_exist = False
# 				if trust_fees_expenses_exist:
# 					for trow in doc.trust_fees_expenses:
# 						if trow.amount and trow.amount > 0:
# 							row = pa.append("trust_fees_log", {})
# 							row.contractor = doc.contractor
# 							row.date = trow.date or doc.posting_date
# 							row.amount = trow.amount
# 							row.description = trow.description or "Trust fee expense"
# 							row.reference = doc.name
# 							row.transaction_type = "Expense"
# 							trust_fees_log_added += 1
# 					total_claimed_trust_fees = 0
# 					for r in pa.trust_fees_log:
# 						total_claimed_trust_fees += (r.amount or 0)
# 					pa.total_claimed_trust_fees = total_claimed_trust_fees
# 					total_trust_fees = pa.total_trust_fees or 0
# 					pa.trust_fees_balance = total_trust_fees - total_claimed_trust_fees
# 				pa.save()
# 			except Exception as e:
# 				frappe.log_error("Error updating Project Agreement: " + str(e), "Project Expenses Agreement Update Error")
# 		if journal_entries_created:
# 			frappe.msgprint("Successfully created " + str(len(journal_entries_created)) + " Journal Entry(ies) for Project Expenses " + str(doc.name))
# 		else:
# 			frappe.msgprint("No journal entries were created - no valid expense items found.")
