# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
import math
from frappe import format_value, _
from frappe.model.document import Document
from frappe.utils import flt, cint, getdate, nowdate, today, fmt_money,add_days
from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common \
	import get_today_date
from ecommerce_business_store_singlevendor.utils.setup import get_settings_value
from urllib.parse import unquote
from six import string_types

class Discounts(Document):
	def validate(self):
		if self.start_date and self.end_date:
			if self.end_date<self.start_date:
				frappe.throw(frappe._('Start date should not be greater than end date'))
		if self.percent_or_amount == 'Discount Percentage' and \
						self.discount_type != 'Assigned to Delivery Charges':
			if flt(self.discount_percentage)>=100:
				frappe.throw(frappe._('Please enter percentage below 100'))
		if self.discount_type == 'Assigned to Sub Total' and self.requires_coupon_code:
			coupon=frappe.db.get_list("Discounts", fields=['*'], filters={
				'coupon_code':self.coupon_code,'name':("!=",self.name)})		
			if coupon:
				frappe.throw(frappe._('This Coupon code is already used.'))
		if int(self.min_qty) < 1:
			frappe.throw(frappe._('Minimum quantity must be greater than 0'))

		self.validate_freeitems()
		if self.discount_type == 'Assigned to Categories':
			self.check_deleted_category()
			self.check_child_category()

		self.validate_date_range()

	def on_update(self):
		frappe.enqueue('ecommerce_business_store_singlevendor.\
				 ecommerce_business_store_singlevendor.doctype.discounts.discounts.update_cart')
		if self.discount_type == 'Assigned to Categories':
			self.check_deleted_category()
			self.check_child_category()

	def validate_freeitems(self):
		if self.price_or_product_discount == "Product" and len(self.discount_applied_product) > 0:
			for n in self.discount_applied_product:
				if not n.discount_type:
					n.discount_percentage = 0
					n.discount_amount = 0
				elif n.discount_type == "Discount Percentage":
					n.discount_amount = 0
				elif n.discount_type == "Discount Amount":
					n.discount_percentage = 0

	
	def discount_validation(self):
		if self.discount_type == 'Assigned to Sub Total' and self.percent_or_amount == 'Discount Amount':
			discount_requirements_has_values(self)
		elif self.discount_type == 'Assigned to Products' and self.percent_or_amount == 'Discount Amount':
			for item in self.discount_products:
				products = frappe.db.sql('''
							SELECT P.product, P.product_name, P.price, P.vendor_name 
							FROM `tabProduct Price` AS P 
							WHERE P.product = "{0}"
						'''.format(item.items), as_dict=1)

				for pdt in products:
					if flt(self.discount_amount) > flt(pdt.price):
						frappe.throw(frappe._('Price of {0} is lesser than \
									the current discount amount.').format(pdt.product_name))
		if self.discount_type == 'Assigned to Sub Total':
			for item in self.discount_requirements:
				if item.discount_requirement != 'Spend x amount' and item.discount_requirement != \
						'Specific price range' and item.discount_requirement != 'Spend x weight':
					frappe.throw(frappe._('Please add any items for discount \
						   requirement "{0}"').format(item.discount_requirement))
		else:
			if self.discount_requirements:
				for req in self.discount_requirements:
					requirement = [
									'Has any one product in cart',
									'Has all these products in cart', 
									'Specific price range'
								]
					if req.discount_requirement in requirement:
						frappe.delete_doc('Discount Requirements', req.name, ignore_permissions=True)


	def check_deleted_category(self):
		unique_parent = list(set([i.get('parent_category') for i in self.discount_categories]))
		category = ''
		for item in unique_parent:
			if item:
				check_parent = next((x for x in self.discount_categories if x.category == item), None)
				category = '"' + item + '",'
		if category == '': category = '"",'
		category = category[:-1]
		frappe.db.sql('''DELETE FROM `tabDiscount Categories`
						WHERE parent_category IN ({0}) 
							AND parent = "{1}"
					'''.format(category, self.name))


	def check_child_category(self):
		for item in self.discount_categories:
			child_level_1 = frappe.db.sql('''
								SELECT P.name, P.category_name, P.is_group 
								FROM `tabProduct Category` AS P 
								WHERE P.parent_product_category = %(category)s
							''', {'category': item.category}, as_dict=1)

			for l1 in child_level_1:
				check_record1 = next((x for x in self.discount_categories if x.category == l1.name), None)
				if not check_record1:
					self.append('discount_categories', {
														'category': l1.name,
														'category_name': l1.category_name,
														'is_child': 1,
														'parent_category': item.category,
														'discount_value':item.discount_value
													})
				if l1.is_group:
					child_level_2 = frappe.db.sql('''
										SELECT P.name, P.category_name, P.is_group 
										FROM `tabProduct Category` AS P 
										WHERE P.parent_product_category = %(category)s
									''', {'category': l1.name}, as_dict=1)

					for l2 in child_level_2:
						check_record2 = next((x for x in self.discount_categories if x.category == l2.name), None)
						if not check_record2:
							self.append('discount_categories', {
																'category': l2.name,
																'category_name': l2.category_name, 
																'is_child': 1,
																'parent_category': item.category,
																'discount_value':item.discount_value
															})


	def validate_date_range(self):
		update_value = False
		if not self.current_date_range:
			update_value = True
		else:
			date_slot = self.current_date_range.split(' -- ')
			if date_slot[0] != str(self.start_date):
				update_value = True
			if date_slot[1] != str(self.end_date):
				update_value = True
		if update_value:
			self.current_date_range = '{} -- {}'.format(
														str(self.start_date or ''),
														str(self.end_date or '')
													)


def discount_requirements_has_values(self):
		if len(self.discount_requirements) > 0:
			discount = next((x for x in self.discount_requirements \
					if x.discount_requirement == 'Spend x amount'), None)
			if discount:
				if flt(discount.amount_to_be_spent) < flt(self.discount_amount):
					frappe.throw(frappe._('Spent Amount should not be greater than Discount Amount'))
			min_max = next((x for x in self.discount_requirements \
				if x.discount_requirement == 'Specific price range'), None)
			if not min_max:
				frappe.throw(frappe._('Please select the requirement type "Spend x Amount"'))
			if min_max:
				if flt(min_max.min_amount) < flt(self.discount_amount) \
							and flt(min_max.max_amount) < flt(self.discount_amount):
					frappe.throw(frappe._('Minimum and Maximum Amount should not \
											be greater than Discount Amount'))
			else:
				if not discount:
					frappe.throw(frappe._('Please select the requirement type "Specific price range"'))
		else:
			frappe.throw(frappe._('Please select the requirement type "Spend x Amount"'))
			
@frappe.whitelist()
def get_free_item(txt):
	condition = ''
	if txt:
		condition += ' AND item LIKE "%{txt}%"'.format(txt=txt)
	return frappe.db.sql('''SELECT name, item 
							FROM `tabProduct`
							WHERE status = "Approved" 
								AND is_active = 1 {condition}
						'''.format(condition=condition))


@frappe.whitelist(allow_guest=True)
def get_product_discount(product, qty = 1, rate = None, customer_id = None, attribute_id = None, product_array = None):
	try:
		product = frappe._dict(product)
	except Exception:
		pass
	if attribute_id:
		if isinstance(attribute_id, string_types):
			if attribute_id.find('[')!=-1:
				attribute_id = json.loads(attribute_id)
				if isinstance(attribute_id, list) and len(attribute_id) == 1:
					attribute_id = attribute_id[0]
	out = {}
	product_info = {}
	if not customer_id and frappe.request.cookies.get('customer_id'):
		customer_id = unquote(frappe.request.cookies.get('customer_id'))
	if frappe.db.get_value('Product', product.get("name")):
		product_info = frappe._dict(name= product.get("name"), price= product.get("price"))
	discounts_list = get_product_discount_rule(product_info, qty)
	currency_name = get_settings_value('Catalog Settings', 'default_currency')
	currency = frappe.db.get_value('Currency', currency_name, 'symbol')
	allowed_discount = None
	if discounts_list:
		out = get_product_discount_requirement(
												discounts_list,
												qty,
												customer_id,
												rate,
												product,
												attribute_id,
												currency,
												allowed_discount
											)
	return out


def get_product_discount_rule(product, qty):
	today_date = get_today_date(replace=True)
	categories = get_product_categories(product.name)
	query = f'''SELECT D.*, DP.product_attribute_json,
				IFNULL((SELECT COUNT(*) 
						FROM `tabDiscount Requirements` DR 
						WHERE DR.parent = D.name 
							AND parenttype = "Discounts"), 0) AS requirements,
				IFNULL((SELECT COUNT(*) 
						FROM `tabDiscount Usage History` DH 
						WHERE DH.parent = D.name 
							AND parenttype = "Discounts"), 0) AS history 
				FROM `tabDiscounts` AS D
				LEFT JOIN `tabDiscount Products` AS DP ON D.name = DP.parent 
				LEFT JOIN `tabDiscount Categories` AS DC ON D.name = DC.parent 
				LEFT JOIN `tabDiscount Applied Product` AS DAP ON D.name = DAP.parent 
				WHERE (CASE WHEN start_date IS NOT NULL THEN start_date <= '{getdate(today_date)}'
						ELSE 1 = 1 END) 
					AND (CASE WHEN end_date IS NOT NULL THEN end_date >= '{getdate(today_date)}'
						ELSE 1 = 1 END) 
					AND ((CASE WHEN D.discount_type = 'Assigned to Products'
						THEN DP.items = '{product.name}'
						WHEN D.discount_type = 'Assigned to Categories'
						THEN DC.category IN ({categories})
						ELSE 1 = 1 END) ) 
					AND D.discount_type NOT IN ("Assigned to Sub Total", "Assigned to Delivery Charges") 
					AND (D.requires_coupon_code = 0 OR D.requires_coupon_code IS NULL)
				ORDER BY priority DESC '''
	rule = frappe.db.sql(query, as_dict = 1)
	if rule:
		return get_product_dixcount_rule_(rule,product)
		

def get_product_categories(product_id):
	res = frappe.db.sql(f'''SELECT group_concat(concat('"',category,'"')) val 
							FROM 
								`tabProduct Category Mapping` 
							WHERE parent=%(parent)s ''', {'parent': product_id}, as_dict=1)
	if res and res[0].val:
		return res[0].val
	return '""'


@frappe.whitelist(allow_guest=True)
def get_order_subtotal_discount(subtotal, customer_id, cart_items, total_weight=0,
								shipping_method=None, payment_method=None, shipping_charges=0):
	out = {}
	assigned = False
	discounts = get_subtotal_discount()
	discount = None
	for d in discounts:
		res = validate_requirements(
									d, 
									subtotal, 
									customer_id, 
									cart_items, 
									total_weight,
									shipping_method, 
									payment_method
								)
		if res['status'] == 'success':			
			assigned = True
			discount = d
			break
	if assigned:
		out['discount_rule'] = discount.name
		out = get_order_subtotal_discount_assigned(discount,subtotal,cart_items)
		
	if shipping_method or payment_method or customer_id:
		out = check_product_discounts(
										cart_items, 
										customer_id, 
										shipping_method,
										payment_method, 
										subtotal = subtotal, 
										out = out,
										total_weight = total_weight
									)
	if shipping_charges and float(shipping_charges) > 0:
		out = check_delivery_charge_discount(
												customer_id, 
												subtotal, 
												cart_items,
												shipping_charges, 
												shipping_method, 
												out=out, 
												payment_method=payment_method
											)
	return out


@frappe.whitelist(allow_guest=True)
def get_ordersubtotal_discount_forfree_item(subtotal,cart_items):
	out = {}
	products_list = []
	assigned = False
	discount = None
	if assigned:
		out['discount_rule'] = discount.name
		if discount.price_or_product_discount == 'Product':
			out['same_product'] = 0
			out['min_qty'] = discount.min_qty
			nonfree_product_item = frappe.db.sql('''SELECT * 
													FROM `tabDiscount Applied Product` 
													WHERE parent=%(parent)s 
													AND (discount_type="Discount Percentage" 
													OR discount_type="Discount Amount")
												''', {'parent': discount.name}, as_dict=1)

			free_product_item = frappe.db.sql('''SELECT * 
												FROM `tabDiscount Applied Product` 
												WHERE parent=%(parent)s 
												AND (discount_type!="Discount Percentage" 
												AND discount_type!="Discount Amount")
											''', {'parent': discount.name}, as_dict=1)

			out =  get_ordersubtotal_discount_fornonfree_product_item(
																		nonfree_product_item,
																		subtotal,
																		out,
																		cart_items
																	)
			if free_product_item and len(free_product_item) > 0:
				products_list = get_ordersubtotal_discount_forfree_product_item(
																				free_product_item,
																				products_list
																			)
	if len(products_list)>0:
		out['free_item'] = 1
		out['products_list'] = products_list
	return out


def get_subtotal_discount():
	today_date = get_today_date(replace=True)
	query = f'''SELECT d.* 
				FROM `tabDiscounts` d  
				WHERE 
					(CASE WHEN start_date IS NOT NULL THEN start_date <= '{getdate(today_date)}'
						ELSE 1 = 1 END) 
					AND (CASE WHEN end_date IS NOT NULL THEN end_date >= '{getdate(today_date)}'
						ELSE 1 = 1 END) 
					AND (d.discount_type = "Assigned to Sub Total" 
						OR (d.discount_type = "Assigned to Delivery Charges"))
					AND (requires_coupon_code = 0 
						OR requires_coupon_code IS NULL)
				ORDER BY priority DESC
			'''
	rule = frappe.db.sql(query, as_dict=1)
	return rule


def validate_requirements(discount, subtotal, customer_id, cart_items, total_weight, shipping_method=None, payment_method=None):
	date = get_today_date(replace=True)
	msg = frappe._('Invalid Coupon Code')
	if discount.start_date and discount.start_date > getdate(date):
		return {'status': 'failed', 'message': msg}
	if discount.end_date and discount.end_date < getdate(date):
		return {'status': 'failed', 'message': msg}
	qty_count = sum(int(x.get('quantity')) for x in cart_items) if cart_items else 0
	if discount.min_qty and discount.min_qty > int(qty_count):
		return {'status': 'failed', 'message':
		  frappe._('Minimum {0} products must be purchased to apply this code').format(discount.min_qty)}
	if discount.max_qty and discount.max_qty < int(qty_count):
		return {'status': 'failed', 'message': 
		  frappe._('Maximum {0} products must be purchased to apply this code').format(discount.max_qty)}
	if discount.limitations != 'Unlimited':
		usage_history = get_usage_history(discount)
		if usage_history and len(usage_history) > 0:
			if discount.limitations == 'N times only' and int(discount.limitation_count) <= len(usage_history):
				return {'status': 'failed', 'message': frappe._('Coupon code has been expired')}
			if discount.limitations == 'N times per user':
				if customer_id.startswith('GC-'):
					return { 'status': 'failed', 'message': frappe._('Please login to use this code')}
				check_customer_records = list(filter(lambda x: x.customer == customer_id, usage_history))
				if len(check_customer_records) >= int(discount.limitation_count):
					return {'status': 'failed', 'message': frappe._('You have tried this coupon for maximum times')}
	
	currency_name = get_settings_value('Catalog Settings', 'default_currency')
	currency = frappe.db.get_value('Currency', currency_name, 'symbol')
	order_by_fields = '"Limit to role", "Has any one product in cart", "Has all these products in cart", "Spend x amount", \
		"Specific price range", "Specific Shipping Method", "Specific Payment Method", "Spend x weight"'
	requirements = frappe.db.sql('''SELECT name, discount_requirement, amount_to_be_spent, min_amount, 
										max_amount, weight_for_discount, items_list 
									FROM `tabDiscount Requirements` 
									WHERE parent = %(parent)s 
										AND parenttype = "Discounts" 
									ORDER BY field (discount_requirement, {fields})
								'''.format(fields=order_by_fields),{'parent': discount.name}, as_dict=1)

	if requirements:
		return validate_item_requirements(requirements,subtotal,total_weight,customer_id,cart_items,msg,payment_method,currency)
	return {'status':'success'}


def get_usage_history(discount):
	condition = ''
	if discount.start_date and discount.end_date:
		condition += ' AND date(creation) BETWEEN cast("{0}" AS date) AND cast("{1}" AS date)'.\
								format(discount.start_date, discount.end_date)
	elif discount.start_date and not discount.end_date:
		condition += ' AND date(creation) >= cast(%(start_date)s AS date)'
	return frappe.db.sql('''SELECT order_id, customer 
							FROM `tabDiscount Usage History` 
							WHERE parent = %(parent)s {0}
						'''.format(condition),{'parent': discount.name, 
												'start_date': discount.start_date}, as_dict=1)


@frappe.whitelist(allow_guest=True)
def get_coupon_code(coupon_code, subtotal, customer_id, cart_items,discount_type=None, 
					shipping_method=None, payment_method=None,total_weight=0,shipping_charges=0):
	out = {}
	today_date = get_today_date(replace=True)
	product_array = ",".join(['"' + i.product + '"' for i in cart_items])
	cartitems = [i.product for i in cart_items if i.product]
	cartattrubutes = [i.attribute_ids.replace("\n", "") for i in cart_items if i.attribute_ids]
	rule = get_coupon_code_from_discount_rule(product_array,coupon_code,today_date)
	frappe.log_error("rule",rule)
	if rule:	
		out = get_coupon_code_by_rule(out,rule, discount_type, subtotal,customer_id, 
										cart_items,total_weight,shipping_method, 
										payment_method,cartitems,cartattrubutes)
		frappe.log_error("OUTTTTTTTTTT", out)
	else:
		if shipping_charges:
			if flt(shipping_charges)>0:
				check_shipping_discount = check_delivery_charge_discount(customer_id, subtotal,
											cart_items, flt(shipping_charges),
											shipping_method, out=out, payment_method=payment_method,
											is_coupon_code=1,coupon_code=coupon_code)
				if check_shipping_discount:
					out['discount_rule'] = check_shipping_discount.get("shipping_discount_id")
					out['shipping_discount'] = check_shipping_discount.get("shipping_discount")
					out['shipping_charges'] = check_shipping_discount.get("shipping_charges")
					out['shipping_label'] = check_shipping_discount.get("shipping_label")
					return out
		out['status'] = 'failed'
		out['message'] = frappe._('Coupon code entered is not valid.')
	return out


def validate_birthday_club(customer_id):
	allow = 0
	from datetime import date
	todays_date = date.today()
	from ecommerce_business_store_singlevendor.utils.setup import get_settings
	birthday_club_settings = get_settings('BirthDay Club Setting')
	if birthday_club_settings:
		if birthday_club_settings.beneficiary_method == "Discount":
			customer = frappe.get_doc("Customers",customer_id)
			members = frappe.db.sql("""SELECT B.email, B.day, B.month, C.name AS `customer_id` 
										FROM `tabBirthDay Club Member` B
										INNER JOIN `tabCustomers` C ON C.email = B.email 
										INNER JOIN `tabHas Role` R ON R.parent=B.email 
										WHERE R.role='BirthDay Club Member' 
											AND B.email = %(customer_email)s
									""", {'customer_email': customer.email}, as_dict=1)
			for x in members:
				from datetime import datetime
				birth_day  = getdate(datetime(todays_date.year, month_string_to_number(x.month.lower()), x.day, 00, 00, 00))
				allow = 0
				if birthday_club_settings.before_days > 0 and birthday_club_settings.after_days>0:
					start_date = add_days(birth_day,-1*birthday_club_settings.before_days)
					end_date = add_days(birth_day,birthday_club_settings.after_days)
					if todays_date>=start_date and todays_date<=end_date:
						allow = 1
				elif birthday_club_settings.before_days > 0:
					start_date = add_days(birth_day,-1*birthday_club_settings.before_days)
					if todays_date>=start_date:
						allow = 1
				elif birthday_club_settings.after_days>0:
					end_date = add_days(birth_day,birthday_club_settings.after_days)
					if todays_date<=end_date:
						allow = 1
				else:
					start_date = getdate(datetime(
													todays_date.year, 
													month_string_to_number(x.month.lower()), 
													1, 
													00, 
													00, 
													00
												))
					from frappe.utils import date_diff
					date_diff = date_diff(getdate(birth_day), getdate())
					if date_diff ==  birthday_club_settings.before_days:
						allow = 1
	return allow


@frappe.whitelist()
def delete_item(name):
	doc = frappe.get_doc("Discount Products", name)
	doc.delete()
	return "success"


def check_product_discounts(cart_items, customer_id, shipping_method = None, payment_method = None,
							order = None, subtotal = None, out = None,   total_weight = None):
	html = "check_product_discounts"+"\n"
	products_list = ''
	if order:
		order_info = frappe.get_doc('Order', order)
		subtotal = order_info.get('order_subtotal')
	for item in cart_items:
		html +=" item: "+str(item)+"\n"
		allow = True
		if order and item.get('order_item_type') != 'Product':
			allow = False
		html +=" ---------------\n"
		if allow:
			if frappe.db.get_value('Product', (item.get('product') or item.get('item'))):
				product_details = frappe.get_doc('Product', (item.get('product') or item.get('item')))
			elif frappe.db.get_value('Service', (item.get('product') or item.get('item'))):
				product_details = frappe.get_doc('Service', (item.get('product') or item.get('item')))
			html += "item.get('discount_rule') : "+str(item.get('discount_rule'))+"\n"
			html += "item.get('discount') : "+str(item.get('discount'))+"\n"
			_discount_id = item.get('discount_rule') or item.get('discount')
			html +=" _discount_id:  "+str(_discount_id)+"\n"			
			if _discount_id and frappe.db.get_value('Discounts', _discount_id):
				data = check_product_discount_by_id(
													_discount_id,
													customer_id,
													subtotal,
													total_weight, 
													shipping_method,
													payment_method,
													item,
													order,
													html
												)
				if data:
					products_list = data
	if out or out == {}:
		if not out.get("type") or (out.get("type") and out.get("type")=="Product"):		
			out['product_discount'] = 1
			out['products_list'] = products_list
		return out


def calculate_discount(discount, product, qty, rate, attribute_id = None, attribute_description = None):
	out = {}
	allow = True
	if discount.min_qty > 0 and cint(qty) < cint(discount.min_qty):
		allow = False
	if discount.max_qty > 0 and cint(qty) > cint(discount.max_qty):
		allow = False
	if allow:
		out = calculate_discount_out(
										discount,
										rate,
										out,
										product,
										attribute_id,
										attribute_description,
										qty
									)
	products_list = []
	item_info = {}
	if out and out.get('discount'):
		item_info = {'product': product, 'discount': out['discount'], 'type': 'Price', 'discount_name': discount.name}
		products_list.append(item_info)
	elif out and out.get('free_item') and discount.price_or_product_discount == 'Product':
		products_list  = calculate_discount_out_(discount,out,qty,products_list)
	elif out and out.get('cashback'):
		item_info = {'product': product, 'cashback': out['cashback_amount'], 'type': 'Cashback', 'discount_name': discount.name}
		products_list.append(item_info)
	return products_list


def check_delivery_charge_discount(
									customer_id, 
									subtotal, 
									cart_items, 
									shipping_charges, 
									shipping_method, 
									out,
									payment_method = None, 
									is_coupon_code = 0,
									coupon_code = None
								):
	today_date = get_today_date(replace=True)
	discounts = frappe.db.sql('''SELECT D.* 
								FROM `tabDiscounts` AS D
								WHERE (CASE WHEN start_date IS NOT NULL THEN start_date <= %(today)s
										ELSE 1 = 1 END) 
									AND (CASE WHEN end_date IS NOT NULL THEN end_date >= %(today)s
										ELSE 1 = 1 END) 
									AND D.discount_type = "Assigned to Delivery Charges" 
									AND requires_coupon_code = 0
								ORDER BY priority DESC
							''', {'today': getdate(today_date)}, as_dict=1)

	if is_coupon_code == 1:
		discounts = frappe.db.sql('''SELECT D.* 
									FROM `tabDiscounts` AS D
									WHERE (CASE WHEN start_date IS NOT NULL THEN start_date <= %(today)s
											ELSE 1 = 1 END) 
										AND (CASE WHEN end_date IS NOT NULL THEN end_date >= %(today)s
											ELSE 1 = 1 END) 
										AND D.discount_type = "Assigned to Delivery Charges" 
										AND requires_coupon_code = 1 
										AND coupon_code = %(coupon_code)s
									ORDER BY priority DESC
								''', {'today': getdate(today_date),"coupon_code":coupon_code}, as_dict=1)
	if discounts:
		out = check_delivery_charge_discount_(
												discounts,
												customer_id,
												cart_items,
												shipping_method,
												payment_method,
												subtotal,
												shipping_charges,
												out
											)
	return out


@frappe.whitelist()
def save_as_template(discount, title):
	from frappe.model.mapper import get_mapped_doc
	doc = get_mapped_doc("Discounts", discount, {
		"Discounts": {
			"doctype": "Discount Template"
		},
		"Discount Requirements":{
			"doctype": "Discount Requirements"
		}
	}, None, ignore_permissions=True)
	doc.name1 = title
	doc.save(ignore_permissions=True)
	return doc

@frappe.whitelist()
def update_cart():
	carts = frappe.db.sql_list('''
				SELECT C.name
				FROM `tabShopping Cart` C
				WHERE EXISTS (SELECT I.name FROM `tabCart Items` I WHERE I.parent = C.name)
			''')


	if carts:
		for item in carts:
			doc = frappe.get_doc('Shopping Cart', item)
			doc.flags.update({'__update': True})
			doc.save(ignore_permissions=True)


@frappe.whitelist()
def get_products(doctype, txt, searchfield, start, page_len, filters):
	condition = ""
	if txt:
		condition += ' and (name like "%{txt}%" or item like "%{txt}%")'.format(txt = txt)
	return frappe.db.sql('''
				SELECT name, item 
				FROM `tabProduct` 
				WHERE status = "Approved"
			''')


def get_query_condition(user):
	if not user: user = frappe.session.user
	if "System Manager" in frappe.get_roles(user):
		return None

	if "Manager" in frappe.get_roles(user) or "Vendor" in frappe.get_roles(user):
		user_info = frappe.db.sql('''
						SELECT restaurant 
						FROM `tabShop User` 
						WHERE name = %(name)s
					''', {'name': user}, as_dict=1)

		if user_info and user_info[0].restaurant:
			user_query = ''
			if "Vendor" in frappe.get_roles(user):
				return '''(`tabDiscounts`.owner = "{0}")'''.format(user)
			else:
				users_list = frappe.db.sql_list('''
								SELECT name 
								FROM `tabShop User` 
								WHERE restaurant = %(restaurant)s
							''', {'restaurant': user_info[0].restaurant})

				if users_list:
					user_query = ','.join([('"' + x + '"') for x in users_list])
				else:
					user_query = '"{0}"'.format(user)
				return '''(`tabDiscounts`.owner in ({0}))'''.format(user_query)
		else:
			return '''(`tabDiscounts`.owner = "{0}")'''.format(user)


def has_permission(doc, user):
	if "System Manager" in frappe.get_roles(user):
		return True
	
	if "Vendor" in frappe.get_roles(user):
		if doc.owner == user:
			return True
		else:
			return False
	if "Manager" in frappe.get_roles(user):
		user_info = frappe.db.sql('''
			SELECT restaurant 
			FROM `tabShop User` 
			WHERE name = %(name)s
		''', {'name': user}, as_dict=1)
		if user_info and user_info[0].restaurant:
			users_list = frappe.db.sql_list('''
						SELECT name 
						FROM `tabShop User` 
						WHERE restaurant = %(restaurant)s
					''', {'restaurant': user_info[0].restaurant})
			if doc.owner in users_list:
				return True
			else:
				return False
	return True


def check_guest_customer(customer):
	check_customer = frappe.db.get_all('Customers', 
									filters={'name': customer}, 
									fields=['naming_series'])
	if check_customer and check_customer[0].naming_series == 'GC-':
		return True

	return False


def update_customer_wallet(order_info):
	is_guest_customer = check_guest_customer(order_info.customer)
	if not is_guest_customer:
		check_subtotal_cashback(order_info)
		check_product_cashback(order_info)


def check_subtotal_cashback(order_info):
	check_discounts = frappe.db.sql('''SELECT D.* 
										FROM `tabDiscounts` D 
										LEFT JOIN `tabDiscount Usage History` H ON D.name = H.parent 
										WHERE H.order_id = %(order_id)s 
											AND D.price_or_product_discount = "Cashback"
									''', {'order_id': order_info.name}, as_dict=1)
	if check_discounts:
		for item in check_discounts:
			notes = 'Cashback Against Discount: {0}'.format(item.name)
			check_wallet = check_wallet_transaction_entry(order_info, notes)
			if not check_wallet:
				cashback = 0
				if item.cashback_type == 'Percentage':
					cashback = (flt(order_info.order_subtotal) * flt(item.cashback_percentage) / 100)
					if item.max_cashback_amount and int(item.max_cashback_amount) > 0 and cashback > int(item.max_cashback_amount):
						cashback = item.max_cashback_amount
				else:
					cashback = flt(item.cashback_amount)
				if cashback > 0:
					update_wallet_transaction(order_info, item, notes, cashback)


def check_product_cashback(order_info):
	for item in order_info.order_item:
		if item.get('discount'):
			check_discounts = frappe.db.sql('''SELECT * 
												FROM `tabDiscounts` 
												WHERE name = %(order_id)s 
													AND price_or_product_discount = "Cashback"
											''', {'order_id': item.get('discount')}, as_dict=1)
			if check_discounts:
				notes = 'Cashback For {0}: {1}'.format(item.order_item_type, item.item)
				check_wallet = check_wallet_transaction_entry(order_info, notes)
				if not check_wallet:
					cashback = 0
					if check_discounts[0].cashback_type == 'Percentage':
						cashback = (flt(item.amount) * flt(check_discounts[0].cashback_percentage) / 100)
						max_cashback = check_discounts[0].max_cashback_amount
						if max_cashback and int(max_cashback) > 0 and cashback > int(max_cashback):
							cashback = max_cashback
					else:
						cashback = flt(check_discounts[0].cashback_amount)
					if cashback > 0:
						update_wallet_transaction(order_info, check_discounts[0], notes, cashback)


def check_wallet_transaction_entry(order_info, notes):
	return frappe.db.get_all('Wallet Transaction', filters = {
																'type': 'Customers', 
																'party': order_info.customer, 
																'order_type': 'Order', 
																'order_id': order_info.name, 
																'transaction_type': 'Pay', 
																'notes': notes
															})


def update_wallet_transaction(order_info, discount, notes, cashback):
	from ecommerce_business_store_singlevendor.accounts.api import insert_wallet_transaction
	end_date = None
	if discount.set_cashback_expiry and discount.expires_after and int(discount.expires_after) > 0:
		end_date = frappe.utils.add_days(getdate(nowdate()), int(discount.expires_after))
	doc = {
			'reference': 'Order', 
			'order_type': 'Order',
			'order_id': order_info.name, 
			'amount': cashback,
			'total_value': order_info.total_amount, 
			'disabled': 0,
			'notes': notes, 
			'party_type': 'Customers', 
			'party': order_info.customer, 
			'transaction_type': 'Pay', 
			'status': 'Credited',
			'is_paid': 0, 
			'start_date': getdate(nowdate()), 
			'end_date': end_date
		}
	res = insert_wallet_transaction(doc)
	return res


@frappe.whitelist()
def get_shopping_cart_settings():
	from ecommerce_business_store_singlevendor.utils.setup import get_settings
	return get_settings('Shopping Cart Settings')


@frappe.whitelist()
def get_product_attribute(product):
	from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.\
		product.product import get_product_attribute_options
	attributes=frappe.db.get_all('Product Attribute Mapping',
									filters = {'parent':product},
									fields = [
												'name',
												'product_attribute',
												'is_required',
												'control_type',
												'attribute_unique_name', 
												'attribute'
											],
									order_by = 'display_order')
	if attributes:
		for item in attributes:
			item.options=get_product_attribute_options(item.product_attribute,product,item.name)			
	return attributes


def month_string_to_number(string):
	m = {
		'jan': 1,
		'feb': 2,
		'mar': 3,
		'apr': 4,
		'may': 5,
		'jun': 6,
		'jul': 7,
		'aug': 8,
		'sep': 9,
		'oct': 10,
		'nov': 11,
		'dec': 12
		}
	s = string.strip()[:3].lower()
	try:
		out = m[s]
		return out
	except:
		raise ValueError('Not a month')


def get_product_discount_attr_items(disc,product,attribute_id,out):
	price = frappe.db.get_value('Product', disc.product,'price')
	all_attr = frappe.db.sql('''SELECT (IFNULL(O.price_adjustment, 0) + IFNULL(PDT.price, 0)) AS rate, 
									O.option_value, P.attribute,O.name AS optionid, 
									P.name AS attributeid, P.parent 
								FROM `tabProduct Attribute Option` O 
								LEFT JOIN `tabProduct Attribute Mapping` P ON P.name = O.attribute_id 
								LEFT JOIN `tabProduct` PDT ON PDT.name = P.parent 
								WHERE O.parent = %(parent)s
							''', {'parent': disc.product}, as_dict=1)
	attr_items = json.loads(disc.product_attribute_json)
	discount_item = {}
	if len(attr_items)>0:
		for attr in attr_items:
			attr_name = attr['name'].split('-')
			attribute_ids = attr_name[1]
			options = frappe.db.sql('''SELECT O.price_adjustment, O.option_value, P.attribute 
										FROM `tabProduct Attribute Option` O 
										LEFT JOIN `tabProduct Attribute Mapping` P 
											ON P.name = O.attribute_id 
										WHERE O.name = %(name)s 
											AND O.parent = %(parent)s
									''', {'name': attribute_ids, 'parent': disc.product}, as_dict=1)
			if options:
				price = float(price) + float(options[0].price_adjustment)
			if disc.product==product.name and attribute_ids==attribute_id:
				discount_item = disc
				discount_item["rate"]=price
				allow = True
				break	
	else:
		if all_attr:
			min_attr = min(all_attr, key=lambda x: x.rate)
			if min_attr:
				price = float(min_attr.rate)
				discount_item = min_attr
				discount_item["rate"]=price
		else:
			discount_item = disc
			discount_item["rate"]=price
	if discount_item:
		if disc.discount_type == 'Discount Percentage':
			discount_amt = (flt(discount_item.rate) * flt(disc.discount_percentage) / 100)
		else:
			discount_amt = discount_item.discount_amount
		out['discount_amount'] = flt(discount_amt)* cint(disc.qty)
		out['rate'] = flt(discount_item.rate) - flt(discount_amt)
		out['total'] = flt(out['rate']) * cint(disc.qty)
	return out


def check_attr_items(attr_items, item_info, dis_list,disc):
	for attr in attr_items:
		attr_name = attr['name'].split('-')
		attribute_ids = attr_name[1]
		html = ''
		options = frappe.db.sql('''SELECT O.price_adjustment, O.option_value, P.attribute 
									FROM `tabProduct Attribute Option` O 
									LEFT JOIN `tabProduct Attribute Mapping` P 
										ON P.name = O.attribute_id 
									WHERE O.name = %(name)s 
										AND O.parent = %(parent)s
								''', {'name': attribute_ids, 'parent': disc.product}, as_dict=1)
		if options:
			html += '<div class="cart-attributes"><span class="attr-title">'+options[0].attribute+ \
				' </span> : <span>'+options[0].option_value+'</span></div>'
			price = float(price) + float(options[0].price_adjustment)
		item_info['price'] = price
		item_info['attribute_ids'] = attribute_ids
		item_info['attribute_description'] = html
		dis_list.append(item_info)


def check_not_attr_items(all_attr, item_info, dis_list, disc):
	if all_attr:
		min_attr = min(all_attr, key=lambda x: x.rate)
		if min_attr:
			html = ''
			options = frappe.db.sql('''SELECT O.price_adjustment, O.option_value, P.attribute 
										FROM `tabProduct Attribute Option` O 
										LEFT JOIN `tabProduct Attribute Mapping` P 
											ON P.name = O.attribute_id 
										WHERE O.name = %(name)s AND O.parent = %(parent)s
									''', {'name': min_attr.optionid, 'parent': disc.product}, as_dict=1)
			if options:
				html += '<div class="cart-attributes"><span class="attr-title">'+ \
					options[0].attribute+' </span> : <span>'+options[0].option_value+'</span></div>'
				price = float(price) + float(options[0].price_adjustment)
			item_info['price'] = price
			item_info['attribute_ids'] = min_attr.optionid
			item_info['attribute_description'] = html
	dis_list.append(item_info)


def get_product_discount_items(discount,dis_list,out):
	for disc in discount.free_items:
		item_name, price, route = frappe.db.get_value('Product', disc.product, ['item', 'price', 'route'])
		item_info = {
		'free_item': disc.product,
		'free_qty': disc.qty
		}
		all_attr = frappe.db.sql('''SELECT (IFNULL(O.price_adjustment, 0) + IFNULL(PDT.price, 0)) AS rate, 
										O.option_value,P.attribute,O.name AS optionid,
										P.name AS attributeid
									FROM `tabProduct Attribute Option` O
									LEFT JOIN `tabProduct Attribute Mapping` P 
										ON P.name = O.attribute_id
									LEFT JOIN `tabProduct` PDT 
										ON PDT.name = P.parent
									WHERE O.parent = %(parent)s
								''', {'parent': disc.product}, as_dict=1)

		attr_items = json.loads(disc.product_attribute_json)
		if len(attr_items)>0:
			check_attr_items(attr_items, item_info, disc)
		else:
			check_not_attr_items(all_attr, item_info, dis_list, disc)
	out['same_product'] = 0
	out['products_list'] = dis_list
	out['free_item'] = 1
	return out


def get_product_discount_by_product(discount,product,attribute_id,out):
	if discount.same_product:
		dis_list=[]
		out['free_item'] = product.get("name")
		out['free_qty'] = discount.free_qty
		out['same_product'] = 1
		price = frappe.db.get_value('Product', product.get("name"),'price')
		item_info = {
						'free_item': product.get("name"),
						'price' : price,
						'free_qty': discount.free_qty
					}
		if attribute_id:
			html = ''
			options = frappe.db.sql('''SELECT O.price_adjustment, O.option_value, P.attribute 
										FROM `tabProduct Attribute Option` O 
										LEFT JOIN `tabProduct Attribute Mapping` P 
											ON P.name = O.attribute_id 
										WHERE O.name = %(name)s AND O.parent = %(parent)s
									''', {'name': attribute_id, 'parent': product.get("name")}, as_dict=1)
			if options:
				html += '<div class="cart-attributes"><span class="attr-title">'+ \
					options[0].attribute+' </span> : <span>'+options[0].option_value+'</span></div>'
				price = float(price) + float(options[0].price_adjustment)
			item_info['price'] = price
			item_info['attribute_ids'] = attribute_id
			item_info['attribute_description'] = html
		dis_list.append(item_info)
		out['products_list'] = dis_list
	else:
		dis_list = []
		discount.non_free = frappe.db.sql('''SELECT product, product_attribute, qty, product_attribute_json, 
												discount_type, discount_amount, discount_percentage 
											FROM `tabDiscount Applied Product` 
											WHERE parent = %(parent)s 
												AND (discount_type="Discount Percentage" 
													OR discount_type="Discount Amount")
										''', {'parent': discount.name}, as_dict=1)
		for disc in discount.non_free:
			if disc.product==product.name:
				out = get_product_discount_attr_items(disc,product,attribute_id,out)
		discount.free_items = frappe.db.sql('''SELECT product, product_attribute, qty, 
													product_attribute_json, discount_type, 
													discount_amount, discount_percentage 
												FROM `tabDiscount Applied Product` 
												WHERE parent = %(parent)s 
													AND (discount_type!="Discount Percentage" 
													AND discount_type!="Discount Amount")
											''', {'parent': discount.name}, as_dict=1)
		if discount.free_items and len(discount.free_items) > 0:
			out = get_product_discount_items(discount,dis_list,out)
	out['min_qty'] = discount.min_qty
	return out


def allowed_discount_percentage(allowed_discount,out,currency,req_data):
	if allowed_discount.percent_or_amount == 'Discount Percentage':
		if allowed_discount.min_qty > 1:
			out['discount_label'] = 'Buy {0} Get {1}% off {2}'.format(
																	allowed_discount.min_qty,
																	allowed_discount.discount_percentage, 
																	req_data
																)
		else:
			out['discount_label'] = '{0}% Off {1}'.format(
														allowed_discount.discount_percentage, 
														req_data
														)
	else:
		if allowed_discount.min_qty > 1:
			out['discount_label'] = 'Buy {0} Get Flat {1}{2} off {3}'.format(
																	allowed_discount.min_qty,
																	currency,
																	allowed_discount.discount_amount, 
																	req_data
																)
		else:
			out['discount_label'] = 'Flat {0}{1} Off {2}'.format(
																currency, 
																allowed_discount.discount_amount, 
																req_data
															)


def get_product_allowed_discount(allowed_discount,out,currency,req_data):
	if allowed_discount.price_or_product_discount == 'Price':			
		allowed_discount_percentage(allowed_discount,out,currency,req_data)

	elif allowed_discount.price_or_product_discount == 'Product':
		if allowed_discount.same_product:
			out['discount_label'] = 'Buy {0} Get {1} Free {2}'.format(
																		allowed_discount.min_qty,
																		allowed_discount.free_qty, 
																		req_data
																	)
		else:
			item = None
			if allowed_discount.free_product:
				item = frappe.db.get_value('Product', allowed_discount.free_product, 'item')
			else:
				
				if(allowed_discount.get("free_items")):
					item = str(allowed_discount.get("free_items")[0].qty)+" Item"
			if item:	
				out['discount_label'] = 'Buy {0} Get {1} Free {2}'.format(
																			allowed_discount.min_qty, 
																			item, 
                   															req_data
																		)
	elif allowed_discount.price_or_product_discount == 'Cashback':
		qty_txt = ''
		if allowed_discount.min_qty > 1:
			qty_txt = 'Buy {0} and Get '.format(allowed_discount.min_qty)
		if allowed_discount.cashback_type == 'Percentage':
			out['discount_label'] = '{0}{1}% Cashback {2}'.format(
													qty_txt, 
													format_value(allowed_discount.cashback_percentage),
													req_data
												)
		else:
			out['discount_label'] = '{0}Flat {1} Cashback {2}'.format(
													qty_txt, 
													fmt_money(allowed_discount.cashback_amount),
													req_data
												)
	out['discount_rule'] = allowed_discount.name
	return out


def get_product_discount_list(discounts_list,qty,customer_id,rate,product,attribute_id,allowed_discount):
	out = {}
	for discount in discounts_list:
		allow = True
		if discount.min_qty > 0 and cint(qty) < cint(discount.min_qty):
			allow = False
		if discount.max_qty > 0 and cint(qty) > cint(discount.max_qty):
			allow = False
		if allow:
			if discount.limitations != 'Unlimited':
				if discount.limitations == 'N times only':
					if int(discount.limitation_count) <= int(discount.history):
						allow = False
				else:
					if customer_id:
						history = get_usage_history(discount)
						usage_history = list(filter(lambda x: x.customer == customer_id, history))

						if usage_history:
							if len(usage_history) >= int(discount.limitation_count):
								allow = False
		if allow:
			if not flt(discount.requirements) > 0:
				if discount.price_or_product_discount == 'Price':
					if discount.percent_or_amount == 'Discount Percentage':
						discount_amt = ((flt(rate) if rate else flt(product.get("price"))) * \
								flt(discount.discount_percentage) / 100)
					else:
						discount_amt = discount.discount_amount
					# frappe.log_error("--entered-->",discount_amt)
					out['discount_amount'] = flt(discount_amt)
					out['rate'] = (flt(rate) if rate else flt(product.get("price"))) - flt(discount_amt)
					out['total'] = flt(out['rate']) * cint(qty)
				elif discount.price_or_product_discount == 'Product':
					out = get_product_discount_by_product(discount,product,attribute_id,out)
			break
	return out


def get_product_discount_requirement(discounts_list,qty,
									customer_id,rate,
									product,attribute_id,
									currency,allowed_discount
									):
	out = get_product_discount_list(
										discounts_list,
										qty,
										customer_id,
										rate,product,
										attribute_id,
										allowed_discount
									)
	if not allowed_discount and len(discounts_list) > 0:
		allowed_discount = discounts_list[0]
	if allowed_discount:
		req_data = ''
		if flt(allowed_discount.requirements) == 1:
			requirement = frappe.db.sql('''SELECT discount_requirement, items_list, min_amount, 
												max_amount 
											FROM `tabDiscount Requirements` 
											WHERE parent = %(PARENT)s
										''', {'PARENT': allowed_discount.name}, as_dict=1)
			if requirement and requirement[0].discount_requirement == "Specific Shipping Method":
				items_list = json.loads(requirement[0].items_list)
				req_data = ' on {0}'.format(items_list[0].get('item_name'))
		out = get_product_allowed_discount(allowed_discount,out,currency,req_data)
	return out


def check_delivery_charge_discount_reqs(
										reqs,
                                        shipping_method,
                                        customer_id,
                                        payment_method,
                                        subtotal,
                                        condition_passed = 0
									):
	user_id = frappe.db.get_value('Customers', customer_id, 'user_id')
	for item in reqs:
		if shipping_method and item.discount_requirement == 'Specific Shipping Method':
			items = json.loads(item.items_list)
			items_list = [i.get('item') for i in items]
			if shipping_method in items_list:
				condition_passed = condition_passed + 1
		if item.discount_requirement == 'Specific Payment Method' and payment_method:
			items = json.loads(item.items_list)
			items_list = [i.get('item') for i in items]
			if payment_method in items_list:
				condition_passed = condition_passed + 1
		if item.discount_requirement == 'Limit to role' and user_id:
			items = json.loads(item.items_list)
			items_list = [i.get('item') for i in items]
			check_role = list(frappe.utils.has_common(frappe.get_roles(user_id), items_list))
			if check_role and len(check_role) == len(items_list):
				condition_passed = condition_passed + 1
		if item.discount_requirement == 'Spend x amount':
			if item.amount_to_be_spent and float(subtotal) >= float(item.amount_to_be_spent):
				condition_passed = condition_passed + 1
	return condition_passed

def check_delivery_charge_discount_(
										discounts,
										customer_id,
										cart_items,
										shipping_method,
										payment_method,
										subtotal,
										shipping_charges,
										out
									):
	for discount in discounts:
		condition_passed = 0
		reqs = frappe.db.get_all('Discount Requirements', 
						   fields=['name', 'discount_requirement', 'items_list', 'amount_to_be_spent'],
						   filters={'parent': discount.name})
		qty_count = sum(x.get('quantity') for x in cart_items) if cart_items else 0
		if discount.min_qty > 0 and int(discount.min_qty) > int(qty_count):
			return
		if discount.max_qty > 0 and int(discount.max_qty) < int(qty_count):
			return
		if discount.limitations and discount.limitations != 'Unlimited':				
			if discount.limitations == 'N times only':
				history = get_usage_history(discount)
				if int(discount.limitation_count) <= len(history):
					break
			elif frappe.session.user != 'Guest':
				usage = get_usage_history(discount)
				history = list(filter(lambda x: x.customer == customer_id, usage))
				if int(discount.limitation_count) <= len(history):
					break
		if reqs:
			condition_passed = check_delivery_charge_discount_reqs(
																	reqs,
																	shipping_method,
																	customer_id,
																	payment_method,
																	subtotal,
																	condition_passed = 0
																)
		if len(reqs) == condition_passed:
			charges = 0
			if discount.percent_or_amount == 'Discount Percentage':
				amt = float(shipping_charges) * float(discount.discount_percentage) / 100
				charges = float(shipping_charges) - amt
			else:
				if float(shipping_charges) >= float(discount.discount_amount):
					charges = float(shipping_charges) - float(discount.discount_amount)
			out['shipping_discount'] = 1
			out['shipping_charges'] = math.ceil(charges * 100) / 100
			out['shipping_discount_id'] = discount.name
			if charges == 0:
				out['shipping_label'] = _('Free Delivery')
			tax = 0
			out['shipping_tax'] = tax
			break
	return out


def get_coupon_code_by_apply_discount(products_list,apply_discount):
	for disc in apply_discount:
		free_qty = int(disc.qty)
		item_name, price, route= frappe.db.get_value('Product', disc.product, ['item', 'price', 'route'])
		image = frappe.db.sql('''SELECT IFNULL(mini_cart, '') AS image 
								FROM `tabProduct Image` 
								WHERE parent = %(parent)s 
								ORDER BY is_primary DESC 
								LIMIT 1
							''', {'parent': disc.product}, as_dict=1)
		if image:
			image = image[0].image
		item_info = {
						'product': disc.product, 
						'product_name': item_name, 
						'price': price, 
						'quantity': free_qty,
						'route': route,
						'image': image,
						'attribute_ids': None,
						'attribute_description': None,
						'type': 'Product'
					}
		attr_items = json.loads(disc.product_attribute_json)
		if len(attr_items)>0:
			for attr in attr_items:
				attr_name = attr['name'].split('-')
				attribute_ids = attr_name[1]
				html = ''
				options = frappe.db.sql('''SELECT O.price_adjustment, O.option_value, P.attribute 
											FROM `tabProduct Attribute Option` O 
											LEFT JOIN `tabProduct Attribute Mapping` P 
												ON P.name = O.attribute_id 
											WHERE O.name = %(name)s 
												AND O.parent = %(parent)s
										''', {'name': attribute_ids, 'parent': disc.product}, as_dict=1)

				if options:
					html += '<div class="cart-attributes"><span class="attr-title">'+ \
						options[0].attribute+' </span> : <span>'+options[0].option_value+'</span></div>'
					price = float(price) + float(options[0].price_adjustment)
				item_info['price'] = price
				item_info['attribute_ids'] = attribute_ids
				item_info['attribute_description'] = html
				products_list.append(item_info)
		else:
			products_list.append(item_info)
	return products_list
		

def get_coupon_code_price_or_product_discount(out,discount,cart_items,cartitems,cartattrubutes):
	products_list = []
	out['free_item'] = 1
	out['min_qty'] = discount.min_qty
	added_product=[]
	added_attribute=[]
	condition_products = frappe.db.sql(f''' SELECT *
											FROM `tabDiscount Products`
											WHERE parent = %(parent)s''',{'parent': discount.name}, as_dict=1)
	for x in condition_products: 
		if x.items: added_product.append(x.get('items'))
		if x.product_attribute_json: 
			attr_items = json.loads(x.product_attribute_json)
			for atr in attr_items:
				attr_name = atr['name'].split('-')
				attribute_ids = attr_name[1]
				added_attribute.append(attribute_ids)
	nonfree_product_item = frappe.db.sql('''SELECT product, product_attribute, qty, 
												product_attribute_json, discount_type, discount_amount,
												discount_percentage
											FROM `tabDiscount Applied Product`
											WHERE parent = %(parent)s 
												AND (discount_type = "Discount Percentage" 
												OR discount_type = "Discount Amount")
										''', {'parent': discount.name}, as_dict=1)
	freeitems =[]
	for x in nonfree_product_item: 
		if x.product: freeitems.append(x.product)
	ht = str(added_product) +": added_product\n"
	ht += str(added_attribute)+": added_attribute\n"
	ht += str(cartitems)+": cartitems\n"
	ht += str(cartattrubutes) +": cartattrubutes\n"
	data = get_coupon_code_price_or_product_discount_(
														nonfree_product_item,
														added_product,
														cartitems,
														cartattrubutes,
														cart_items
													)
	if data:
		return data
	apply_discount = frappe.db.sql('''SELECT product, product_attribute, qty, product_attribute_json, 
											discount_type, discount_amount, discount_percentage 
										FROM 
											`tabDiscount Applied Product` 
										WHERE 
											parent = %(parent)s 
											AND (discount_type!="Discount Percentage" 
											AND discount_type!="Discount Amount")
									''', {'parent': discount.name}, as_dict=1)
	if apply_discount and len(apply_discount) > 0:
		products_list = get_coupon_code_by_apply_discount(products_list,apply_discount)
	out['products_list'] = products_list
	return out


def get_coupon_code_by_rule(out,rule, discount_type, subtotal, customer_id, cart_items, total_weight, 
							shipping_method, payment_method,cartitems,cartattrubutes):
	discount = rule[0]
	if discount_type == 'remove':
		res = { 'status': 'success' }
	else:
		res = validate_requirements(
									discount, 
									subtotal, 
									customer_id, 
									cart_items, 
									total_weight,
									shipping_method, 
									payment_method
								)
	if discount.is_birthday_club_discount == 1:
		check_allow = validate_birthday_club(customer_id)
		if check_allow == 0:
			res['status'] = 'failed'
			res['message'] = frappe._('Coupon code entered is not valid.')
	if res['status'] == 'success':
		out['discount_rule'] = discount.name
		if discount.price_or_product_discount == 'Price':
			if discount.percent_or_amount == 'Discount Percentage':
				discount_amt = (flt(subtotal) * flt(discount.discount_percentage) / 100)
				if discount.max_discount_amount > 0 and discount_amt > discount.max_discount_amount:
					discount_amt = discount.max_discount_amount
			else:
				discount_amt = flt(discount.discount_amount)
			out['discount_amount'] = math.ceil(discount_amt * 100) / 100
			out['subtotal'] = flt(subtotal) - flt(discount_amt)
		elif discount.price_or_product_discount == 'Product':
			out = get_coupon_code_price_or_product_discount(
															out,
															discount,
															cart_items,
															cartitems,
															cartattrubutes
														)
		elif discount.price_or_product_discount == 'Cashback':
			out['cashback'] = 1
			cashback = 0
			if discount.cashback_type == 'Percentage':
				cashback = (flt(subtotal) * flt(discount.cashback_percentage) / 100)
				if discount.max_cashback_amount > 0 and cashback > discount.max_cashback_amount:
					cashback = discount.max_cashback_amount
			else:
				cashback = flt(discount.cashback_amount)
			out['cashback_amount'] = cashback
	else:
		out = res
	return out


def get_coupon_code_from_discount_rule(product_array,coupon_code,today_date):
	today = getdate(today_date)
	query = f'''SELECT D.* FROM `tabDiscounts` AS D
				LEFT JOIN `tabDiscount Products` AS DP ON D.name = DP.parent 
				LEFT JOIN `tabDiscount Applied Product` AS DAP ON D.name = DAP.parent  
				WHERE (CASE WHEN start_date IS NOT NULL THEN start_date <= "{today}"
						ELSE 1 = 1 END) 
					AND (CASE WHEN end_date IS NOT NULL THEN end_date >= "{today}"
						ELSE 1 = 1 END) 
					AND (D.discount_type = "Assigned to Sub Total" 
						OR (CASE WHEN D.discount_type = 'Assigned to Products'
								THEN DP.items IN ({product_array}) 
							OR DAP.product IN ({product_array})
								ELSE 1 = 1 END))
					AND requires_coupon_code = 1 
					AND coupon_code = "{coupon_code}"  
				ORDER BY priority DESC 
			'''
	rule = frappe.db.sql(query, as_dict = 1)
	return rule


def get_free_product_item(free_product_item,products_list):
	for free in free_product_item:
		attr_out = {}
		attr_out['free_item'] = free.product
		attr_out['free_qty'] = free.qty
		attr_out['min_qty'] = free.qty
		attr_out['item_name'], attr_out['price'], \
			attr_out['route'] = frappe.db.get_value('Product', free.product, ['item', 'price', 'route'])
		image = frappe.db.sql(f'''  SELECT IFNULL(mini_cart, '') AS image
									FROM `tabProduct Image`
									WHERE parent = %(parent)s
									ORDER BY is_primary DESC
									LIMIT 1 ''', {'parent': free.product}, as_dict=1)
		if image:
			attr_out['image'] = image[0].image
		attr_items = json.loads(free.product_attribute_json)
		if len(attr_items)>0:
			for atr in attr_items:
				attr_name = atr['name'].split('-')
				attribute_ids = attr_name[1]
				attr_out['attribute_ids'] = attribute_ids
				attrhtml = ''
				options = frappe.db.sql(f'''SELECT O.price_adjustment, O.option_value, P.attribute
											FROM `tabProduct Attribute Option` O
											LEFT JOIN 
		   										`tabProduct Attribute Mapping` P ON P.name = O.attribute_id
											WHERE O.name = %(name)s AND O.parent = %(parent)s
										''', {'name': attribute_ids, 'parent': free.product}, as_dict=1)
				if options:
					attrhtml += '<div class="cart-attributes"><span class="attr-title">'+options[0].attribute+ \
						' </span> : <span>'+options[0].option_value+'</span></div>'
				attr_out['attribute_description'] = attrhtml
				item_info = {
								'product': attr_out.get('free_item'), 
								'product_name': attr_out.get('item_name'), 
								'price': attr_out.get('price'), 
								'quantity': attr_out.get('free_qty'),
								'route': attr_out.get('route'),
								'image': attr_out.get('image'),
								'attribute_ids': attr_out.get('attribute_ids'),
								'attribute_description': attr_out.get('attribute_description'),
								'type': 'Product'
							}
				if item_info:
					products_list.append(item_info)
		else:
			item_info = {
							'product': attr_out.get('free_item'), 
							'product_name': attr_out.get('item_name'), 
							'price': attr_out.get('price'), 
							'quantity': attr_out.get('free_qty'),
							'route': attr_out.get('route'),
							'image': attr_out.get('image'),
							'attribute_ids': "",
							'attribute_description': "",
							'type': 'Product'
						}
			if item_info:
				products_list.append(item_info)	
	return products_list


def get_nonfree_product_item(nonfree_product_item,cart_items,subtotal,out):
	for nonfree in nonfree_product_item:
		discount_item = {}
		all_attr = frappe.db.sql('''SELECT 
										(IFNULL(O.price_adjustment, 0) + IFNULL(PDT.price, 0)) AS rate, 
										O.option_value, P.attribute, O.name AS optionid, 
										P.name AS attributeid
									FROM `tabProduct Attribute Option` O
									LEFT JOIN `tabProduct Attribute Mapping` P 
										ON P.name = O.attribute_id
									LEFT JOIN `tabProduct` PDT 
										ON PDT.name = P.parent
									WHERE O.parent = %(parent)s
								''', {'parent': nonfree.product}, as_dict=1)
		attr_items = json.loads(nonfree.product_attribute_json)
		if len(attr_items)>0:
			allow = False
			for atr in attr_items:
				attr_name = atr['name'].split('-')
				attribute_ids = attr_name[1].replace('\n','')
				nonfree_items = list(filter(lambda x: x.get('product') == nonfree.product \
									and x.get('attribute_ids').replace('\n','') == attribute_ids, \
									cart_items))
				if len(nonfree_items)>0:
					discount_item = nonfree_items
					discount_item["discount_type"]=nonfree.discount_type
					discount_item["discount_percentage"]=nonfree.discount_percentage
					discount_item["discount_amount"]=nonfree.discount_amount
					allow = True
					break	
		else:
			nonfree_items = list(filter(lambda x: x.get('product') == nonfree.product, cart_items))
			if len(nonfree_items)>0:
				if all_attr:
					min_attr = min(all_attr, key=lambda x: x.rate)
					if min_attr:
						discount_item = min_attr
						discount_item["discount_type"]=nonfree.discount_type
						discount_item["discount_percentage"]=nonfree.discount_percentage
						discount_item["discount_amount"]=nonfree.discount_amount
				else:
					discount_item = nonfree
				allow = True
			else:
				allow = False
		if allow:
			if discount_item.discount_type == 'Discount Percentage':
				discount_amt = (flt(subtotal) * flt(discount_item.discount_percentage) / 100)	
			else:
				discount_amt = flt(discount_item.discount_amount)			
			out['discount_amount'] = math.ceil(discount_amt * 100) / 100
			out['subtotal'] = flt(subtotal) - flt(discount_amt)
	return out


def get_price_or_price_product_discount(cart_items,subtotal,discount):
	nonfree_product_item= frappe.db.sql(f'''SELECT *
											FROM `tabDiscount Applied Product`
											WHERE parent = %(parent)s 
												AND (discount_type = "Discount Percentage" 
												OR discount_type = "Discount Amount")
										''', {'parent': discount.name}, as_dict=1)
	free_product_item = frappe.db.sql(f'''  SELECT *
											FROM `tabDiscount Applied Product`
											WHERE parent = %(parent)s 
												AND (discount_type != "Discount Percentage" 
												AND discount_type != "Discount Amount")
										''', {'parent': discount.name}, as_dict=1)
	free_items = []
	cart = frappe.db.exists("Shopping Cart", cart_items[0].parent)
	if not cart:
		cart = frappe.db.exists("Order", cart_items[0].parent)
		shop = frappe.get_doc("Order", cart)
		free_items = list(filter(lambda x: x.get('is_free_item') == 1, shop.order_item))
	else:
		shop = frappe.get_doc("Shopping Cart", cart)
		free_items = list(filter(lambda x: x.get('is_free_item') == 1, shop.items))
	if len(free_items)<=0:
		setattr(cart_items[0], "discount_rule", out['discount_rule'])
	out = get_nonfree_product_item(
									nonfree_product_item,
									cart_items,
									subtotal,
									out
								)
	if 	discount.same_product==1:
		pass
	else:
		products_list = get_free_product_item(
												free_product_item,
												products_list
											)
	out['products_list'] = products_list
	if len(free_items)<=0 and len(nonfree_product_item)<=0:
		return out
	return out


def get_order_subtotal_discount_assigned(discount,subtotal,cart_items):
	out = {}
	if discount.price_or_product_discount == 'Price':
		if discount.percent_or_amount == 'Discount Percentage':
			discount_amt = (flt(subtotal) * flt(discount.discount_percentage) / 100)
			if discount.max_discount_amount > 0 and discount_amt > discount.max_discount_amount:
				discount_amt = discount.max_discount_amount
		else:
			discount_amt = flt(discount.discount_amount)			
		out['discount_amount'] = math.ceil(discount_amt * 100) / 100
		out['subtotal'] = flt(subtotal) - flt(discount_amt)
	elif discount.price_or_product_discount == 'Product':
		out = get_price_or_price_product_discount(
													cart_items,
													subtotal,
													discount
												)
	elif discount.price_or_product_discount == 'Cashback':
		out['cashback'] = 1
		cashback = 0
		if discount.cashback_type == 'Percentage':
			cashback = (flt(subtotal) * flt(discount.cashback_percentage) / 100)
			if discount.max_cashback_amount > 0 and cashback > discount.max_cashback_amount:
				cashback = discount.max_cashback_amount
		else:
			cashback = flt(discount.cashback_amount)
		out['cashback_amount'] = cashback
	return out


def get_product_dixcount_rule_(rule,product):
	for discount in rule:
		if discount.discount_type == "Assigned to Categories" \
					and discount.price_or_product_discount == "Price":
			categories = get_product_categories(product.name)
			query = f'''SELECT discount_value
										FROM `tabDiscount Categories`
													WHERE category IN ({categories})
														AND parent = "{discount.name}"
												'''
			# frappe.log_error("---query-->",query)
			discount_categories = frappe.db.sql(query,as_dict=1)
			if discount_categories:
				for x in discount_categories:
					if x.discount_value:
						if flt(x.discount_value)>0:
							if discount.percent_or_amount == "Discount Percentage":
								discount.discount_percentage = flt(x.discount_value)
							else:
								discount.discount_amount = flt(x.discount_value)
			else:
				rule.remove(discount)
	return rule


def	get_ordersubtotal_discount_forfree_product_item(free_product_item,products_list):
	for disc in free_product_item:
		free_qty = int(disc.qty)
		item_name, price, route = frappe.db.get_value('Product', disc.product, ['item', 'price', 'route'])
		image = frappe.db.sql(f'''	SELECT IFNULL(mini_cart, '') AS image
									FROM `tabProduct Image`
									WHERE parent = %(parent)s
									ORDER BY is_primary DESC
									LIMIT 1 ''', {'parent': disc.product}, as_dict=1)
		if image:
			image = image[0].image
		item_info = {
						'free_item': disc.product, 
						'product_name': item_name, 
						'price': price, 
						'free_qty': free_qty,
						'route': route,
						'image': image,
						'attribute_ids': None,
						'attribute_description': None,
						'type': 'Product'
					}
		attr_items = json.loads(disc.product_attribute_json)
		if len(attr_items)>0:
			for attr in attr_items:
				attr_name = attr['name'].split('-')
				attribute_ids = attr_name[1]
				html = ''
				options = frappe.db.sql(f'''SELECT O.price_adjustment, O.option_value, P.attribute
											FROM `tabProduct Attribute Option` O
											LEFT JOIN `tabProduct Attribute Mapping` P 
												ON P.name = O.attribute_id
											WHERE O.name = %(name)s AND O.parent = %(parent)s
										''', {'name': attribute_ids, 'parent': disc.product}, as_dict=1)
				if options:
					html += '<div class="cart-attributes"><span class="attr-title">'+ \
						options[0].attribute+' </span> : <span>'+options[0].option_value+'</span></div>'
					price = float(price) + float(options[0].price_adjustment)
				attr_name = attr['name'].split('-')
				attribute_ids = attr_name[1]
				item_info['price'] = price
				item_info['attribute_ids'] = attribute_ids
				item_info['attribute_description'] = html
				products_list.append(item_info)
		else:
			products_list.append(item_info)
	return products_list


def get_ordersubtotal_discount_fornonfree_product_item(nonfree_product_item,subtotal,out,cart_items):
	for nonfree in nonfree_product_item:
		attr_items = json.loads(nonfree.product_attribute_json)
		if len(attr_items)>0:
			allow = False
			for atr in attr_items:
				attr_name = atr['name'].split('-')
				attribute_ids = attr_name[1]
				nonfree_items = list(filter(lambda x: x.get('product')==nonfree.product \
						and x.get('attribute_ids') == attribute_ids,cart_items))
				if len(nonfree_items)>0:
					allow = True
					break
		else:
			allow = True
		if allow:
			if nonfree.discount_type == 'Discount Percentage':
				discount_amt = (flt(subtotal) * flt(nonfree.discount_percentage) / 100)
			else:
				discount_amt = flt(nonfree.discount_amount)			
			out['discount_amount'] = math.ceil(discount_amt * 100) / 100
			out['subtotal'] = flt(subtotal) - flt(discount_amt)
	return out


def validate_requirements_items_list(item,cart_items,customer_id,msg,payment_method):
	items = json.loads(item.items_list)
	items_list = [i.get('item') for i in items]
	if item.discount_requirement in ['Has any one product in cart', 'Has all these products in cart']:
		citems = [x.get('product') for x in cart_items] if cart_items else []
		check_product = list(frappe.utils.has_common(citems, items_list))
		if item.discount_requirement == 'Has any one product in cart':			
			if not check_product:
				return {
						'status': 'failed', 
						'message': msg
					}
		if item.discount_requirement == 'Has all these products in cart':
			if len(check_product) != len(items_list):
				return {
						'status': 'failed', 
						'message': msg
					}
	elif item.discount_requirement == 'Limit to role' and customer_id:
		
		userid = frappe.db.get_value("Customers", customer_id, "user_id")
		if not userid:
			return {
					'status': 'failed', 
					'message': frappe._('Invalid User')
				}
		else:
			for itlist in items_list:
				if itlist not in frappe.get_roles(userid):
					return {
								'status': 'failed', 
								'message': frappe._('Not a Valid Role')
							}
	elif item.discount_requirement == 'Specific Shipping Method':
		if not shipping_method:
			return {
					'status': 'failed', 
					'message': frappe._('Please select shipping method and try this coupon again')
				}
		if not shipping_method in items_list:
			if shipping_method:
				shipping_method = frappe.db.get_value("Shipping Method", shipping_method, 'shipping_method_name')
			return {
					'status': 'failed', 
					'message': frappe._('This coupon is not applicable for "{0}"').format(
																						shipping_method
																					)}
	elif item.discount_requirement == 'Specific Payment Method':
		if not payment_method:
			return {
					'status': 'failed',
					'message': frappe._('Please select payment method and try this coupon again')
				}
		if not payment_method in items_list:
			message = frappe._('This coupon is not applicable for payment by "{0}"').format(
																						payment_method
																					)
			return {
					'status': 'failed', 
					'message': message
				}

	return{'status':'success'}
	
 	
def validate_item_requirements(requirements,subtotal,total_weight,customer_id,cart_items,msg,
									payment_method,currency):
	for item in requirements:
		
		if item.discount_requirement == 'Spend x amount' and float(subtotal) < float(item.amount_to_be_spent):
			return {
					'status': 'failed', 
					'message': frappe._('The minimum order value must be {0}{1} to apply this coupon').\
							format(currency, "%0.2f" %item.amount_to_be_spent)
				}
		elif item.discount_requirement == 'Specific price range':
			if float(item.min_amount):
				if float(subtotal) < float(item.min_amount):
					return {
					'status': 'failed', 
					'message':frappe._('The minimum order value must be {0}{1} to apply this coupon').\
								format(currency, "%0.2f" %item.min_amount)}
			if float(item.max_amount):
				if float(subtotal) > float(item.max_amount):
					return {
					'status': 'failed',
					'message': frappe._('The maximum order value must be {0}{1} to apply this coupon').\
								format(currency, "%0.2f" %item.max_amount)}
		elif item.discount_requirement == 'Spend x weight':
			if float(item.weight_for_discount):
				if float(total_weight) > float(item.weight_for_discount):
					return {
							'status': 'failed', 
							'message':frappe._('The order weight must be {0}{1} to apply this coupon').\
										format(currency, item.weight_for_discount)}
		elif item.discount_requirement == 'Limit to customer':
			items = json.loads(item.items_list)
			items_list = [i.get('item') for i in items]
			if customer_id not in items_list:
				return {
						'status': 'failed', 
						'message': frappe._('Not valid customer.')
					}
		elif item.items_list:
			return validate_requirements_items_list(
													item,
													cart_items,
													customer_id,
													msg,
													payment_method
												)


def calculate_count_by_discount_requirement(customer_id,dis,subtotal,total_weight,shipping_method,
											payment_method):
	for r in dis.discount_requirements:
		html += "discount_requirements: "+str(r.discount_requirement)+"\n"
		if r.discount_requirement == 'Spend x amount':
			html += "float(r.amount_to_be_spent): "+str(float(r.amount_to_be_spent))+"\n"
			html += "float(subtotal or 0): "+str(float(subtotal or 0))+"\n"
			if float(r.amount_to_be_spent) <= float(subtotal or 0):
				count = count + 1
			else:
				break
		if r.discount_requirement == 'Spend x weight':
			if float(r.weight_for_discount) <= float(total_weight or 0):
				count = count + 1
			else:
				break
		items = json.loads(r.items_list) if r.items_list else []
		items_list = [i.get('item') for i in items]
		if r.discount_requirement == 'Specific Shipping Method':
			if shipping_method in items_list:
				count = count + 1
			else:
				break
		elif r.discount_requirement == 'Specific Payment Method':
			if payment_method in items_list:
				count = count + 1
			else:
				break
		elif r.discount_requirement == 'Limit to role':
			userid = frappe.db.get_value("Customers", customer_id, "user_id")
			for itlist in items_list:
				if itlist in frappe.get_roles(userid):
					count = count + 1
				else:
					break
	return count


def check_product_discount_by_id(_discount_id,customer_id,subtotal,total_weight,shipping_method, 
									payment_method,item,order,html,order_info = None):
	def _insert_order_item(res, dis, order_info):
		for it in res:
			if it.get('type') == 'Product':
				frappe.get_doc({
								"doctype": "Order Item", 
								"parenttype": "Order", 
								"parentfield": "order_item",
								"parent": order_info.name, 
								"tax": 0,
								"attribute_ids": it.get('attribute_ids'),
								"attribute_description": it.get('attribute_description'),
								"item": it.get('product'), 
								"quantity": it.get('quantity'),
								"is_free_item": 1, 
								"price": it.get('price'), 
								"item_name": it.get('product_name'),
								"amount": flt(it.get('price')) * flt(it.get('quantity')),
								"order_item_type": "Product", 
								"discount": dis.name,
							}).insert(ignore_permissions=True)

	dis = frappe.get_doc('Discounts', _discount_id)
	item_info = {}
	count = 0
	update_discount_history = False
	if dis.discount_requirements and len(dis.discount_requirements) > 0:
		count = calculate_count_by_discount_requirement(
														customer_id,
														dis,
														subtotal,
														total_weight,
														shipping_method,
														payment_method
													)
	if order or (dis.discount_requirements and len(dis.discount_requirements) > 0):
		if dis.limitations != 'Unlimited':
			discount_history = get_usage_history(dis)
			usage_count = 0
			if dis.limitations == 'N times only':
				usage_count = len(discount_history) or 0
			else:
				_check_list = list(filter(lambda x: x.customer == customer_id, discount_history))
				usage_count = len(_check_list) or 0
			if usage_count < dis.limitation_count:
				update_discount_history = True
		else:
			update_discount_history = True
		if dis.min_qty > 0 and cint(item.get('quantity')) < cint(dis.min_qty):
			update_discount_history = False
		if dis.max_qty > 0 and cint(item.get('quantity')) > cint(dis.max_qty):
			update_discount_history = False
	html +="len(dis.discount_requirements): "+str(len(dis.discount_requirements))+", \n"+"count: "+ \
		str(count)+", \nupdate_discount_history: "+str(update_discount_history)+"\n"
	if update_discount_history and count == len(dis.discount_requirements):
		item_info = calculate_discount(dis, (item.get('product') or item.get('item')), \
								item.get('quantity'), item.get('price'), \
								item.get('attribute_ids'), item.get('attribute_description'))
		html +="str(item_info)"+ str(item_info)+"\n"
		if item_info:
			if order:
				check = next((x for x in order_info.order_item if (x.is_free_item == 1 and x.discount == dis.name)), None)
				if not check:
					_insert_order_item(item_info, dis, order_info)
					update_discount_history = True
		html +="str(order)"+ str(order)+"\n"
		if order:
			check_history = next((x for x in dis.discount_history if x.order_id == order_info.name), None)
			if not check_history:
				dis.append('discount_history', {
												'order_id': order_info.name,
												'customer': order_info.customer
											})
				dis.save(ignore_permissions=True)
	else:
		if order:
			frappe.db.set_value('Order Item', item.get('name'), 'discount', '')


def calculate_discount_out(discount,rate,out,product,attribute_id,attribute_description,qty):
	if discount.price_or_product_discount == 'Price':
		if discount.percent_or_amount == 'Discount Percentage':
			discount_amt = (flt(rate) * flt(discount.discount_percentage) / 100)
		else:
			discount_amt = discount.discount_amount
		out['discount'] = flt(discount_amt)* cint(qty)
		out['rate'] = flt(rate) - flt(discount_amt)
		out['total'] = flt(out['rate']) * cint(qty)
	elif discount.discount_type == 'Assigned to Products' and discount.price_or_product_discount == 'Product':	
		if discount.same_product:
			out['free_item'] = product
			out['attribute_ids'] = attribute_id
			out['attribute_description'] = attribute_description
		else:
			out['free_item'] = 1			
		if discount.same_product:
			val = float(qty) / float(discount.min_qty)
			if val > 0:
				out['free_qty'] = int(discount.free_qty) * int(val)
			out['item_name'], out['price'], out['route'] =	frappe.db.get_value('Product', 
															out['free_item'],['item', 'price', 'route'])
			image = frappe.db.sql(f'''  SELECT IFNULL(mini_cart, '') AS image 
										FROM `tabProduct Image` 
										WHERE parent = %(parent)s 
										ORDER BY is_primary DESC 
										LIMIT 1 ''', {'parent': out['free_item']}, as_dict=1)
			if image:
				out['image'] = image[0].image
	elif discount.discount_type == 'Assigned to Sub Total' \
				and discount.price_or_product_discount == 'Product':			
		if discount.same_product:
			pass
		else:
			out['free_item'] = 1			
		if discount.same_product:
			val = float(qty) / float(discount.min_qty)
			if val > 0:
				out['free_qty'] = int(discount.free_qty) * int(val)
			out['item_name'], out['price'], out['route'] = frappe.db.get_value(
																				'Product', 
																				out['free_item'], 
																				[
																					'item', 
																					'price', 
																					'route'
																				])
			image = frappe.db.sql(f'''	SELECT IFNULL(mini_cart, '') AS image 
										FROM `tabProduct Image` 
										WHERE parent = %(parent)s 
										ORDER BY is_primary DESC 
										LIMIT 1 ''', {'parent': out['free_item']}, as_dict=1)
			if image:
				out['image'] = image[0].image
	elif discount.price_or_product_discount == 'Cashback':
		out['cashback'] = 1
		if discount.cashback_type == 'Percentage':
			cashback = (flt(rate) * flt(discount.cashback_percentage) / 100)
		else:
			cashback = discount.cashback_amount
		out['cashback_amount'] = cashback


def calculate_apply_discount(apply_discount,qty,discount,products_list):
	for disc in apply_discount:
		val = float(qty) / float(discount.min_qty)
		if val > 0:
			free_qty = int(disc.qty) * int(val)
		item_name, price, route= frappe.db.get_value('Product', disc.product, ['item', 'price', 'route'])
		image = frappe.db.sql(f'''	SELECT IFNULL(mini_cart, '') AS image 
									FROM `tabProduct Image` 
									WHERE parent=%(parent)s 
									ORDER BY is_primary DESC 
									LIMIT 1 ''', {'parent': disc.product}, as_dict=1)
		if image:
			image = image[0].image
		html = ''
		options = frappe.db.sql(f'''SELECT O.price_adjustment, O.option_value, P.attribute 
									FROM `tabProduct Attribute Option` AS O 
									LEFT JOIN `tabProduct Attribute Mapping` AS P 
									ON P.name = O.attribute_id 
									WHERE O.name=%(name)s AND O.parent=%(parent)s
								''', {'name': disc.product_attribute, 'parent': disc.product}, as_dict=1)
		if options:
			html += '<div class="cart-attributes"><span class="attr-title">'+ \
				options[0].attribute+' </span> : <span>'+options[0].option_value+'</span></div>'
			price = float(price) + float(options[0].price_adjustment)
		item_info = {
						'product': disc.product, 
						'product_name': item_name, 
						'price': price, 
						'quantity': free_qty,
						'route': route,
						'image': image,
						'attribute_ids': None,
						'attribute_description': None,
						'type': 'Product' 
					}
		attr_items = json.loads(disc.product_attribute_json)
		if len(attr_items)>0:
			for attr in attr_items:
				attr_name = attr['name'].split('-')
				attribute_ids = attr_name[1]
				html = ''
				options = frappe.db.sql(f'''SELECT O.price_adjustment, O.option_value, P.attribute
											FROM `tabProduct Attribute Option` O
											LEFT JOIN 
												`tabProduct Attribute Mapping` P ON P.name = O.attribute_id
											WHERE O.name = %(name)s AND O.parent = %(parent)s
										''', {'name': attribute_ids, 'parent': disc.product}, as_dict=1)
				if options:
					html += '<div class="cart-attributes"><span class="attr-title">'+ \
						options[0].attribute+' </span> : <span>'+options[0].option_value+'</span></div>'
					price = float(price) + float(options[0].price_adjustment)
				item_info['price'] = price
				item_info['attribute_ids'] = attribute_ids
				item_info['attribute_description'] = html
				products_list.append(item_info)
		else:
			products_list.append(item_info)
	return products_list


def calculate_discount_out_(discount,out,qty,products_list):
	if discount.same_product:
		item_info = {'product': out.get('free_item'), 
					'product_name': out.get('item_name'), 
					'price': out.get('price'), 
					'quantity': out.get('free_qty'),
					'route': out.get('route'),
					'image': out.get('image'),
					'attribute_ids': out.get('attribute_ids'),
					'attribute_description': out.get('attribute_description'),
					'type': 'Product'}
		products_list.append(item_info)
	else:
		apply_discount = frappe.db.sql(f''' SELECT product, product_attribute, qty, 
												product_attribute_json, 
												discount_type, discount_amount, discount_percentage 
											FROM 
												`tabDiscount Applied Product` 
											WHERE 
												parent = %(parent)s 
													AND (discount_type!="Discount Percentage" 
													AND discount_type!="Discount Amount")
										''', {'parent': discount.name}, as_dict=1)
		if apply_discount and len(apply_discount) > 0:
			data = calculate_apply_discount(apply_discount,qty,discount,products_list)
			if data:
				products_list = data
	return products_list


def get_coupon_code_price_or_product_discount_(nonfree_product_item,added_product,cartitems,
												cartattrubutes,cart_items):
	for disc in nonfree_product_item:
		allows = False
		for n in added_product:
			if n.replace("\n", "") in cartitems:
				allows = True
		price = frappe.db.get_value('Product', disc.product, 'price')
		all_attr = get_coupan_code_query(disc)

		attr_items = json.loads(disc.product_attribute_json)
		attr_allows = False
		ht += str(attr_items)+": attr_items\n"
		attr = None

		if len(attr_items)>0:
			for atr in attr_items:
				attr_name = atr['name'].split('-')
				attribute_ids = attr_name[1]
				if attribute_ids in cartattrubutes:
					attr_allows = True
					attr = attribute_ids
					options = frappe.db.sql('''SELECT O.price_adjustment, O.option_value, P.attribute
												FROM `tabProduct Attribute Option` O
												LEFT JOIN `tabProduct Attribute Mapping` P 
													ON P.name = O.attribute_id
												WHERE O.name = %(name)s 
													AND O.parent = %(parent)s
											''', {'name': attribute_ids, 'parent': disc.product}, 
												as_dict=1)
					if options:
						price = float(price) + float(options[0].price_adjustment)
		else:
			if all_attr:
				min_attr = min(all_attr, key=lambda x: x.rate)
				
				if min_attr and min_attr.optionid in cartattrubutes:
					attr = min_attr.optionid
					price = float(min_attr.rate)
					attr_allows = True
		discount_amt = 0
		if disc.product and disc.product in cartitems and (allows or attr_allows):
			if disc.discount_type == 'Discount Percentage':
				discount_amt = (flt(price) * flt(disc.discount_percentage) / 100)
			rate = flt(price) - flt(discount_amt)
			total = flt(rate) * cint(disc.qty)
			if attr and disc.product and disc.qty:
				frappe.db.set_value("Cart Items", {
													"parent": cart_items[0].parent, 
													"product": disc.product, 
													"attribute_ids": attr
												}, "price", rate)
				frappe.db.set_value("Cart Items", {
													"parent": cart_items[0].parent, 
													"product": disc.product, 
													"attribute_ids": attr
												}, "total", total)
		else:
			return {
					'status': 'failed', 
					'message': frappe._('Coupon code entered is not valid.')
				}


def get_coupan_code_query(disc):
    return frappe.db.sql('''SELECT (IFNULL(O.price_adjustment, 0) + IFNULL(PDT.price, 0)) AS rate,
								O.option_value, P.attribute, O.name AS optionid, 
								P.name AS attributeid, P.parent
							FROM `tabProduct Attribute Option` O
							LEFT JOIN `tabProduct Attribute Mapping` P 
								ON P.name = O.attribute_id
							LEFT JOIN `tabProduct` PDT 
								ON PDT.name = P.parent
							WHERE O.parent = %(parent)s
						''', {'parent': disc.product}, as_dict = 1)