# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class SMSTemplates(Document):
	pass

def get_phone_number(doc):
	query=''
	numbers=[]
	if doc.doctype=="Customers":
		query = '''	SELECT phone AS value 
					FROM `tabCustomers` 
					WHERE name="{name}"
				'''.format(name=doc.name)
	elif doc.doctype=="Business Registration":
		query = ''' SELECT business_phone AS value 
					FROM `tabBusiness Registration` 
					WHERE name="{name}"
				'''.format(name=doc.name)
	elif doc.doctype=="Order":
		if doc.customer:
			query = '''	SELECT phone AS value 
						FROM `tabCustomers` 
						WHERE name="{name}"
					'''.format(name=doc.customer)
	elif doc.doctype=="Vendor Orders":
		if doc.business:
			query = ''' SELECT (SELECT
									business_phone 
								FROM `tabBusiness` 
								WHERE name="{name}") AS value,
								(SELECT phone 
								FROM `tabCustomers` 
								WHERE name="{name1}") AS customer
					'''.format(name=doc.business, name1=doc.customer)
	if query:
		number = frappe.db.sql(query,as_dict=True)
		if number and number[0].value:
			numbers.append(number[0].value)
		if number and number[0].customer:
			numbers.append(number[0].customer)
		return numbers
	return None