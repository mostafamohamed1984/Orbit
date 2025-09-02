// // Copyright (c) 2025, Smart Vision Group and contributors
// // For license information, please see license.txt

// // Fetch Accounts and filter
// frappe.ui.form.on('Project Payment', {
// 	setup: function(frm) {
// 		// Filter Mode of Payment based on company linked to user
// 		frm.set_query("mode_of_payment", function() {
// 			return {
// 				filters: {
// 					company: frappe.defaults.get_user_default('company')
// 				}
// 			};
// 		});
		
// 		// Filter Customer based on custom_company field
// 		frm.set_query("customer", function() {
// 			return {
// 				filters: {
// 					custom_company: frappe.defaults.get_user_default('company')
// 				}
// 			};
// 		});
		
// 		// Filter Tax Account based on company
// 		frm.set_query("tax_account", function() {
// 			return {
// 				filters: {
// 					company: frappe.defaults.get_user_default('company'),
// 					is_group: 0,
// 					account_type: "Tax"
// 				}
// 			};
// 		});
		
// 		// Filter Party Account based on company
// 		frm.set_query("party_account", function() {
// 			return {
// 				filters: {
// 					company: frappe.defaults.get_user_default('company'),
// 					is_group: 0
// 				}
// 			};
// 		});
		
// 		// Filter Advance Account based on company
// 		frm.set_query("advance_account", function() {
// 			return {
// 				filters: {
// 					company: frappe.defaults.get_user_default('company'),
// 					is_group: 0
// 				}
// 			};
// 		});
// 	},
	
// 	customer: function(frm) {
// 		if (frm.doc.customer) {
// 			// Fetch Customer's accounts to get default account and advance account
// 			frappe.call({
// 				method: 'frappe.client.get',
// 				args: {
// 					doctype: 'Customer',
// 					name: frm.doc.customer
// 				},
// 				callback: function(r) {
// 					if (r.message && r.message.accounts && r.message.accounts.length > 0) {
// 						const company = frappe.defaults.get_user_default('company');
						
// 						// Find the account entry for the current company
// 						const company_account = r.message.accounts.find(acc => acc.company === company);
						
// 						if (company_account) {
// 							// Set party account (default receivable account)
// 							if (company_account.account) {
// 								frm.set_value('party_account', company_account.account);
// 							}
							
// 							// Set advance account if available
// 							if (company_account.advance_account) {
// 								frm.set_value('advance_account', company_account.advance_account);
// 							}
// 						}
// 					}
					
// 					// If no accounts found in customer accounts table, try to get default receivable account
// 					if (!frm.doc.party_account) {
// 						frappe.call({
// 							method: 'erpnext.accounts.party.get_party_account',
// 							args: {
// 								party_type: 'Customer',
// 								party: frm.doc.customer,
// 								company: frappe.defaults.get_user_default('company')
// 							},
// 							callback: function(account_response) {
// 								if (account_response.message) {
// 									frm.set_value('party_account', account_response.message);
// 								}
// 							}
// 						});
// 					}
// 				}
// 			});
// 		} else {
// 			// Clear accounts when customer is cleared
// 			frm.set_value('party_account', '');
// 			frm.set_value('advance_account', '');
// 		}
// 	},
	
// 	mode_of_payment: function(frm) {
// 		if (frm.doc.mode_of_payment) {
// 			// Fetch the Mode of Payment's accounts table
// 			frappe.call({
// 				method: 'frappe.client.get',
// 				args: {
// 					doctype: 'Mode of Payment',
// 					name: frm.doc.mode_of_payment
// 				},
// 				callback: function(r) {
// 					if (r.message && r.message.accounts && r.message.accounts.length > 0) {
// 						const company = frappe.defaults.get_user_default('company');
						
// 						// Find the account entry for the current company
// 						const company_account = r.message.accounts.find(acc => acc.company === company);
						
// 						if (company_account && company_account.default_account) {
// 							frm.set_value('receiving_account', company_account.default_account);
// 						} else if (r.message.accounts[0].default_account) {
// 							// Fallback to first account if company-specific account not found
// 							frm.set_value('receiving_account', r.message.accounts[0].default_account);
// 						}
// 					}
// 				}
// 			});
			
// 			// Clear fields based on mode of payment change
// 			if (frm.doc.mode_of_payment !== 'Bank Transfer Orbit (AED)') {
// 				frm.set_value('reference_number', '');
// 			}
			
// 			if (frm.doc.mode_of_payment !== 'Cheque') {
// 				frm.set_value('due_date', '');
// 				frm.set_value('cheque_number', '');
// 				frm.set_value('bank_name', '');
// 			}
			
// 			if (frm.doc.mode_of_payment !== 'Visa') {
// 				frm.set_value('visa_number', '');
// 			}
// 		}
// 	},
	
// 	visa_number: function(frm) {
// 		if (frm.doc.visa_number) {
// 			// Validate Visa number - must be exactly 14 digits
// 			const visaNumber = frm.doc.visa_number.toString().trim();
// 			if (!/^\d{14}$/.test(visaNumber)) {
// 				frappe.msgprint(__('Visa Number must be exactly 14 digits'));
// 				frm.set_value('visa_number', '');
// 			}
// 		}
// 	},
	
// 	// Optional: Refresh accounts when company changes (if company field exists)
// 	company: function(frm) {
// 		if (frm.doc.customer) {
// 			// Re-trigger customer function to update accounts for new company
// 			frm.trigger('customer');
// 		}
// 		if (frm.doc.mode_of_payment) {
// 			// Re-trigger mode_of_payment function to update receiving account
// 			frm.trigger('mode_of_payment');
// 		}
// 	}
// });

// // Totals calculation
// frappe.ui.form.on('Project Payment', {
// 	refresh: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	validate: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	onload: function(frm) {
// 		calculate_totals(frm);
// 	}
// });

// frappe.ui.form.on('Service Payment Details', {
// 	service_payment_details_add: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	service_payment_details_remove: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	payment_amount: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	payment_tax: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	total: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	total_taxes: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	outstanding: function(frm) {
// 		calculate_totals(frm);
// 	}
// });

// frappe.ui.form.on('Government Fees Payment', {
// 	government_fees_add: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	government_fees_remove: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	amount: function(frm) {
// 		calculate_totals(frm);
// 	}
// });

// frappe.ui.form.on('Trust Fees Payment', {
// 	trust_fees_payment_add: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	trust_fees_payment_remove: function(frm) {
// 		calculate_totals(frm);
// 	},
// 	amount: function(frm) {
// 		calculate_totals(frm);
// 	}
// });

// function calculate_totals(frm) {
// 	if (!frm.doc) return;
// 	let total_government_fees = 0;
// 	let total_trust_fees = 0;
// 	let total_services = 0;
// 	let tax_amount = 0;
// 	let outstanding_amount = 0;
// 	let service_total_amount = 0;
// 	let service_total_taxes = 0;

// 	if (frm.doc.service_payment_details) {
// 		frm.doc.service_payment_details.forEach(function(row) {
// 			if (row.payment_amount) total_services += flt(row.payment_amount);
// 			if (row.payment_tax) tax_amount += flt(row.payment_tax);
// 			if (row.outstanding) outstanding_amount += flt(row.outstanding);
// 			if (row.total) service_total_amount += flt(row.total);
// 			if (row.total_taxes) service_total_taxes += flt(row.total_taxes);
// 		});
// 	}

// 	if (frm.doc.government_fees) {
// 		frm.doc.government_fees.forEach(function(row) {
// 			if (row.amount) total_government_fees += flt(row.amount);
// 		});
// 	}

// 	if (frm.doc.trust_fees_payment) {
// 		frm.doc.trust_fees_payment.forEach(function(row) {
// 			if (row.amount) total_trust_fees += flt(row.amount);
// 		});
// 	}

// 	let claim_amount = total_government_fees + total_services + total_trust_fees + tax_amount;
// 	let paid_amount = (service_total_amount + service_total_taxes) - outstanding_amount + total_services + tax_amount;

// 	frm.set_value('total_government_fees', total_government_fees);
// 	frm.set_value('total_trust_fees', total_trust_fees);
// 	frm.set_value('total_services', total_services);
// 	frm.set_value('tax_amount', tax_amount);
// 	frm.set_value('paid_amount', paid_amount);
// 	frm.set_value('outstanding_amount', outstanding_amount);
// 	frm.set_value('claim_amount', claim_amount);

// 	frm.refresh_fields([
// 		'total_government_fees',
// 		'total_trust_fees',
// 		'total_services',
// 		'tax_amount',
// 		'paid_amount',
// 		'outstanding_amount',
// 		'claim_amount'
// 	]);
// }

// function flt(value, precision = 2) {
// 	if (value == null || value == undefined || value === '') {
// 		return 0.0;
// 	}
// 	if (typeof value === 'string') {
// 		value = parseFloat(value);
// 	}
// 	return Math.round(value * Math.pow(10, precision)) / Math.pow(10, precision);
// }
