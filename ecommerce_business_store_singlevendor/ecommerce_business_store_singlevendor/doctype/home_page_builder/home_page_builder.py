# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import frappe, os
from frappe.utils import encode
from frappe.core.doctype.domain_settings.domain_settings import get_active_domains

class HomePageBuilder(Document):
	def validate(self):
		domains_list = get_active_domains()
		if "Restaurant" in domains_list:
			path = frappe.get_module_path('restaurant_cms_website')
		else:
			path = frappe.get_module_path("cms_website")		
		path_parts = path.split('/')
		path_parts = path_parts[:-1]
		url = '/'.join(path_parts)
		with open(os.path.join(url,"templates/pages/homebuilder.html"), "w") as f:
			f.write(encode(self.home_page))