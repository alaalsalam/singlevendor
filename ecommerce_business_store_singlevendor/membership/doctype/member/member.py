# -*- coding: utf-8 -*-
# Copyright (c) 2020, valiantsystems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate,nowdate,now
import datetime
from ecommerce_business_store_singlevendor.utils.setup import get_settings_from_domain
from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.orders \
    import get_today_date
from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.\
    customers.customers import update_password

class Member(Document):
	def autoname(self):
		from frappe.model.naming import make_autoname
		self.name = make_autoname(self.naming_series+'.#####', doc=self)

	def onload(self):
		settings = get_settings_from_domain('Membership Settings')
		if settings.enable_expiry and self.membership_expiry_date:
			newdate1 = getdate(get_today_date(replace=True))
			newdate2 = getdate(self.membership_expiry_date)
			if newdate1 > newdate2:
				frappe.msgprint(frappe._("Membership is Expired!").format())

	def validate(self):
		self.member_name = self.first_name
		if self.middle_name:
			self.member_name = self.member_name + ' ' + self.middle_name
		if self.last_name:
			self.member_name = self.member_name + ' ' + self.last_name
		if self.email:
			self.validate_email_type(self.email)
		if self.email:
			email = self.email
			Emember=frappe.db.sql('''select * from `tabMember` where email=%(email)s and name!=%(name)s''',{'email':email,'name':self.name})
			if Emember:
				frappe.throw(_("{0} is already a member!").format(self.email))
		if self.associated_member:
			for mem in self.associated_member:
				mem.member_name = mem.first_name
				if mem.middle_name:
					mem.member_name = mem.member_name + ' ' + mem.middle_name
				if mem.last_name:
					mem.member_name = mem.member_name + ' ' + mem.last_name
				if mem.email:
					self.validate_email_type(mem.email)

	def validate_email_type(self, email):
		from frappe.utils import validate_email_address
		validate_email_address(email.strip(), True)

	def on_update(self):
		if self.email:
			self.add_user(self.email, self.user)
		if self.associated_member:
			for item in self.associated_member:
				if item.email:
					self.add_user(item.email, item.user, 1, item)

	def add_user(self, email, user=None, is_child=0, child_doc=None):
		if user:
			user = frappe.get_doc('User', user)			
		elif email:
			email = email
			check_user = frappe.db.get_all('User', filters={'name': email})
			if check_user:
				user = frappe.get_doc('User', email)
			else:
				user = frappe.new_doc('User')
				user.send_welcome_email = 0
				from frappe.utils import random_string
				user.reset_password_key = random_string(32)
				user.simultaneous_sessions = 4
				user.email = email
		user.first_name = self.first_name if not is_child else child_doc.first_name
		user.middle_name = self.middle_name if not is_child else child_doc.middle_name
		user.last_name = self.last_name if not is_child else child_doc.last_name
		user.username = self.name if not is_child else child_doc.name
		user.gender = self.gender if not is_child else child_doc.gender
		user.mobile_no = self.mobile_no if not is_child else child_doc.phone_no
		user.save(ignore_permissions=True)
		if not is_child and not self.user:
			frappe.db.set_value('Member', self.name, 'user', user.name)
		if is_child and not child_doc.user:
			frappe.db.set_value('Associated Member', child_doc.name, 'user', user.name)
		insert_role = True
		role = 'Member'
		if is_child and child_doc.relation:
			role = frappe.db.get_value('Relation', child_doc.relation, 'role')
		if user.roles:
			check_role = frappe.db.get_all('Has Role', filters={'role': role, 'parent': user.name})
			if check_role:
				insert_role = False
		if insert_role:
			frappe.get_doc({
				"doctype": "Has Role",
				"name": nowdate(),
				"parent": user.name,
				"parentfield": "roles",
				"parenttype": "User",
				"role": role
				}).insert()
		if user and self.set_password:
			update_password(self.set_password, old_password=None, user=user.name)
			frappe.db.set_value('Member', self.name, 'set_password', '')

	def on_payment_authorized(self,payment_status):
		if payment_status in ["Authorized", "Completed"]:
			frappe.db.set_value('Member', self.name, 'active', 1)
			payment=frappe.db.get_all('Membership Payment',filters={'member':self.name})
			if not payment:
				doc = frappe.get_doc({
					"doctype":"Membership Payment",
					"member":self.name,
					"amount":self.membership_amount,
					"to_date":self.membership_expiry_date,
					"paid":1,
					"membership_type":self.membership_type,
					"member_since_date":datetime.date.today(),
					"membership_status":"New"
					})
				doc.docstatus = 1
				doc.save(ignore_permissions=True)
				redirect_to = "/thankyou?id="+self.name
				return redirect_to


@frappe.whitelist()
def get_newsletter_based_email(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql('''select name, title, category from `tabEmail Group`''')

@frappe.whitelist()
def get_temple_based_email(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql('''select name, title, category from `tabEmail Group`''')

