from __future__ import unicode_literals
# import frappe
# from _future_ import unicode_literals
import frappe
import frappe.utils
import json
import calendar
from frappe import _
from frappe.utils import getdate,nowdate
from datetime import date
from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api import getProductCategories,getCustomerList,getAllProducts,getAllProductsTitle
from ecommerce_business_store_singlevendor.sale.api import get_productlist_scroll
from frappe.core.doctype.domain_settings.domain_settings import get_active_domains
from ecommerce_business_store_singlevendor.utils.setup import get_settings_from_domain

def get_context(context):
	user = frappe.session.user 
	context.pos_settings=check_PosSettings()
	context.modeof_pay=get_modeof_pay()
	context.return_reason=get_return_reason()
	if "System Manager" in frappe.get_roles(user):
		business=""
		context.categories=getProductCategories(business)
		context.customers=getCustomerList()
		context.allproducts=getAllProducts()
		context.order_settings=check_OrderSettings()
		context.csrf_token=frappe.local.session.data.csrf_token if frappe.local.session.data.csrf_token else ''
		
		context.domains_list=get_active_domains()
	elif "Super Admin" in frappe.get_roles(user):
		business=""
		context.categories=getProductCategories(business)
		context.customers=getCustomerList()
		context.allproducts=get_productlist_scroll(page_no=1,page_len=10)
		context.order_settings=check_OrderSettings()
		context.csrf_token=frappe.local.session.data.csrf_token if frappe.local.session.data.csrf_token else ''
		context.domains_list=get_active_domains()
	else:
		frappe.throw(frappe._('You need to be logged in to access this page'), frappe.PermissionError)

@frappe.whitelist(allow_guest=True)
def check_OrderSettings():
	Order_settings = get_settings_from_domain("Order Settings")
	if Order_settings:
		return Order_settings

@frappe.whitelist(allow_guest=True)
def check_PosSettings():
	Pos_Settings = frappe.get_doc("POS Settings","POS Settings")
	if Pos_Settings:
		if (Pos_Settings.enable_pos == 0):
			frappe.throw(frappe._('You dont have enough permission to access this page'), frappe.DoesNotExistError)
		return Pos_Settings

@frappe.whitelist(allow_guest=True)
def get_user_details(user):
	return frappe.db.get_all('Shop User',filters={'name':user},fields=['restaurant'])

@frappe.whitelist(allow_guest=True)
def get_modeof_pay():
	return frappe.db.get_all('Mode Of Payments',fields=['name'])

@frappe.whitelist(allow_guest=True)
def get_return_reason():
	return frappe.db.get_all('Return Request Reasons',fields=['name'])