# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe, json
from frappe import _
from ecommerce_business_store_singlevendor.utils.setup import get_settings_from_domain, get_theme_settings
from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.business_payment_gateway_settings.business_payment_gateway_settings import get_available_payments

@frappe.whitelist()
def get_shipping_details():
	business = get_vendor_business()
	condition = ''
	if business:
		condition = ' where business = "{0}"'.format(business)
	shipping_methods = frappe.db.sql('''select s.name, s.shipping_method_name, s.is_deliverable, 
		s.display_order, s.show_in_website, s.description, s.business, b.restaurant_name as business_name 
		from `tabShipping Method` s left join `tabBusiness` b on b.name = s.business
		{condition} order by s.business, s.display_order'''.format(condition=condition), as_dict=1)
	shipping_rate_methods = frappe.db.sql('''select name, shipping_rate_method, is_active from `tabShipping Rate Method` {0}'''.format(condition), as_dict=1)
	return {'shipping_methods': shipping_methods, 'shipping_rate_methods': shipping_rate_methods}

@frappe.whitelist()
def get_payment_details(business=None):
	if not business:
		business = get_vendor_business()
	condition = ''
	if business:
		condition = ' where business = "{0}"'.format(business)
	available_methods = get_available_payments()
	pay_options = {}
	for item in available_methods:
		if item.get('dt'):
			pay_options[item.get('dt')] = frappe.get_single(item.get('dt'))
	payment_methods = frappe.db.sql('''select p.*, b.restaurant_name as business_name 
		from `tabBusiness Payment Gateway Settings` p left join `tabBusiness` b on b.name = p.business 
		{0}'''.format(condition), as_dict=1)
	return {'available_methods': available_methods, 'payment_methods': payment_methods, 'pay_options': pay_options}

def get_vendor_business():
	business = None
	if frappe.session.user != "Administrator" and "Vendor" in frappe.get_roles(frappe.session.user):
		if not frappe.db.get_value('Shop User', frappe.session.user):
			frappe.throw(_("You are not allowed to view this page"), frappe.PermissionError)
		business = frappe.db.get_value('Shop User', frappe.session.user, 'restaurant')
	return business

@frappe.whitelist()
def send_razorpay_submerchant_email(business_name, email, sender, website):
	template = 'submerchant_registration'
	args = {
		'account_name': business_name,
		'email': email,
		'website': website
	}
	reciepients = [sender]
	subject = frappe._('New request for Razorpay submerchant registration')
	frappe.sendmail(reciepients, subject=subject, template=template, args=args)
	return {'status': 'success'}
