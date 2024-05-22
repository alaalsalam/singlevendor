# -*- coding: utf-8 -*-
# Copyright (c) 2019, sivaranjani and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import flt, nowdate, money_in_words
from frappe.utils import flt, nowdate
from ecommerce_business_store_singlevendor.utils.setup import get_settings_value

class Invoice(Document):
	def validate(self):
		if self.items:
			total_amount = 0
			for lit in self.items:
				total_amount += flt(lit.amount)
			self.total=total_amount
			self.net_total=total_amount	
		else:
			frappe.throw('Please add item details')
		for d in self.items:
				if hasattr(d, 'quantity') and d.quantity < 0 and not self.get('is_return'):
					frappe.throw(_("For an item {0}, quantity must be positive number").format(d.product))

				if hasattr(d, 'quantity') and d.quantity > 0 and self.get('is_return'):
					frappe.throw(_("For an item {0}, quantity must be negative number").format(d.product))
		if self.taxes and self.net_total:
			taxamount=0
			for txt in self.taxes:
				taxamount += flt(txt.amount)
			totaltax_amount=self.net_total+taxamount
			self.taxes_and_charges_added=taxamount
			self.total_taxes_and_charges=taxamount
			self.grand_total=totaltax_amount
			self.base_grand_total=totaltax_amount
		else:
			self.taxes_and_charges_added=0
			self.total_taxes_and_charges=0
			self.grand_total=self.net_total
			self.base_grand_total=self.net_total
		if self.grand_total:
			self.outstanding_amount=self.grand_total
		if self.docstatus==0:
			self.status="Draft"
		if self.docstatus==1:
			self.status="Submitted"
		if self.docstatus==2:
			self.status="Cancelled"
		if self.currency:
			self.in_words=money_in_words(self.grand_total, main_currency = self.currency)


@frappe.whitelist()
def make_payment(source_name, target_doc=None):
	default_currency=get_settings_value("Catalog Settings","default_currency")
	source=frappe.db.get_list("Invoice",fields=["*"],filters={"name":source_name})[0]
	account_settings=frappe.get_single('Core Settings')
	if flt(source.outstanding_amount)>0:
		total=source.outstanding_amount
	else:
		total=source.grand_total
	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Pay"
	pe.restaurant = source.restaurant
	pe.posting_date = nowdate()
	pe.mode_of_payment = ""
	pe.party_type = source.party_type
	pe.party = source.party
	pe.party_name = source.party_name
	pe.contact_person = ""
	pe.contact_email = ""
	pe.paid_from = account_settings.paid_from_account
	pe.paid_to = account_settings.paid_to_account
	pe.paid_from_account_currency = default_currency
	pe.paid_to_account_currency = default_currency
	if source.is_return==0:
		pe.paid_amount = total
		pe.base_paid_amount = total
		pe.received_amount = total
	else:
		pe.paid_amount = (total)*-1
		pe.base_paid_amount = (total)*-1
		pe.received_amount = (total)*-1
	pe.allocate_payment_amount = 1
	pe.append("references", {
		'reference_doctype': "Invoice",
		'reference_name': source.name,
		"bill_no": "",
		"due_date": "",
		'total_amount': total,
		'outstanding_amount': 0,
		'allocated_amount': total
	})
	return pe