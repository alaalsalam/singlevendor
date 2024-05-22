# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe, json
from frappe import _
from ecommerce_business_store_singlevendor.utils.setup import get_settings_from_domain, get_theme_settings

@frappe.whitelist()
def get_page_details(website):
	out = {}
	out['catalog_settings'] = get_settings_from_domain('Catalog Settings', domain=website)
	theme = get_theme_settings(domain=website)
	if theme:
		out['theme_settings'] = frappe.get_doc('Web Theme', theme)
	check_website = frappe.db.sql('''select home_page, business from `tabWebsite` where domain_name = %(domain)s or concat("www.", domain_name) = %(domain)s''', {'domain': website}, as_dict=1)
	home_page, business = None, None
	if check_website:
		home_page = check_website[0].home_page
		business = check_website[0].business
	filters = {'is_published': 1, 'business': ''}
	if business:
		filters['business'] = business
	pages_list = frappe.db.get_all('Pages', filters=filters, fields=['name', 'page_title', 'route'])
	filters_new = {'published': 1, 'business': ''}
	if business:
		filters_new['business'] = business
	page_builder = frappe.db.get_all('Web Page Builder', filters=filters_new, fields=['name', 'page_title', 'route'])
	category = frappe.db.get_all('Product Category', filters={'business': (business if business else '')}, fields=['route'], limit_page_length=1)
	product = frappe.db.get_all('Product', filters={'restaurant': (business if business else '')}, fields=['route'], limit_page_length=1)
	all_pages = [{'name': 'index', 'page_title': 'Home', 'route': ''}]
	if category:
		all_pages.append({'name': 'Category', 'page_title': 'Category', 'route': category[0].route})
	if product:
		all_pages.append({'name': 'Product', 'page_title': 'Product', 'route': product[0].route})
	if page_builder and len(page_builder) > 0:
		builders = list(filter(lambda x: x.route != home_page, page_builder))
		all_pages += builders
	if pages_list and len(pages_list) > 0:
		all_pages += pages_list
	out['pages'] = all_pages
	return out

@frappe.whitelist()
def update_cache_value(catalog, theme):
	sid = frappe.local.session.sid
	frappe.cache().hset(sid, 'catalog_settings', json.loads(catalog))
	frappe.cache().hset(sid, 'theme_settings', json.loads(theme))
	return {'status': 'success'}