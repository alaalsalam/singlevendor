# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.orders \
    import get_today_date

class OrderDelivery(Document):
	def validate(self):
		if self.driver_allocation_count == 0:
			self.driver_allocation_count = 1
			self.reschedule_time = get_today_date(replace=True)

@frappe.whitelist()
def check_for_notification(name):
	if frappe.db.get_value('Order Delivery',name):
		delivery = frappe.get_doc('Order Delivery',name)
		if delivery.driver_assigned:
			driver_seconds = frappe.db.get_single_value('General Settings','driver_time')
			return {
					'status':'Success'
				}
		return {
				'status':'Failed'
			}
	else:
		return {
				'status':'Success'
			}