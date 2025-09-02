# # Copyright (c) 2025, Smart Vision Group and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class ProjectAgreement(Document):
# 	def on_submit(self):
# 		# Integrate: Create Sales Invoices for services not yet invoiced
# 		self._create_sales_invoices_for_project_services()
# 		# Create Sales Invoices for contractors services
# 		self._create_sales_invoices_for_contractors_services()
# 		# Create Purchase Invoices for outsource services
# 		self._create_purchase_invoices_for_outsource_services()

# 	def on_update_after_submit(self):
# 		# Re-run creation flows for newly added rows on submitted docs
# 		self._create_sales_invoices_for_project_services()
# 		self._create_sales_invoices_for_contractors_services()
# 		self._create_purchase_invoices_for_outsource_services()

# 	def _get_default_company(self) -> str:
# 		default_company = None
# 		# Method 1: Use company on Project Agreement
# 		try:
# 			if self.company:
# 				default_company = self.company
# 		except Exception:
# 			pass
# 		# Method 2: User default
# 		if not default_company:
# 			try:
# 				user_defaults = frappe.db.get_value(
# 					"User Permission", {"user": frappe.session.user, "allow": "Company"}, "for_value"
# 				)
# 				if user_defaults:
# 					default_company = user_defaults
# 			except Exception:
# 				pass
# 		# Method 3: Global default
# 		if not default_company:
# 			try:
# 				default_company = frappe.db.get_single_value("Global Defaults", "default_company")
# 			except Exception:
# 				pass
# 		# Method 4: Company named "Orbit"
# 		if not default_company:
# 			try:
# 				orbit_company = frappe.db.get_value("Company", {"name": "Orbit"}, "name")
# 				if orbit_company:
# 					default_company = orbit_company
# 			except Exception:
# 				pass
# 		# Method 5: Any company
# 		if not default_company:
# 			try:
# 				companies = frappe.get_all("Company", limit=1)
# 				if companies:
# 					default_company = companies[0].name
# 			except Exception:
# 				pass
# 		if not default_company:
# 			frappe.throw("No company found. Please create a company first.")
# 		return default_company

# 	def _create_sales_invoices_for_project_services(self) -> None:
# 		default_company = self._get_default_company()
# 		frappe.log_error(
# 			f"Using company: {default_company} for Project Agreement: {self.name}",
# 			"Debug: Company Selection",
# 		)
# 		invoices_created = []

# 		for service_row in (self.project_services or []):
# 			if not getattr(service_row, "invoiced", 0):
# 				# Create Sales Invoice
# 				sales_invoice = frappe.new_doc("Sales Invoice")
# 				sales_invoice.customer = self.customer
# 				sales_invoice.company = default_company
# 				sales_invoice.custom_project_agreement = self.name
# 				sales_invoice.posting_date = getattr(service_row, "invoice_date", None)
# 				sales_invoice.set_posting_time = 1

# 				customer_doc = frappe.get_doc("Customer", self.customer)
# 				company_doc = frappe.get_doc("Company", default_company)

# 				# Currency and price list
# 				try:
# 					customer_currency = getattr(customer_doc, "default_currency", None)
# 					if customer_currency:
# 						sales_invoice.currency = customer_currency
# 						sales_invoice.price_list_currency = customer_currency
# 					else:
# 						sales_invoice.currency = company_doc.default_currency
# 						sales_invoice.price_list_currency = company_doc.default_currency
# 				except Exception:
# 					sales_invoice.currency = company_doc.default_currency
# 					sales_invoice.price_list_currency = company_doc.default_currency

# 				try:
# 					customer_price_list = getattr(customer_doc, "default_price_list", None)
# 					if customer_price_list:
# 						sales_invoice.selling_price_list = customer_price_list
# 				except Exception:
# 					pass

# 				# Other customer defaults
# 				try:
# 					if getattr(customer_doc, "payment_terms", None):
# 						sales_invoice.payment_terms_template = customer_doc.payment_terms
# 				except Exception:
# 					pass
# 				try:
# 					if getattr(customer_doc, "customer_group", None):
# 						sales_invoice.customer_group = customer_doc.customer_group
# 				except Exception:
# 					pass
# 				try:
# 					if getattr(customer_doc, "territory", None):
# 						sales_invoice.territory = customer_doc.territory
# 				except Exception:
# 					pass

# 				# Override with agreement currency
# 				if getattr(self, "currency", None):
# 					sales_invoice.currency = self.currency
# 					sales_invoice.price_list_currency = self.currency
# 					company_currency = frappe.db.get_value("Company", default_company, "default_currency")
# 					if self.currency == company_currency:
# 						sales_invoice.conversion_rate = 1

# 				# Receivable account
# 				customer_receivable_account = None
# 				try:
# 					customer_receivable_account = frappe.db.get_value(
# 						"Party Account",
# 						{"parent": self.customer, "parenttype": "Customer", "company": default_company},
# 						"account",
# 					)
# 				except Exception:
# 					pass
# 				if not customer_receivable_account:
# 					try:
# 						customer_receivable_account = frappe.db.get_value("Company", default_company, "default_receivable_account")
# 					except Exception:
# 						pass
# 				if not customer_receivable_account:
# 					try:
# 						customer_receivable_account = frappe.db.get_value(
# 							"Account", {"company": default_company, "account_type": "Receivable", "is_group": 0}, "name"
# 						)
# 					except Exception:
# 						pass
# 				if not customer_receivable_account:
# 					try:
# 						accounts = frappe.db.sql(
# 							"""
# 							SELECT name FROM `tabAccount`
# 							WHERE company = %s AND is_group = 0
# 							AND (name LIKE '%%Debtors%%' OR name LIKE '%%Receivable%%' OR name LIKE '%%Customer%%')
# 							LIMIT 1
# 							""",
# 							(default_company,),
# 						)
# 						if accounts:
# 							customer_receivable_account = accounts[0][0]
# 					except Exception:
# 						pass
# 				if customer_receivable_account:
# 					sales_invoice.debit_to = customer_receivable_account
# 				else:
# 					receivable_count = frappe.db.count(
# 						"Account", {"company": default_company, "account_type": "Receivable", "is_group": 0}
# 					)
# 					frappe.throw(
# 						f"No receivable account found for company {default_company}. Found {receivable_count} receivable accounts. Please check customer setup or create receivable accounts."
# 					)

# 				# Essentials
# 				sales_invoice.ignore_pricing_rule = 1
# 				sales_invoice.conversion_rate = sales_invoice.conversion_rate or 1.0
# 				sales_invoice.plc_conversion_rate = sales_invoice.plc_conversion_rate or 1.0

# 				# Item
# 				item_row = sales_invoice.append("items", {})
# 				item_row.item_code = getattr(service_row, "item", None)
# 				item_row.qty = 1
# 				item_row.rate = getattr(service_row, "amount", 0)
# 				item_row.uom = "Nos"

# 				# Remarks
# 				if getattr(service_row, "remark", None):
# 					sales_invoice.remarks = service_row.remark

# 				# Taxes
# 				if getattr(service_row, "tax_template", None):
# 					try:
# 						tax_template = frappe.get_doc("Sales Taxes and Charges Template", service_row.tax_template)
# 						template_company = tax_template.company
# 						if template_company and template_company != default_company:
# 							frappe.log_error(
# 								f"Tax template {service_row.tax_template} belongs to company {template_company} but invoice is for company {default_company}"
# 							)
# 							frappe.msgprint(
# 								f"Warning: Tax template {service_row.tax_template} belongs to different company. Skipping taxes."
# 							)
# 						else:
# 							sales_invoice.taxes_and_charges = service_row.tax_template
# 							valid_taxes = []
# 							for tax in tax_template.taxes:
# 								account_company = None
# 								try:
# 									account_company = frappe.db.get_value("Account", tax.account_head, "company")
# 								except Exception:
# 									account_company = None
# 								if account_company == default_company:
# 									valid_taxes.append({
# 										"charge_type": tax.charge_type,
# 										"account_head": tax.account_head,
# 										"description": tax.description,
# 										"rate": tax.rate,
# 										"tax_amount": tax.tax_amount if tax.charge_type == "Actual" else 0
# 									})
# 								elif account_company:
# 									frappe.log_error(
# 										f"Account {tax.account_head} belongs to company {account_company}, expected {default_company}"
# 									)
# 							for tax_data in valid_taxes:
# 								sales_invoice.append("taxes", tax_data)
# 					except Exception as e:
# 						frappe.log_error(f"Error applying tax template: {str(e)}")
# 						frappe.msgprint(
# 							f"Warning: Could not apply tax template {service_row.tax_template}. Invoice created without taxes."
# 						)

# 				# Validate account set
# 				if not getattr(sales_invoice, "debit_to", None):
# 					frappe.throw(
# 						f"Debit To account is required but not set for Sales Invoice. Customer: {self.customer}, Company: {default_company}"
# 					)

# 				sales_invoice.run_method("set_missing_values")
# 				sales_invoice.save()
# 				sales_invoice.submit()

# 				# Sum taxes
# 				total_tax_amount = 0
# 				if getattr(sales_invoice, "taxes", None):
# 					for tax_row in sales_invoice.taxes:
# 						total_tax_amount = total_tax_amount + (tax_row.tax_amount or 0)

# 				# Update child row
# 				service_row.invoiced = 1
# 				service_row.reference_invoice = sales_invoice.name
# 				service_row.tax_amount = total_tax_amount
# 				invoices_created.append(sales_invoice.name)

# 		# Save document to persist child flags
# 		if invoices_created:
# 			self.save()
# 			invoice_count = len(invoices_created)
# 			frappe.msgprint(f"Successfully created {invoice_count} Sales Invoice(s)")

# 	def _create_sales_invoices_for_contractors_services(self) -> None:
# 		default_company = self._get_default_company()
# 		frappe.log_error(
# 			f"Using company: {default_company} for Project Agreement: {self.name}",
# 			"Debug: Company Selection Contractors",
# 		)
# 		invoices_created = []
# 		for service_row in (self.contractors_services or []):
# 			if not getattr(service_row, "invoiced", 0):
# 				sales_invoice = frappe.new_doc("Sales Invoice")
# 				sales_invoice.customer = service_row.contractor
# 				sales_invoice.company = default_company
# 				sales_invoice.custom_project_agreement = self.name
# 				sales_invoice.posting_date = getattr(service_row, "invoice_date", None)
# 				sales_invoice.set_posting_time = 1

# 				customer_doc = frappe.get_doc("Customer", service_row.contractor)
# 				company_doc = frappe.get_doc("Company", default_company)

# 				try:
# 					customer_currency = getattr(customer_doc, "default_currency", None)
# 					if customer_currency:
# 						sales_invoice.currency = customer_currency
# 						sales_invoice.price_list_currency = customer_currency
# 					else:
# 						sales_invoice.currency = company_doc.default_currency
# 						sales_invoice.price_list_currency = company_doc.default_currency
# 				except Exception:
# 					sales_invoice.currency = company_doc.default_currency
# 					sales_invoice.price_list_currency = company_doc.default_currency

# 				try:
# 					customer_price_list = getattr(customer_doc, "default_price_list", None)
# 					if customer_price_list:
# 						sales_invoice.selling_price_list = customer_price_list
# 				except Exception:
# 					pass

# 				try:
# 					if getattr(customer_doc, "payment_terms", None):
# 						sales_invoice.payment_terms_template = customer_doc.payment_terms
# 				except Exception:
# 					pass

# 				try:
# 					if getattr(customer_doc, "customer_group", None):
# 						sales_invoice.customer_group = customer_doc.customer_group
# 				except Exception:
# 					pass

# 				try:
# 					if getattr(customer_doc, "territory", None):
# 						sales_invoice.territory = customer_doc.territory
# 				except Exception:
# 					pass

# 				if getattr(self, "currency", None):
# 					sales_invoice.currency = self.currency
# 					sales_invoice.price_list_currency = self.currency
# 					company_currency = frappe.db.get_value("Company", default_company, "default_currency")
# 					if self.currency == company_currency:
# 						sales_invoice.conversion_rate = 1

# 				customer_receivable_account = None
# 				try:
# 					customer_receivable_account = frappe.db.get_value(
# 						"Party Account",
# 						{"parent": service_row.contractor, "parenttype": "Customer", "company": default_company},
# 						"account",
# 					)
# 				except Exception:
# 					pass
# 				if not customer_receivable_account:
# 					try:
# 						customer_receivable_account = frappe.db.get_value("Company", default_company, "default_receivable_account")
# 					except Exception:
# 						pass
# 				if not customer_receivable_account:
# 					try:
# 						customer_receivable_account = frappe.db.get_value(
# 							"Account", {"company": default_company, "account_type": "Receivable", "is_group": 0}, "name"
# 						)
# 					except Exception:
# 						pass
# 				if not customer_receivable_account:
# 					try:
# 						accounts = frappe.db.sql(
# 							"""
# 							SELECT name FROM `tabAccount`
# 							WHERE company = %s AND is_group = 0
# 							AND (name LIKE '%%Debtors%%' OR name LIKE '%%Receivable%%' OR name LIKE '%%Customer%%')
# 							LIMIT 1
# 							""",
# 							(default_company,),
# 						)
# 						if accounts:
# 							customer_receivable_account = accounts[0][0]
# 					except Exception:
# 						pass
# 				if customer_receivable_account:
# 					sales_invoice.debit_to = customer_receivable_account
# 				else:
# 					receivable_count = frappe.db.count(
# 						"Account", {"company": default_company, "account_type": "Receivable", "is_group": 0}
# 					)
# 					frappe.throw(
# 						f"No receivable account found for company {default_company}. Found {receivable_count} receivable accounts. Please check customer setup or create receivable accounts."
# 					)

# 				sales_invoice.ignore_pricing_rule = 1
# 				sales_invoice.conversion_rate = sales_invoice.conversion_rate or 1.0
# 				sales_invoice.plc_conversion_rate = sales_invoice.plc_conversion_rate or 1.0

# 				item_row = sales_invoice.append("items", {})
# 				item_row.item_code = getattr(service_row, "item", None)
# 				item_row.qty = 1
# 				item_row.rate = getattr(service_row, "amount", 0)
# 				item_row.uom = "Nos"

# 				if getattr(service_row, "remark", None):
# 					sales_invoice.remarks = service_row.remark

# 				if getattr(service_row, "tax_template", None):
# 					try:
# 						tax_template = frappe.get_doc("Sales Taxes and Charges Template", service_row.tax_template)
# 						template_company = tax_template.company
# 						if template_company and template_company != default_company:
# 							frappe.log_error(
# 								f"Tax template {service_row.tax_template} belongs to company {template_company} but invoice is for company {default_company}"
# 							)
# 							frappe.msgprint(
# 								f"Warning: Tax template {service_row.tax_template} belongs to different company. Skipping taxes."
# 							)
# 						else:
# 							sales_invoice.taxes_and_charges = service_row.tax_template
# 							valid_taxes = []
# 							for tax in tax_template.taxes:
# 								account_company = None
# 								try:
# 									account_company = frappe.db.get_value("Account", tax.account_head, "company")
# 								except Exception:
# 									account_company = None
# 								if account_company == default_company:
# 									valid_taxes.append({
# 										"charge_type": tax.charge_type,
# 										"account_head": tax.account_head,
# 										"description": tax.description,
# 										"rate": tax.rate,
# 										"tax_amount": tax.tax_amount if tax.charge_type == "Actual" else 0
# 									})
# 								elif account_company:
# 									frappe.log_error(
# 										f"Account {tax.account_head} belongs to company {account_company}, expected {default_company}"
# 									)
# 							for tax_data in valid_taxes:
# 								sales_invoice.append("taxes", tax_data)
# 					except Exception as e:
# 						frappe.log_error(f"Error applying tax template: {str(e)}")
# 						frappe.msgprint(
# 							f"Warning: Could not apply tax template {service_row.tax_template}. Invoice created without taxes."
# 						)

# 				if not getattr(sales_invoice, "debit_to", None):
# 					frappe.throw(
# 						f"Debit To account is required but not set for Sales Invoice. Customer: {service_row.contractor}, Company: {default_company}"
# 					)

# 				sales_invoice.run_method("set_missing_values")
# 				sales_invoice.save()
# 				sales_invoice.submit()

# 				total_tax_amount = 0
# 				if getattr(sales_invoice, "taxes", None):
# 					for tax_row in sales_invoice.taxes:
# 						total_tax_amount = total_tax_amount + (tax_row.tax_amount or 0)

# 				service_row.invoiced = 1
# 				service_row.reference_invoice = sales_invoice.name
# 				service_row.tax_amount = total_tax_amount
# 				invoices_created.append(sales_invoice.name)

# 		if invoices_created:
# 			for service_row in (self.contractors_services or []):
# 				if getattr(service_row, "invoiced", 0) and getattr(service_row, "reference_invoice", None):
# 					frappe.db.set_value(
# 						"Contractors Services",
# 						service_row.name,
# 						{
# 							"invoiced": service_row.invoiced,
# 							"reference_invoice": service_row.reference_invoice,
# 							"tax_amount": getattr(service_row, "tax_amount", 0) or 0,
# 						},
# 					)
# 			invoice_count = len(invoices_created)
# 			frappe.msgprint(f"Successfully created {invoice_count} Sales Invoice(s) for contractors")

# 	def _create_purchase_invoices_for_outsource_services(self) -> None:
# 		default_company = self._get_default_company()
# 		frappe.log_error(
# 			f"Using company: {default_company} for Project Agreement (Outsource): {self.name}",
# 			"Debug: Company Selection (Outsource Purchase)",
# 		)
# 		invoices_created = []
# 		for service_row in (self.outsource_services or []):
# 			if not getattr(service_row, "invoiced", 0):
# 				purchase_invoice = frappe.new_doc("Purchase Invoice")
# 				purchase_invoice.supplier = service_row.service_provider
# 				purchase_invoice.company = default_company
# 				purchase_invoice.custom_project_agreement = self.name
# 				purchase_invoice.posting_date = getattr(service_row, "date", None)
# 				purchase_invoice.set_posting_time = 1

# 				try:
# 					supplier_doc = frappe.get_doc("Supplier", service_row.service_provider)
# 				except Exception as e:
# 					frappe.throw(f"Supplier not found for outsource service row: {str(e)}")
# 				company_doc = frappe.get_doc("Company", default_company)

# 				try:
# 					supplier_currency = None
# 					try:
# 						supplier_currency = getattr(supplier_doc, "default_currency", None)
# 					except Exception:
# 						supplier_currency = None
# 					if supplier_currency:
# 						purchase_invoice.currency = supplier_currency
# 						purchase_invoice.price_list_currency = supplier_currency
# 					else:
# 						purchase_invoice.currency = company_doc.default_currency
# 						purchase_invoice.price_list_currency = company_doc.default_currency
# 				except Exception:
# 					purchase_invoice.currency = company_doc.default_currency
# 					purchase_invoice.price_list_currency = company_doc.default_currency

# 				try:
# 					supplier_price_list = None
# 					try:
# 						supplier_price_list = getattr(supplier_doc, "default_price_list", None)
# 					except Exception:
# 						supplier_price_list = None
# 					if supplier_price_list:
# 						purchase_invoice.buying_price_list = supplier_price_list
# 				except Exception:
# 					pass

# 				try:
# 					has_payment_terms = False
# 					try:
# 						has_payment_terms = bool(getattr(supplier_doc, "payment_terms", None))
# 					except Exception:
# 						has_payment_terms = False
# 					if has_payment_terms:
# 						purchase_invoice.payment_terms_template = supplier_doc.payment_terms
# 				except Exception:
# 					pass

# 				supplier_payable_account = None
# 				try:
# 					supplier_payable_account = frappe.db.get_value(
# 						"Party Account",
# 						{"parent": service_row.service_provider, "parenttype": "Supplier", "company": default_company},
# 						"account",
# 					)
# 				except Exception:
# 					pass
# 				if not supplier_payable_account:
# 					try:
# 						supplier_payable_account = frappe.db.get_value("Company", default_company, "default_payable_account")
# 					except Exception:
# 						pass
# 				if not supplier_payable_account:
# 					try:
# 						supplier_payable_account = frappe.db.get_value(
# 							"Account", {"company": default_company, "account_type": "Payable", "is_group": 0}, "name"
# 						)
# 					except Exception:
# 						pass
# 				if not supplier_payable_account:
# 					try:
# 						accounts = frappe.db.sql(
# 							"""
# 							SELECT name FROM `tabAccount`
# 							WHERE company = %s AND is_group = 0
# 							AND (name LIKE '%%Creditors%%' OR name LIKE '%%Payable%%' OR name LIKE '%%Supplier%%')
# 							LIMIT 1
# 							""",
# 							(default_company,),
# 						)
# 						if accounts:
# 							supplier_payable_account = accounts[0][0]
# 					except Exception:
# 						pass
# 				if supplier_payable_account:
# 					purchase_invoice.credit_to = supplier_payable_account
# 				else:
# 					payable_count = frappe.db.count("Account", {"company": default_company, "account_type": "Payable", "is_group": 0})
# 					frappe.throw(
# 						f"No payable account found for company {default_company}. Found {payable_count} payable accounts. Please check supplier setup or create payable accounts."
# 					)

# 				purchase_invoice.ignore_pricing_rule = 1
# 				purchase_invoice.conversion_rate = purchase_invoice.conversion_rate or 1.0
# 				purchase_invoice.plc_conversion_rate = purchase_invoice.plc_conversion_rate or 1.0

# 				item_row = purchase_invoice.append("items", {})
# 				item_row.item_code = getattr(service_row, "service", None)
# 				item_row.qty = 1
# 				item_row.rate = getattr(service_row, "amount", 0)
# 				item_row.uom = "Nos"

# 				try:
# 					if getattr(service_row, "remark", None):
# 						purchase_invoice.remarks = service_row.remark
# 				except Exception:
# 					pass

# 				has_tax_template = False
# 				try:
# 					has_tax_template = bool(getattr(service_row, "tax_template", None))
# 				except Exception:
# 					has_tax_template = False
# 				if has_tax_template:
# 					try:
# 						tax_template = frappe.get_doc("Purchase Taxes and Charges Template", service_row.tax_template)
# 						template_company = tax_template.company
# 						if template_company and template_company != default_company:
# 							frappe.log_error(
# 								f"Purchase tax template {service_row.tax_template} belongs to company {template_company} but invoice is for company {default_company}"
# 							)
# 							frappe.msgprint(
# 								f"Warning: Purchase tax template {service_row.tax_template} belongs to different company. Skipping taxes."
# 							)
# 						else:
# 							purchase_invoice.taxes_and_charges = service_row.tax_template
# 							valid_taxes = []
# 							for tax in tax_template.taxes:
# 								account_company = None
# 								try:
# 									account_company = frappe.db.get_value("Account", tax.account_head, "company")
# 								except Exception:
# 									account_company = None
# 								if account_company == default_company:
# 									valid_taxes.append(
# 										{
# 											"charge_type": tax.charge_type,
# 											"account_head": tax.account_head,
# 											"description": tax.description,
# 											"rate": tax.rate,
# 											"tax_amount": tax.tax_amount if tax.charge_type == "Actual" else 0,
# 										}
# 									)
# 								elif account_company:
# 									frappe.log_error(
# 										f"Account {tax.account_head} belongs to company {account_company}, expected {default_company}"
# 									)
# 							for tax_data in valid_taxes:
# 								purchase_invoice.append("taxes", tax_data)

# 					except Exception as e:
# 						frappe.log_error(f"Error applying purchase tax template: {str(e)}")
# 						frappe.msgprint(
# 							f"Warning: Could not apply purchase tax template {service_row.tax_template}. Invoice created without taxes."
# 						)

# 				if not getattr(purchase_invoice, "credit_to", None):
# 					frappe.throw(
# 						f"Payable account (credit_to) is required but not set for Purchase Invoice. Supplier: {service_row.service_provider}, Company: {default_company}"
# 					)

# 				purchase_invoice.run_method("set_missing_values")
# 				purchase_invoice.save()
# 				purchase_invoice.submit()

# 				service_row.invoiced = 1
# 				service_row.reference_invoice = purchase_invoice.name
# 				try:
# 					service_row.tax_amount = purchase_invoice.total_taxes_and_charges or 0
# 				except Exception:
# 					service_row.tax_amount = 0
# 				invoices_created.append(purchase_invoice.name)

# 		if invoices_created:
# 			for service_row in (self.outsource_services or []):
# 				try:
# 					has_ref = bool(getattr(service_row, "reference_invoice", None))
# 				except Exception:
# 					has_ref = False
# 				if getattr(service_row, "invoiced", 0) and has_ref:
# 					try:
# 						frappe.db.set_value(
# 							"Outsource Services",
# 							service_row.name,
# 							{
# 								"invoiced": service_row.invoiced,
# 								"reference_invoice": service_row.reference_invoice,
# 								"tax_amount": getattr(service_row, "tax_amount", 0),
# 							},
# 						)
# 					except Exception:
# 						pass
# 			invoice_count = str(len(invoices_created))
# 			frappe.msgprint("Successfully created " + invoice_count + " Purchase Invoice(s) for Outsource Services")
