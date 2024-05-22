# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import frappe, os, re
from frappe.utils import encode
from ecommerce_business_store_singlevendor.utils.setup import get_settings

class HomePageBuilders(Document):
	def validate(self):
		if not self.file_name:
			self.file_name = re.sub('[^a-zA-Z0-9 ]', '', self.name).lower().replace(' ','_')
		path = None
		try:
			path = frappe.get_module_path("cms_website")
		except Exception as e:
			try:
				path = frappe.get_module_path("restaurant_cms_website")
			except Exception as e:
				path = None	
		if path:	
			path_parts = path.split('/')
			path_parts = path_parts[:-1]
			url = '/'.join(path_parts)
			home_template = self.get_homepage_data1()
			with open(os.path.join(url,'templates/pages', (self.file_name+'.html')), "w") as f:
				f.write(encode(home_template))

	def get_homepage_data1(self):
		if self.custom_header_footer:
			page_template = '{% extends "templates/Layout/layout.html" %}{% block loader %}{% include "/templates/pages/homepageloader.html" %}{% endblock %}'
			if self.header_template:
				route = frappe.db.get_value('Header Template', self.header_template, 'route')
				page_template += '{% block navbar %}{% include "' + route + '" %}{% endblock %}'
			else:
				page_template += '{% block navbar %}{% if header_file %}{% include header_file %}{% endif %}{% endblock %}'
			if self.footer_template:
				froute = frappe.db.get_value('Footer Template', self.footer_template, 'route')
				page_template += '{% block footer %}{% include "' + froute + '" %}{% endblock %}'
			else:
				page_template += '{% block footer %}{% if footer_file %}{% include footer_file %}{% endif %}{% endblock %}'
			page_template += '{% block content %}'
		else:
			page_template = '{% extends "templates/Layout/customweb.html" %}{% block loader %}{% include "/templates/pages/homepageloader.html" %}{% endblock %}{% block content %}'
		if self.home_page:
			for item in self.home_page:
				route = frappe.db.get_value('Homepage Section', item.home_page_section1, 'file_path')
				page_template += '{% include "' + route + '" %}'										
			
		context={}
		context['theme_settings'] = frappe.get_single('Theme Settings')
		context['catalog_settings'] = get_settings('Catalog Settings')
		context['cart_settings'] = get_settings('Shopping Cart Settings')
		context['order_settings'] = get_settings('Order Settings')
		context['general_settings'] = frappe.get_single('General Settings')
		if self.custom_css:			
			page_template += '<style>'
			template = frappe.render_template(self.custom_css,context)
			page_template += template
			page_template += '</style>'
		page_template += '{% endblock %}'
		if self.custom_js:
			page_template += '{% block script %}'
			template = frappe.render_template(self.custom_js,context)
			page_template += template
			page_template += '{% endblock %}'
		return page_template

	def on_trash(self):
		path = frappe.get_module_path("cms_website")
		path_parts = path.split('/')
		path_parts = path_parts[:-1]
		url = '/'.join(path_parts)
		if os.path.exists(os.path.join(url,'templates/pages', (self.file_name + '.html'))):
			os.remove(os.path.join(url,'templates/pages',(self.file_name + '.html')))

@frappe.whitelist(allow_guest=True)
def get_home_page_prod():
	catalog_settings = get_settings('Catalog Settings')
	HomeCategories = frappe.db.get_all("Product Category",
								fields = ['category_name','category_image','description','route','name'],
								filters = {
											'is_active':1,
											'display_on_home_page':1
										},
        						limit_page_length = catalog_settings.no_of_home_categories_display)
	return HomeCategories
						