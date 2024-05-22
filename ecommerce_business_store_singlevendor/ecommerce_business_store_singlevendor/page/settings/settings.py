# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe, json
from frappe import _
from ecommerce_business_store_singlevendor.utils.setup import get_settings_from_domain, get_theme_settings

@frappe.whitelist()
def get_settings_list(business=None):
	theme = get_theme_settings(business=business)
	if theme:
		theme = frappe.get_doc('Web Theme', theme)
	catalog = get_settings_from_domain('Catalog Settings', business=business)
	result = []
	result.append({'doctype': 'Web Theme', 'data': theme})
	result.append({'doctype': 'Catalog Settings', 'data': catalog})
	return result
