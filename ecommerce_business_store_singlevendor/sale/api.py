
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import datetime
from pyqrcode import create as qrcreate
from six import BytesIO
from datetime import date, datetime, time
from frappe.utils import getdate, add_months, add_to_date, nowdate, today, now
from frappe.utils import get_url, get_datetime, time_diff_in_seconds
from frappe.utils import flt, cstr,getdate,nowdate,today,encode,cint
import frappe.client
import json

@frappe.whitelist(allow_guest=True)
def get_all_products(page_no,page_size):
	try:
		products = frappe.db.sql('''select * from `tabProduct` where is_active=1 limit %d,%d''',(int(page_no)-1)*int(page_size),int(page_size),as_dict=1)
		if products:
			for i in products:
				i.images = frappe.db.get_all('Product Image',fields=["*"],filters={"parent": i.name})
				Addons = frappe.db.get_all('Product Attribute Mapping',fields=["*"],filters={"parent":i.name})
				if Addons:
					for j in Addons:
						j.options = frappe.db.get_all('Product Attribute Option',fields=["*"],filters={"parent":i.name,"attribute":j.product_attribute})
					i.addons = Addons
		return products
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_sorted_brand_products") 	

@frappe.whitelist(allow_guest=True)
def get_productlist_scroll(page_no,page_len,condition=None):
	conditions=''
	if condition:
		conditions=conditions
	limit_start=str(((int(page_no)-1)*int(page_len)))
	products=frappe.db.sql('''select * from `tabProduct` where is_active=1 {condition} order by stock desc limit {limit_start},{limit_page_length}'''.format(condition=conditions,limit_start=limit_start,limit_page_length=page_len),as_dict=1)
	if products:
		for i in products:
			i.images = frappe.db.get_all('Product Image',fields=["*"],filters={"parent": i.name})
			Addons = frappe.db.get_all('Product Attribute Mapping',fields=["*"],filters={"parent":i.name})
			if Addons:
				for j in Addons:
					j.options = frappe.db.get_all('Product Attribute Option',fields=["*"],filters={"parent":i.name,"attribute":j.product_attribute})
				i.addons = Addons
	return products

@frappe.whitelist(allow_guest=True)
def insert_ReturnRequest(order_id,product,quantity,reason,comments,customer):
	now=getdate(nowdate())
	result=frappe.get_doc({
		"doctype":"Return Request",
		"order_id":order_id,
		"product":product,
		"customer":customer,
		"quantity":quantity,
		"status": "Pending",
		"reason_for_return":reason,
		"admin_comments":comments
		}).insert()
	if result:
		return "success"
	else:
		return "failed"