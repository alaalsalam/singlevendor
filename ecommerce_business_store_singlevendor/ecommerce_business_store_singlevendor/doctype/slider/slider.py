# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class Slider(Document):
	def on_update(self):
		if self.name:
			data = frappe.db.sql("""SELECT P.name 
									FROM `tabWeb Page Builder` P 
									INNER JOIN `tabMobile Page Section` PS ON PS.parent = P.name 
									INNER JOIN `tabPage Section` S ON S.name = PS.section 
									WHERE S.section_type = "Slider" 
									GROUP BY P.name
								""", as_dict=True)
			for item in data:
				page = frappe.get_doc('Web Page Builder',item.name)
				page.save(ignore_permissions=True)