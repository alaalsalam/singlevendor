# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GeneralSettings(Document):
	def validate(self):
		if self.cancel_order:
			min_cancel_time = int(self.driver_time) * int(self.maximum_notifications_to_driver)
			if self.cancel_after < min_cancel_time:
				message = frappe._('You cannot cancel order within {0} seconds'.format(
																						min_cancel_time
																					))
				frappe.throw(message)
