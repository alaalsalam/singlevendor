# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe, json, math
from frappe.utils.nestedset import get_root_of
from frappe.utils import cint, flt
from six import string_types

@frappe.whitelist()
def get_items(start, page_length, search_txt=None, search_term=None):
	data = dict()
	condition = ''
	filters = ''
	joins = ''
	result = []
	if search_txt:
		joins += ' inner join `tabProduct Category Mapping` PCM on PCM.parent=P.name'
		filters += " and PCM.category='{category}'".format(category=search_txt)
	if search_term:
		filters += ' and (P.name like "%{txt}%" or P.item like "%{txt}%")'.format(txt=search_term)

	items_data = frappe.db.sql("""
		SELECT
			P.name AS item_code,
			P.item AS item_name,
			P.stock,
			P.image AS item_image,
			P.idx AS idx,
			P.price
		FROM
			`tabProduct` P {joins}
		WHERE
			P.is_active = 1 {condition}
		ORDER BY
			P.idx desc"""
		.format(
			start=start,
			page_length=page_length,condition=filters, joins=joins
		), as_dict=1)

	if items_data:
		for item in items_data:
			row = {}
			currency = frappe.cache().hget('currency', 'symbol')
			item.price = currency + ' %.2f' % round(float(item.price),2)
			row.update(item)
			result.append(row)

	res = {
		'items': result
	}

	return res

@frappe.whitelist()
def get_currency():
	currency = frappe.cache().hget('currency', 'symbol')
	return currency

@frappe.whitelist()
def item_group_query(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql('''select name, category_name from `tabProduct Category` where is_active = 1''')

@frappe.whitelist()
def get_item(item_code):
	from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api import get_product_price
	items = frappe.db.sql('''select name, item, price, minimum_order_qty, image from `tabProduct` where name = "{item_code}"'''.format(item_code=item_code), as_dict=1)
	if items:
		if not items[0].image:
			items[0].image = "/assets/cmswebsite/images/no-image-60x50.png"
		tax = calculate_item_tax(items[0])
		if tax:
			items[0].tax = tax['item_tax']
			items[0].tax_label = tax['tax_label']
		else:
			items[0].tax = 0
			items[0].tax_label = ''
	currency = frappe.cache().hget('currency', 'symbol')
	return {'items': items, 'currency': currency}

@frappe.whitelist()
def calculate_item_tax(item):
	tax_info = None
	from ecommerce_business_store_singlevendor.utils.setup import get_settings_from_domain
	tax_info = frappe.db.get_value('Product', item.name, 'tax_category')
	if tax_info:
		catalog_settings = get_settings_from_domain('Catalog Settings', business=item.business)
		tax_template = frappe.get_doc('Product Tax Template', tax_info)
		if tax_template.tax_rates:
			item_tax = 0
			item_breakup = ''
			tax_label = ''
			for tax in tax_template.tax_rates:
				tax_value = 0
				if catalog_settings.included_tax:
					tax_label = "Incl"
					tax_value = (flt(item.price) * tax.rate / (100 + tax.rate))
				else:
					tax_label = "Excl"
					tax_value = flt(item.price) * tax.rate / 100
				item_tax = item_tax + tax_value
				item_breakup += str(tax.tax) + ' - ' + str(tax.rate) + '% - ' + str(tax_value) + '\n'
			return {'item_tax': item_tax, 'tax_label': tax_label}

@frappe.whitelist()
def inserOrder(doc):
	from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api import get_today_date
	from ecommerce_business_store_singlevendor.utils.setup import get_settings_from_domain
	catalog_settings = get_settings_from_domain('Catalog Settings')
	request = json.loads(doc)
	order_sub_total = 0
	order_total = 0
	customers = frappe.db.get_all('Customers', filters={'name': request.get('customer_name')}, fields=['*'])
	customer_billing_address = frappe.db.sql('''select * from `tabCustomer Address` where parent=%(parent)s and is_default=1''',{'parent': request.get('customer_name')}, as_dict=1)
	order = frappe.new_doc('Order')
	order.naming_series = 'ORD-'
	if customer_billing_address:
		order.first_name = customer_billing_address[0].first_name
		if order.first_name == 'Guest':
			order.first_name = customers[0].first_name
		order.city = customer_billing_address[0].city
		order.zipcode = customer_billing_address[0].zipcode
		order.last_name = (customer_billing_address[0].last_name or '')
		if order.last_name == 'None': order.last_name = None
		order.state = customer_billing_address[0].state
		order.phone = customer_billing_address[0].phone
		order.address = customer_billing_address[0].address
		order.country = customer_billing_address[0].country
		if customer_billing_address[0].door_no:
			order.door_no = customer_billing_address[0].door_no
		if customer_billing_address[0].unit_number:
			order.unit_number = customer_billing_address[0].unit_number
		if customer_billing_address[0].landmark:
			order.landmark = customer_billing_address[0].landmark
		order.shipping_first_name = customer_billing_address[0].first_name
		if order.shipping_first_name == 'Guest':
			order.shipping_first_name = customers[0].first_name
		order.shipping_city = customer_billing_address[0].city
		order.shipping_zipcode = customer_billing_address[0].zipcode
		order.shipping_last_name = (customer_billing_address[0].last_name or '')
		if order.shipping_last_name == 'None': order.shipping_last_name = None
		order.shipping_state = customer_billing_address[0].state
		order.shipping_phone = customer_billing_address[0].phone
		order.latitude = customer_billing_address[0].latitude
		order.longitude = customer_billing_address[0].longitude
		if customer_billing_address[0].door_no:
			order.shipping_door_no = customer_billing_address[0].door_no
		if customer_billing_address[0].unit_number:
			order.shipping_unit_number = customer_billing_address[0].unit_number
		if customer_billing_address[0].landmark:
			order.shipping_landmark = customer_billing_address[0].landmark
		order.shipping_shipping_address = customer_billing_address[0].address
		order.shipping_country = customer_billing_address[0].country
	order.payment_method = request.get('payment_method')
	order.order_date = get_today_date(replace=True)
	order.order_time = get_today_date(replace=True).strftime('%I:%M %p')
	if customers:
		order.customer = customers[0].name
		if customers[0].naming_series == 'GC-':
			order.phone = customers[0].phone
	for cart_item in request.get('items_list'):
		order_sub_total += flt(cart_item.get('rate'))
	order.shipping_method = request.get('shipping_method')
	order.order_subtotal = float(request.get('subtotal'))
	order.total_tax_amount = float(request.get('total_tax'))
	order.discount = float(request.get('discount'))
	order.total_amount = float(request.get('total_amt'))
	order.save(ignore_permissions=True)
	order_info = order.as_dict()
	tax_breakup = None
	tax_splitup = []
	if catalog_settings.included_tax:
		tax_type = 'Incl. Tax'
	else:
		tax_type = 'Excl. Tax'
	for cart_item in request.get('items_list'):
		item_tax = 0
		base_price = 0
		product = frappe.get_doc('Product', cart_item.get('name'))
		product_tax = None
		tax_template = None
		if frappe.db.get_value('Product', cart_item.get('name')):
			product_tax = frappe.db.get_value('Product', cart_item.get('name'), 'tax_category')
		if product_tax:
			tax_template = frappe.get_doc('Product Tax Template', product_tax)
		if tax_template and tax_template.tax_rates:
			for tax in tax_template.tax_rates:
				if catalog_settings.included_tax:
					tax_value = cart_item.get('rate') * tax.rate / (100 + tax.rate)
				else:
					tax_value = cart_item.get('rate') * tax.rate / 100
				item_tax = item_tax + tax_value
				cur_tax = next((x for x in tax_splitup if (x['type'] == tax.tax and x['rate'] == tax.rate)), None)
				if cur_tax:
					for it in tax_splitup:
						if it['type'] == tax.tax:
							it['amount'] = it['amount'] + tax_value
				else:
					tax_splitup.append({'type': tax.tax,'rate': tax.rate, 'amount': tax_value, 'account': tax.get('account_head'), 'tax_type': tax_type })
		result = frappe.get_doc({
			'doctype': 'Order Item',
			'parent': order_info.name,
			'parenttype': 'Order',
			'parentfield': 'order_item',
			'order_item_type': 'Product',
			'item': cart_item.get('name'),
			'item_name': product.item,
			'item_sku':product.sku,
			'tax': item_tax,
			'ordered_weight':product.weight*cart_item.get('quantity'),
			'weight':product.weight*cart_item.get('quantity'),
			'quantity': cart_item.get('quantity'),
			'price': cart_item.get('rate'),
			'amount': cart_item.get('rate'),
			't_amount': cart_item.get('rate'),
			'base_price': ('%.2f'%base_price)
			}).insert()
	tax_json = []
	if tax_splitup:
		tax_breakup = ''
		for s in tax_splitup:
			tax_json.append(s)
			tax_breakup += str(s['type']) + ' - ' + str('{0:.2f}'.format(s['rate'])) + '% - ' + str('{0:.2f}'.format(s['amount'])) + ' - ' + tax_type + '\n'
	frappe.db.set_value('Order', order_info.name, 'tax_json', json.dumps(tax_json))
	frappe.db.set_value('Order', order_info.name, 'tax_breakup', tax_breakup)
	order_data = frappe.get_doc('Order', order_info.name)
	order_data.docstatus = 1
	order_data.save(ignore_permissions=True)
	return order_data