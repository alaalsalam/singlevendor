# Copyright (c) 2024, Tridotstech Private Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, re, os
from frappe.model.document import Document
from frappe.utils import get_files_path
from ecommerce_business_store_singlevendor.utils.setup import get_business_from_web_domain, get_settings_from_domain


class OrderSettings(Document):
	def on_update(self):
		path = get_files_path()
		if not os.path.exists(os.path.join(path,'settings')):
			frappe.create_folder(os.path.join(path,'settings'))
		with open(os.path.join(path,'settings', self.name.lower() + '.json'), "w") as f:
			f.write(frappe.as_json(self))

@frappe.whitelist()
def validate_password(password, business=None):
	password_policy = get_settings_from_domain('Order Settings').get("password_policy")
	# frappe.log_error("@@password_policy",password_policy)
	if password_policy == 'Upper Case, Special Character, Number':
		res = re.search('(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!%&@#$^*?_~])[a-zA-Z\d!%&@#$^*?_~]', password)
		if not res:
			frappe.throw(frappe._('Password must contain at least one upper case, one number & one special character'))
			return {"status":"Failed"}
		else:
			return {"status":"Success"}
	elif password_policy == 'Upper Case, Number':
		res = re.search('(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[a-zA-Z\d]', password)
		if not res:
			frappe.throw(frappe._('Password must contain at least one upper case & one number'))
			return {"status":"Failed"}
		else:
			return {"status":"Success"}
	elif password_policy == 'Upper Case, Special Character':
		res = re.search('(?=.*[A-Z])(?=.*[a-z])(?=.*[!%&@#$^*?_~])[a-zA-Z!%&@#$^*?_~]', password)
		if not res:
			frappe.throw(frappe._('Password must contain at least one upper case & one special character'))
			return {"status":"Failed"}
		else:
			return {"status":"Success"}
	elif password_policy == 'Number, Special Character':
		res = re.search('(?=.*\d)(?=.*[a-z])(?=.*[!%&@#$^*?_~])[\d@$!%*#?&a-z]', password)
		if not res:
			frappe.throw(frappe._('Password must contain at least one number & one sepcial character'))
			return {"status":"Failed"}
	elif password_policy == 'Upper Case, Letters':
		res = re.search('(?=.*[A-Z])(?=.*[a-z])[A-Za-z]', password)
		if not res:
			frappe.throw(frappe._('Password must contain at least one upper case'))
			return {"status":"Failed"}
		else:
			return {"status":"Success"}
	elif password_policy == 'Number, Letters':
		res = re.search('(?=.*[a-z])(?=.*\d)[a-z\d]', password)
		if not res:
			frappe.throw(frappe._('Password must contain at least one number and letters'))
			return {"status":"Failed"}
		else:
			return {"status":"Success"}
	elif password_policy == 'Special Character, Letters':
		res = re.search('(?=.*[a-z])(?=.*[!%&@#$^*?_~])[a-z!%&@#$^*?_~]', password)
		if not res:
			frappe.throw(frappe._('Password must contain at least one special character and letters'))
			return {"status":"Failed"}
		else:
			return {"status":"Success"}
	elif password_policy == 'Only Upper Case':
		res = re.match('^[A-Z]*$', password)
		if not res:
			frappe.throw(frappe._('Password must contain only upper case'))
			return {"status":"Failed"}
		else:
			return {"status":"Success"}
	elif password_policy == 'Only Number':
		res = re.match('^[0-9]*$', password)
		if not res:
			frappe.throw(frappe._('Password must contain only number'))
			return {"status":"Failed"}
		else:
			return {"status":"Success"}
	elif password_policy == 'Only Special Character':
		res = re.search('(?=.*[!%&@#$^*?_~])[!%&@#$^*?_~]', password)
		if not res:
			frappe.throw(frappe._('Password must contain only special character'))
			return {"status":"Failed"}
		else:
			return {"status":"Success"}

