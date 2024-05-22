from __future__ import unicode_literals
import frappe

def get_context(context):
	key = frappe.form_dict.sid or frappe.form_dict.key
	if not key:
		frappe.local.flags.redirect_location = '/404'
	data = frappe.cache().hget("session", key)
	if data:
		frappe.local.login_manager.user = data.data.user
		if frappe.form_dict.sid:
			frappe.local.login_manager.resume = True
		frappe.local.login_manager.post_login()
		frappe.local.flags.redirect_location = frappe.local.response.home_page
	else:
		frappe.local.flags.redirect_location = '/404'
	raise frappe.Redirect