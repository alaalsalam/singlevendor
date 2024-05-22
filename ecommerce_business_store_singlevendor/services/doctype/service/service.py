# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from datetime import date
from frappe.model.document import Document

class Service(Document):
	def autoname(self):
		if self.business:
			abbr = frappe.db.get_value('Business', self.business, 'abbr')
			from frappe.model.naming import make_autoname
			self.name = make_autoname('{0}-{1}-.#####'.format('SR', abbr), doc = self)

	def validate(self):
		if self.get('time_slot'):
			business_info = frappe.get_doc('Business',self.business)
			today_date = date.today()
			for n in self.get('time_slot'):
				check_status = list(filter(lambda x: x.day==n.day, business_info.opening_hour))
				if check_status:
					for item in check_status:
						if item.status == 'Closed':
							frappe.throw(frappe._('Business closed for {0}'.format(item.day)))
				else:					
					frappe.throw(frappe._('Business timing is not mentioned for {0}'.format(n.day)))