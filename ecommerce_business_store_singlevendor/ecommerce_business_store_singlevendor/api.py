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

@frappe.whitelist(allow_guest=True)
def update_order_status(order_id, transaction_id, capture=None):
	try:
		from razor_pay.templates.pages.razor_pay_checkout import update_order_status as _update_order_status
		return _update_order_status(order_id, transaction_id, capture)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store.ecommerce_business_store.api.update_order_status") 	

def get_attributes_json(attribute_id):
	if attribute_id:
		if attribute_id.find('\n'):
			attribute_ids = attribute_id.split('\n')
			ids_list = []
			for x in attribute_ids:
				if x:
					ids_list.append(x)
			# ids_list.sort()
			attribute_id = json.dumps(ids_list)
		return attribute_id.replace(' ','')

@frappe.whitelist(allow_guest=True)
def calculate_shipment_charges(shipment_bag_id):
	condition = ''
	weight = shipping_charges = 0
	order_total = 0
	shipping_charges_list = []
	shipping_method = None
	shipping_rate_method = frappe.db.sql('''select shipping_rate_method as name from `tabShipping Rate Method` where is_active = 1 {0}'''.format(condition), as_dict=1)
	order_list = frappe.db.get_all("Shipment Bag Item",filters={"parent":shipment_bag_id},fields=['order_id'])
	if order_list:
		shipping_method = frappe.db.get_value("Order",order_list[0].order_id,"shipping_method")
	if len(order_list)>0:
		shipping_addr = frappe._dict({"zipcode":order_list[0].shipping_zipcode, "state": order_list[0].shipping_state, "country":order_list[0].shipping_country})
	for x in order_list:
		# shipping_addr = frappe.get_doc('Customer Address', shipping_addr)

		order_items = frappe.db.get_all("Order Item",filters={"parent":x.order_id},fields=['*'])

		for citem in order_items:
			(product_weight, enable_shipping, free_shipping,
			 additional_shipping_cost, tracking_method) = frappe.db.get_value('Product', citem.item,
					['weight', 'enable_shipping', 'free_shipping', 'additional_shipping_cost', 'inventory_method'])
			if enable_shipping == 1 and free_shipping == 0:

				if citem.attribute_ids and tracking_method == 'Track Inventory By Product Attributes':
					attribute_id = get_attributes_json(citem.attribute_ids)						
					combination_weight = frappe.db.sql('''select weight from `tabProduct Variant Combination` where parent=%(name)s and attributes_json=%(attribute_id)s''', {'name': citem.item, 'attribute_id': attribute_id}, as_dict=1)
					if combination_weight:
						weight += combination_weight[0].weight * citem.quantity
						if additional_shipping_cost > 0:
							shipping_charges += additional_shipping_cost * citem.quantity
						order_total += citem.t_amount
				else:

					weight += product_weight * citem.quantity
					if additional_shipping_cost > 0:
						shipping_charges += additional_shipping_cost \
						* citem.quantity
					order_total += citem.t_amount

					if citem.attribute_ids:
						attr_id = citem.attribute_ids.splitlines()
						for item in attr_id:
							query = \
								'''SELECT * FROM `tabProduct Attribute Option` WHERE name="{name}"'''.format(name=item)
							attribute_weight = frappe.db.sql(query,
									as_dict=1)
							if attribute_weight \
								and attribute_weight[0].weight_adjustment:
								weight += \
		flt(attribute_weight[0].weight_adjustment) * citem.quantity
	
	if shipping_rate_method[0].name == 'Fixed Rate Shipping':
		shipping_charges_list = frappe.db.sql('''select * from `tabShipping By Fixed Rate Charges` where shipping_method=%(shipping_method)s'''
					  , {'shipping_method': shipping_method}, as_dict=True)
		
	if shipping_rate_method[0].name == 'Shipping By Total':
		shipping_charges_list = frappe.db.sql('''select * from `tabShipping By Total Charges` where shipping_method=%(shipping_method)s and %(order_total)s>=order_total_from and %(order_total)s<=order_total_to'''
					  , {'order_total': order_total, 'shipping_method': shipping_method}, as_dict=True)

	if shipping_rate_method[0].name == 'Shipping By Weight':
		shipping_charges_list = \
		frappe.db.sql('''select * from `tabShipping By Weight Charges` where shipping_method=%(shipping_method)s and %(weight)s>=order_weight_from and %(weight)s<=order_weight_to'''
					  , {'weight': weight,
					  'shipping_method': shipping_method}, as_dict=True)
	return calculate_shipping_charges_from_list(shipping_charges,
			shipping_charges_list, shipping_addr, order_total)

@frappe.whitelist(allow_guest=True)
def shipping_zip_matches(zip, ziprange):
	zipcoderanges = []
	returnValue = False
	if ziprange.find(',') > -1:
		zipcoderanges = ziprange.split(',')
		for x in zipcoderanges:
			if x.find('-') > -1:
				zipcoderanges_after = x.split('-')
				for zipcode in range(int(zipcoderanges_after[0]), int(zipcoderanges_after[1]) + 1):
					if str(zipcode).lower() == str(zip).lower():
						returnValue = True
			else:
				if str(x).lower().replace(" ","") == str(zip).lower().replace(" ",""):
					returnValue = True
	elif ziprange.find('-') > -1:
		zipcoderanges_after = ziprange.split('-')
		for zipcode in range(int(zipcoderanges_after[0]), int(zipcoderanges_after[1]) + 1):
			if str(zipcode).lower() == str(zip).lower():
				returnValue = True
	else:
		if str(ziprange).lower() == str(zip).lower():
			returnValue = True
	return returnValue

def calculate_shipping_charges_from_list(shipping_charges, shipping_charges_list, shipping_addr,
	subtotal, is_multivendor=None, vendor_id=None):
	if is_multivendor and vendor_id:
		matchedByVendor = []
		vendors = frappe.db.sql('select zip_code from `tabBusiness` where name=%(vendor_id)s' , {'vendor_id': vendor_id}, as_dict=True)
		if vendors:
			vendor_info = vendors[0]
			for x in shipping_charges_list:
				shipping_zone = frappe.get_doc('Shipping Zones', x.shipping_zone)
				if shipping_zone:
					shipping_city = frappe.db.sql('''select * from `tabShipping City` where name=%(city)s''', {'city': shipping_zone.from_city}, as_dict=True)
					if shipping_city:
						if shipping_city[0].zipcode_range:
							if shipping_zip_matches(vendor_info.zip_code, shipping_city[0].zipcode_range):
								matchedByVendor.append(x)
		if len(matchedByVendor) == 0:
			for item in shipping_charges_list:
				shipping_zone = frappe.get_doc('Shipping Zones', item.shipping_zone)
				if not shipping_zone.from_city:
					matchedByVendor.append(item)
					shipping_charges_list = matchedByVendor

	matchedShippingCharges = []
	# matched by zip
	matchedByZip = []
	for item in shipping_charges_list:
		shipping_zone = frappe.get_doc('Shipping Zones', item.shipping_zone)
		if shipping_zone:
			shipping_city = frappe.db.sql('''select * from `tabShipping City` where name=%(city)s''', {'city': shipping_zone.to_city},as_dict=True)
			if shipping_city:
				if shipping_city[0].zipcode_range:
					if shipping_zip_matches(shipping_addr.zipcode, shipping_city[0].zipcode_range):
						matchedShippingCharges.append(item)
	if len(matchedShippingCharges) == 0:
		for x in shipping_charges_list:
			shipping_zone = frappe.get_doc('Shipping Zones', x.shipping_zone)
			if shipping_zone.state == shipping_addr.state:
				matchedShippingCharges.append(x)
		if len(matchedShippingCharges) == 0:
			for x in shipping_charges_list:
				shipping_zone = frappe.get_doc('Shipping Zones', x.shipping_zone)
				if shipping_zone.country == shipping_addr.country:
					matchedShippingCharges.append(x)

	# matched by zip
	# matched by state

	matchedByState = []
	for x in matchedByZip:
		shipping_zone = frappe.get_doc('Shipping Zones', x.shipping_zone)
		if shipping_zone.state == shipping_addr.state:
			matchedByState.append(x)
	if len(matchedByState) == 0:
		for x in matchedByZip:
			shipping_zone = frappe.get_doc('Shipping Zones', x.shipping_zone)
			if not shipping_zone.state:
				matchedByState.append(x)

	# matched by state
	# matched by country

	matchedByCountry = []
	for x in matchedByState:
		shipping_zone = frappe.get_doc('Shipping Zones', x.shipping_zone)
		if shipping_zone.country == shipping_addr.country:
			matchedByCountry.append(x)
	if len(matchedByCountry) == 0:
		for x in matchedByState:
			shipping_zone = frappe.get_doc('Shipping Zones', x.shipping_zone)
			if not shipping_zone.country:
				matchedByCountry.append(x)

	# matched by country

	if matchedShippingCharges:
		shipingmatchedByZip = matchedShippingCharges[0]
		if shipingmatchedByZip.use_percentage == 1:
			shipping_charges += float(subtotal) * shipingmatchedByZip.charge_percentage / 100
		else:
			shipping_charges += float(shipingmatchedByZip.charge_amount)

	return shipping_charges