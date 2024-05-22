# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridots Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from ecommerce_business_store_singlevendor.utils.setup import get_settings_from_domain

class MembershipPayment(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		naming_series = 'M-.YY.-'
		self.name = make_autoname(naming_series+'.#####', doc=self)

	def validate(self):
		if not self.business:
			default_business = frappe.db.get_all('Business')
			if default_business:
				self.business = default_business[0].name
		if not self.remarks:
			self.remarks = 'Membership Payment of {0}'.format(self.member)
		self.validate_membership_period()

	def validate_membership_period(self):
		if self.from_date and self.to_date:
			check_records = frappe.db.sql('''select name from `tabMembership Payment` where ((from_date between %(start_date)s and %(end_date)s) or (to_date between %(start_date)s and %(end_date)s)) and member = %(member)s and name <> %(name)s and docstatus = 1''', {'start_date': self.from_date, 'end_date': self.to_date, 'member': self.member, 'name': self.name})
			if check_records:
				frappe.throw(frappe._('Membership already exists for the selected period.'))

	def on_submit(self):
		if self.paid:
			self.make_payment()

	def make_payment(self):
		pay = get_payment_args(self.name)
		pay.flags.ignore_permissions = True
		pay.submit()
		frappe.db.set_value("Member", self.member, "active", 1)
		frappe.db.set_value("Member", self.member, "membership_type", self.membership_type)

@frappe.whitelist()
def get_payment_args(source_name, as_dict=None):
	doc = frappe.get_doc('Membership Payment', source_name)
	settings = get_settings_from_domain('Catalog Settings', business=doc.business)
	pay = frappe.new_doc('Payment Entry')
	pay.payment_type = 'Receive'
	pay.business = doc.business
	pay.posting_date = nowdate()
	pay.mode_of_payment = doc.mode_of_payment
	pay.party_type = 'Member'
	pay.party = doc.member
	pay.paid_amount = doc.amount
	pay.base_paid_amount = doc.amount
	pay.received_amount = doc.amount
	pay.allocate_payment_amount = 1
	if doc.mode_of_payment:
		pay.mode_of_payment = doc.mode_of_payment
	if doc.reference:
		pay.reference_no = doc.reference
	pay.remarks = 'Amount {0} {1} received from {2}'.format(settings.default_currency, doc.amount, pay.party)
	pay.append('references', {
		'reference_doctype': 'Membership Payment',
		'reference_name': doc.name,
		'bill_no': '',
		'due_date': nowdate(),
		'total_amount': doc.amount,
		'outstanding_amount': 0,
		'allocated_amount': doc.amount
		})
	if as_dict:
		return pay.__dict__
	return pay
