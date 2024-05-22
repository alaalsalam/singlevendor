# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import frappe, os, re
from frappe.utils import  encode
from frappe.core.doctype.domain_settings.domain_settings import get_active_domains


class ThemeSettings(Document):
	def validate(self):
		domains_list=get_active_domains()
		if "Restaurant" in domains_list:
			path = frappe.get_module_path('restaurant_cms_website')
		else:
			path = frappe.get_module_path("cms_website")		
		path_parts=path.split('/')
		path_parts=path_parts[:-1]
		url='/'.join(path_parts)
		# if os.path.exists(os.path.join(url,'public','css','theme.css')):
		# 	template=frappe.render_template(os.path.join(url,'public','css','theme.css'),{'theme_settings':self})
		# else:
		# 	template=None
		template=frappe.get_template("templates/includes/themes.css")

		with open(os.path.join(url,'public','css', ('theme.css')), "w") as f:
			f.write(encode(template.render({'doc':self})))
	def on_update(self):
		from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api import get_homepage_builder
		get_homepage_builder()