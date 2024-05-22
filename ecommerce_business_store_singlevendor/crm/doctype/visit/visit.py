# Copyright (c) 2023, Tridots Tech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
from ecommerce_business_store_singlevendor.utils.setup import get_settings

class Visit(Document):
	def validate(self):
		if self.cus_type=="Customer":
			self.reference_id = self.customer_id
		if self.cus_type=="Lead":
			self.reference_id = self.lead_id
		if self.business_phone and len(str(self.business_phone)) > 0:
			self.validate_phone()

	def on_update(self):
		if self.cus_type=="Customer":
			self.reference_id = self.customer_id
		if self.cus_type=="Lead":
			self.reference_id = self.lead_id
		frappe.db.set_value("Visit",self.name,"reference_id",self.reference_id)
		p_list = ""
		if self.purpose_of_visits:
			for p in self.purpose_of_visits:
				if frappe.db.get_value("Visit of Purpose",p.name_of_purpose,"vis_of_purps"):
					p_list += frappe.db.get_value("Visit of Purpose",p.name_of_purpose,"vis_of_purps")+","
		if p_list:
			p_list = p_list.rstrip(',')
		self.purpose_of_visit_list = p_list
		frappe.db.set_value(self.doctype,self.name,"purpose_of_visit_list",p_list)
		frappe.db.commit()

	def validate_phone(self):
		if not str(self.business_phone).isnumeric():
			frappe.throw(frappe._('Business Phone Number must contain only numbers'))
		order_settings = get_settings('Order Settings')
		import re
		res = re.search('(?=.*\d)[\d]', str(self.business_phone))
		if not res:
			frappe.throw(frappe._('Business Phone number must contain only numbers'))
		if order_settings.enable_phone_validation:
			if len(str(self.business_phone)) < int(order_settings.min_phone_length):
				frappe.throw(frappe._('Business Phone number should be minimum of {0} digits').format(order_settings.min_phone_length))
			if len(str(self.business_phone)) > int(order_settings.max_phone_length):
				frappe.throw(frappe._('Business Phone number should be maximum of {0} digits').format(order_settings.max_phone_length))

@frappe.whitelist()
def purpose_of_visits(purpose_of_visits):
	purposes = ''
	if len(json.loads(purpose_of_visits))>0:
		for x in json.loads(purpose_of_visits):
			purposes += "'"+x.get("name_of_purpose")+"',"
		purposes = purposes[:-1]
		query = """ SELECT vis_of_purps
					FROM `tabVisit of Purpose`
					WHERE name IN({name_list})
				""".format(name_list=purposes)
		return frappe.db.sql(query,as_dict=1)
	return []
