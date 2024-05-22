# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class EmailTemplate(Document):
	def on_update(self):		
		email_template = frappe.db.get_all('Notification', filters = {'name':self.name})
		if email_template:
			template = frappe.get_doc('Notification', email_template[0].name)
			if template.subject != self.subject:
				frappe.db.set_value('Notification', template.name,'subject', self.subject)
			if template.message != self.body:
				frappe.db.set_value('Notification', template.name,'message', self.body)	
	