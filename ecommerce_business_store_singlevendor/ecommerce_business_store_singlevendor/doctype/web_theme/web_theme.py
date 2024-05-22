# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import frappe, os


class WebTheme(Document):
	def on_update(self):
		path, sitename = get_path_name()
		if path:
			template = frappe.get_template("templates/includes/themes.css")
			folder_name = self.name.lower().replace(' ', '-')
			if not os.path.exists(os.path.join(path,'public', "webthemes")):
				frappe.create_folder(os.path.join(path,'public', "webthemes"))
			if not os.path.exists(os.path.join(path,'public', "webthemes", folder_name)):
				frappe.create_folder(os.path.join(path,'public', "webthemes", folder_name))
			with open(os.path.join(path,'public', "webthemes", folder_name, ('theme.css')), "w") as f:
				doc_obj = self
				doc_obj.page_css = (self.page_css.replace('\n',''))
				theme_css = template.render({'doc':doc_obj})
				from ecommerce_business_store_singlevendor.utils.setup import minify_string
				f.write(minify_string(theme_css))
			fpath = "/assets/{0}/webthemes/{1}/theme.css".format(sitename, folder_name)
			if self.file_path != fpath:
				frappe.db.set_value('Web Theme', self.name, 'file_path', fpath)
			if self.is_active:
				self.deactivate_themes()

	def deactivate_themes(self):
		themes = frappe.db.get_all('Web Theme', filters={'name': ('!=', self.name), 'is_active': 1})
		if themes:
			frappe.db.set_value('Web Theme', themes[0].name, 'is_active', 0)

	def on_trash(self):
		path, sitename = get_path_name()

@frappe.whitelist()
def get_path_name():
	path = sitename = None
	if "cmswebsite" in frappe.get_installed_apps():
		path = frappe.get_app_path("cmswebsite")
		sitename = 'cmswebsite'
	elif "restaurantcmswebsite" in frappe.get_installed_apps():
		path = frappe.get_app_path("restaurantcmswebsite")
		sitename = 'restaurantcmswebsite'
	return path, sitename

@frappe.whitelist()
def change_theme_values():
	theme = frappe.get_single('Theme Settings')
	keys = theme.as_dict().keys()
	new_doc = frappe.new_doc('Web Theme')
	new_doc.name = 'Website Theme 1'
	new_doc.is_active = 1
	for key in keys:
		if key not in ['modified','creation','owner','modified_by','name','idx','docstatus','doctype']:
			if type(theme.get(key)) == list:
				for item in theme.get(key):
					new_doc.append(key, item)
			else:
				setattr(new_doc, key, theme.get(key))
	new_doc.save(ignore_permissions=True)
