import frappe
import json
from ecommerce_business_store_singlevendor.utils.setup import get_business_from_web_domain, get_settings_from_domain
from urllib.parse import urljoin, unquote, urlencode
import requests
from frappe.utils import cstr, flt, getdate, nowdate, now, today, encode, get_url

try:
	catalog_settings = get_settings_from_domain('Catalog Settings')
	media_settings = get_settings_from_domain('Media Settings')
	cart_settings = get_settings_from_domain('Shopping Cart Settings')
	order_settings = get_settings_from_domain('Order Settings')
	no_of_records_per_page = catalog_settings.no_of_records_per_page
	domain_constants = []
except Exception as e:
	catalog_settings = None
	media_settings = None
	cart_settings = None
	order_settings = None
	no_of_records_per_page = 10

@frappe.whitelist(allow_guest=True)
def insert_questionaproduct(data):
	try:
		val1=json.loads(data)
		isMobile = 0
		if val1.get('ismobile'):
			isMobile = val1.get('ismobile')
		if catalog_settings.enable_captcha and catalog_settings.qsn_a_product and isMobile == 0:
			captcha_message = validate_captcha(val1.get('private_key'), val1.get('captcha_response'))						
			if captcha_message == "Success":
				result = insert_question_aproduct(data)
				return result
		else:
			result = insert_question_aproduct(data)
			return result
	except Exception:
		frappe.log_error(frappe.get_traceback(),
						 'ecommerce_business_store.ecommerce_business_store.api.insert_questionaproduct'
						 )

@frappe.whitelist(allow_guest=True)
def validate_captcha(secret, response):
	VERIFY_SERVER="www.google.com"
	params = {
	  'secret': secret,
	  'response': response,
	  'remoteip': get_url()
	}
	url = "https://%s/recaptcha/api/siteverify?%s" % (VERIFY_SERVER, urlencode(params))
	response = requests.get(url)
	return_values = response.json()
	return_code = return_values ["success"]
	if (return_code == True):
		return "Success"
	else:
		return "Failed"

@frappe.whitelist(allow_guest=True)
def insert_question_aproduct(data):
	try:
		response = json.loads(data)
		result = frappe.get_doc({
			'doctype': 'Product Enquiry',
			'email': response.get('sender_email'),
			'user_name': response.get('sender_name'),
			'phone': response.get('sender_phone'),
			'question': response.get('question'),
			'product': response.get('product'),
			}).insert(ignore_permissions=True)
		result.creation = getdate(result.creation).strftime('%d %b, %Y')
		frappe.db.commit()
		return result
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'ecommerce_business_store.ecommerce_business_store.api.insert_question_aproduct')
