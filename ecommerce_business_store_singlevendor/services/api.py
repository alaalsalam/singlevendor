#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import frappe, json
from frappe import _
from frappe.utils import getdate, add_to_date, time_diff_in_hours
from datetime import datetime, timedelta
from six import string_types
from ecommerce_business_store_singlevendor.utils.setup import get_settings_from_domain, get_settings_value_from_domain
from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api import perdelta, get_today_date, node_cancel_order
from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.discounts.discounts import get_product_discount

@frappe.whitelist(allow_guest=True)
def businesslist(latitude, longitude, category=None, limit_start=0, limit_page_length=10, filters=None, sort=None):
	try:
		catalog_settings = get_settings_from_domain('Catalog Settings')
		category_condition = ''
		if category:
			category_lists = ''			
			if catalog_settings.include_products_from_subcategories:
				lft, rgt = frappe.db.get_value('Product Category', category, ['lft', 'rgt'])
				category_list = frappe.db.sql_list('''select name from `tabProduct Category` where lft >= {lft} and rgt <= {rgt} and is_active = 1 and disable_in_website = 0'''.format(lft=lft, rgt=rgt))
				category_lists = ','.join([('"' + x + '"') for x in category_list])
			else:
				category_lists = '"{0}"'.format(category)
			category_condition = ' and pcm.category in ({0})'.format(category_lists)
		business_cond = ''
		if filters:
			if isinstance(filters, string_types):
				filters = json.loads(filters)
			if filters.get('service_for'):
				business_cond += ' and sm.service_for in ({0})'.format(','.join([('"' + x + '"') for x in filters.get('service_for')]))
			if filters.get('price_range'):
				ranges = " or ".join(['(s.price >= {min} and s.price <= {max})'.format(min=i['min'],max=i['max']) for i in filters.get('price_range')])
				business_cond += ' and {0}'.format(ranges)
		business_list = frappe.db.sql_list('''select distinct s.business from `tabService` s left join `tabProduct Category Mapping` pcm on pcm.parent = s.name left join `tabService For Mapping` sm on sm.parent = s.name where s.is_active = 1 {0} {1}'''.format(category_condition, business_cond))
		if business_list:
			rating_filter = ''
			condition = ' and b.name in ({0})'.format(','.join([('"' + x + '"') for x in business_list]))
			if filters and filters.get('business_location'):
				condition += ' and b.business_location in ({0})'.format(','.join([('"' + x + '"') for x in filters.get('business_location')]))
			if filters and filters.get('business_area'):
				condition += ' and b.business_area in ({0})'.format(','.join([('"' + x + '"') for x in filters.get('business_area')]))
			if filters and filters.get('ratings'):
				rating_filter += ' and business_rating >= {0}'.format(filters.get('ratings'))
			distance = get_settings_value_from_domain('Business Setting','nearby_distance')
			sort_condition = get_sort_condition(sort)
			query='''SELECT distinct b.name,b.restaurant_name,b.business_phone,b.contact_number,b.city,b.country,b.contact_email,b.business_address,b.state,
				b.zip_code,b.restaurant_logo,b.banner_image,b.price_type,b.about_restaurant,b.latitude,b.longitude, SQRT(POW(69.1 * (latitude - {lat}), 2) + 
				POW(69.1 * ({lng} - longitude) * COS(latitude / 57.3), 2)) AS distance, avg(br.overall_rating) as business_rating,
				(select min(price) from `tabService` where is_active = 1 and business = b.name limit 1) as min_price, 
				(select max(price) from `tabService` where is_active = 1 and business = b.name limit 1) as max_price
				FROM `tabBusiness` b left join `tabBusiness Reviews` br on br.review_for = "Business" and br.business = b.name and br.is_approved = 1
				where b.show_in_website = 1 {condition} group by b.name HAVING distance < cast({distance} as decimal) {rating} {sort}
				limit {start},{limit}'''.format(limit=limit_page_length,start=limit_start,distance=distance,lat=latitude,lng=longitude,condition=condition, rating=rating_filter, sort=sort_condition)
			businesslist = frappe.db.sql(query,{'lat': latitude,'lng': longitude,'d': distance}, as_dict=1)
			for business in businesslist:
				business = get_business_other_info(business)
			return businesslist
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store_singlevendor.services.api.businesslist")

def get_sort_condition(sort=None):
	if not sort:
		sort = 'Near Me'
	if sort == 'Near Me':
		return ' ORDER BY distance'
	elif sort == 'Popular':
		return ' ORDER BY business_rating desc'
	elif sort == 'New':
		return ' ORDER BY b.creation desc'
	elif sort == 'Price Low To High':
		return ' ORDER BY min_price'
	elif sort == 'Price High To Low':
		return ' ORDER BY max_price desc'

@frappe.whitelist()
def get_business_other_info(business):
	business.distance = business.distance * 1.609
	business.gallery = frappe.db.sql(''' select business_image, is_primary, thumbnail, image_name from `tabBusiness Images` where parent = %(parent)s and parentfield = "business_images" order by is_primary desc''', {'parent': business.name}, as_dict=1)
	reviews = frappe.db.sql('''select customer, email, review_title, review_message, overall_rating from `tabBusiness Reviews` where business = %(business)s  and is_approved=1''', {'business': business.name}, as_dict=1)
	if len(reviews) > 0:
		business.ratings = sum(r.overall_rating for r in reviews)/len(reviews)
	business.reviews = reviews
	return business

@frappe.whitelist(allow_guest=True)
def get_business_information(business):
	try:
		business_list = frappe.db.get_all('Business', filters={'name': business}, fields=['restaurant_name', 'business_phone', 'contact_person', 'contact_number', 'contact_email', 'business_address', 'business_location', 'business_area', 'country', 'state', 'zip_code', 'restaurant_logo', 'about_restaurant', 'banner_image', 'name'])
		if business_list:
			business_info = business_list[0]
			business_info.gallery = frappe.db.sql('''select business_image, is_primary, thumbnail, image_name 
				from `tabBusiness Images` where parent = %(parent)s and parentfield = "business_images" order 
				by is_primary desc''', {'parent': business_list[0].name}, as_dict=1)
			reviews = frappe.db.sql('''select customer, email, review_title, review_message, overall_rating 
				from `tabBusiness Reviews` where review_for = "Business" and business = %(business)s  and is_approved=1 order by creation desc''', {'business': business_list[0].name}, as_dict=1)
			if len(reviews) > 0:
				business_info.ratings = sum(r.overall_rating for r in reviews)/len(reviews)
			business_info.reviews = reviews
			services = frappe.db.sql('''select name, service_title, description, price, old_price, business,
				service_duration_in_mins, (select group_concat(service_for) from `tabService For Mapping` where 
				parent = tabService.name) as service_for, max_allow, tax_template, enable_booking, time_slot_length, 
				restrict_booking, max_bookings from tabService where business = %(business)s and status = "Approved" 
				and is_active = 1''', {'business': business_list[0].name}, as_dict=1)
			for service in services:
				price_details = get_product_discount(service, 1, service.price)
				service_price = service.price
				if price_details:
					if price_details.get('discount_amount'):
						service_price = price_details.get('rate')
					service.discount_rule = price_details.get('discount_rule')
					service.discount_label = price_details.get('discount_label')
				if service.price != service_price:
					service.old_price = service.price
					service.price = service_price
				if float(service.old_price) > 0 and float(service.price) < float(service.old_price):
					service.discount_percentage = int(round((service.old_price - service.price) / service.old_price * 100, 0))
			business_info.services = services
			business_info.working_hrs = frappe.db.sql('''select day, status, from_hrs, to_hrs from `tabOpening Hour` where parent = %(parent)s order by idx''', {'parent': business_list[0].name}, as_dict=1)
			if frappe.db.get_value('DocType', 'Booking Settings'):
				booking_settings = frappe.db.get_all('Booking Settings', filters={'business': business}, fields=['*'])
				if booking_settings:
					business_info.booking_settings = booking_settings[0]
			return business_info
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store_singlevendor.services.api.get_business_information")

@frappe.whitelist(allow_guest=True)
def get_home_page_data(latitude, longitude):
	try:
		sliders = frappe.db.sql('''select title, mobile_app_image, sub_title from `tabSlider` where published = 1 order by display_order''', as_dict=1)
		categories = frappe.db.sql('''select name, category_name, ifnull(mobile_image, category_image) as image from `tabProduct Category` where (parent_product_category is null or parent_product_category = "" or parent_product_category = "All Product Category") and is_active = 1 and disable_in_website = 0 order by display_order''', as_dict=1)
		# nearby_business = get_nearby_business(latitude, longitude)
		service_for = frappe.db.sql('''select name from `tabService For` order by name''', as_dict=1)
		business_location = frappe.db.sql('''select name from `tabBusiness Location`''', as_dict=1)
		for item in business_location:
			item.area = frappe.db.sql('''select name, area_name from `tabBusiness Area` where location = %(location)s''',{'location': item.name}, as_dict=1)
		return {'sliders': sliders, 'categories': categories, 'service_for': service_for, 'location': business_location}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store_singlevendor.services.api.get_home_page_data")

def get_nearby_business(latitude, longitude):
	distance=get_settings_value_from_domain('Business Setting','nearby_distance')
	query='''SELECT distinct b.name,b.restaurant_name,b.business_phone,b.contact_number,b.city,b.country,b.contact_email,b.business_address,b.state,
		b.zip_code,b.restaurant_logo,b.banner_image,b.price_type,b.about_restaurant,b.latitude,b.longitude, SQRT(POW(69.1 * (latitude - {lat}), 2) + 
		POW(69.1 * ({lng} - longitude) * COS(latitude / 57.3), 2)) AS distance
		FROM `tabBusiness` b where show_in_website = 1 HAVING distance < cast({distance} as decimal) ORDER BY distance 
		limit 10'''.format(distance=distance,lat=latitude,lng=longitude)
	businesslist = frappe.db.sql(query,{'lat': latitude,'lng': longitude,'d': distance}, as_dict=1)
	for business in businesslist:
		business = get_business_other_info(business)
	return businesslist

@frappe.whitelist(allow_guest=True)
def get_service_persons(business):
	try:
		service_persons = frappe.db.sql('''select name, full_name, email, mobile, image from `tabService Person` where business = %(business)s and is_active = 1''', {'business': business}, as_dict=1)
		for person in service_persons:
			services = frappe.db.sql('''SELECT name, service_title, service, parent FROM `tabService Person Service Mapping` WHERE parent=%(name)s''',{'name':person.name},as_dict=1)
			if len(services) > 0:
				person.services = services
			availability = frappe.db.sql('''SELECT from_time, to_time, parent, day, name FROM `tabAvailable Time Slot` WHERE parent=%(name)s''',{'name':person.name},as_dict=1)
			if len(availability) > 0:
				person.availability = availability
			reviews = frappe.db.sql('''select customer, email, review_title, review_message, overall_rating from `tabBusiness Reviews` where review_for = "Service Person" and business = %(business)s  and is_approved=1 order by creation desc''', {'business': person.name}, as_dict=1)
			if len(reviews) > 0:
				person.ratings = sum(r.overall_rating for r in reviews)/len(reviews)
			person.reviews = reviews
		return service_persons
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store_singlevendor.services.api.get_service_persons")

@frappe.whitelist(allow_guest=True)
def get_booking_time_slot(business='BS-00001', service=None):
	try:
		booking_settings = frappe.db.get_all('Booking Settings', filters={'business': business}, fields=['*'])
		if booking_settings:
			booking_setting = booking_settings[0]
			check_type = 'Service'
			if booking_settings[0].allow_multiple_items:
				check_type = 'Business'
			else:
				if not service:
					return {'status': 'Failed', 'message': _('Value missing for service')}
				all_time = frappe.db.get_value('Service', service, 'all_time')
				if all_time:
					check_type = 'Business'
			if check_type == 'Business':
				timings = frappe.db.sql('''select day, from_hrs as from_time, to_hrs as to_time from `tabOpening Hour` where parent = %(parent)s and status = "Open"''', {'parent': business}, as_dict=1)
			else:
				timings = frappe.db.sql('''select day, from_time, to_time from `tabAvailable Time Slot` where parent = %(parent)s''',{'parent': service}, as_dict=1)
			time_zone = frappe.db.get_single_value('System Settings','time_zone')
			dtfmt = '%Y-%m-%d %H:%M:%S'
			booking_timings = []
			currentdatezone = get_today_date(time_zone, True)
			today_date = getdate(currentdatezone)
			if booking_setting and booking_setting.no_of_days:
				no_of_days = int(booking_setting.no_of_days)
			else:
				no_of_days = 7
			stop = True
			dates = []
			step = 0
			while stop:
				new_date = add_to_date(today_date, days=step)
				step = step + 1
				day = getdate(new_date).strftime('%A')
				allow = False
				check_time = []
				if timings:
					check_day = list(filter(lambda x: x.day == day, timings))
					if check_day:
						for item in check_day:
							check_time.append({'from_hrs': item.from_time, 'to_hrs': item.to_time})			
				if len(check_time) > 0:
					dates.append({'date': new_date, 'time': check_time})
				if len(dates) > 0 and len(dates) == int(no_of_days):
					stop = False
				if int(step) > 25:
					stop = False

			if dates:
				slot_timing = booking_setting.time_slot_length
				if not booking_setting.allow_multiple_items:
					# slot_timing = frappe.db.get_value('Service', service, 'time_slot_length')
					duration, slot = frappe.db.get_value('Service', service, ['service_duration_in_mins', 'time_slot_length'])
					if booking_setting.service_duration == 1 and duration:
						slot_timing = duration
					elif slot:
						slot_timing = slot
				for d in dates:
					time = []
					blocked_dates = frappe.db.get_all('Online Order Timing Block', filters={'date_to_be_blocked': getdate(d['date']), 'restaurant': business}, fields=['*'])
					closed = 0
					blocked_timings = []
					if blocked_dates:
						for item in blocked_dates:
							if item.full_day:
								closed = 1
							else:
								blocked_timings.append({
									'from_time': datetime.strptime(str(d['date']) + ' ' + str(item.from_time), dtfmt),
									'to_time': datetime.strptime(str(d['date']) + ' ' + str(item.to_time), dtfmt)
								})
					if not closed:
						for t in d['time']:
							from_date_time = datetime.strptime(str(d['date']) + ' ' + str(t['from_hrs']), dtfmt)
							to_date_time = datetime.strptime(str(d['date']) + ' ' + str(t['to_hrs']), dtfmt)
							# if not block_time:
							if getdate(d['date']) == getdate(today_date):
								if booking_setting.min_time > 0:
									add_min_time =False
									if currentdatezone > from_date_time:
										time_diff = time_diff_in_hours(currentdatezone, from_date_time)
										hour = float(time_diff) + int(booking_setting.min_time)
										from_date_time = from_date_time + timedelta(hours=int(round(hour)))
									else:
										time_diff = time_diff_in_hours(from_date_time, currentdatezone)
										if time_diff < booking_setting.min_time:
											from_date_time = from_date_time + timedelta(hours=int(booking_setting.min_time))
							opsgt=0
							for result in perdelta(from_date_time,to_date_time,timedelta(minutes=int(slot_timing))):	
								duration = result - currentdatezone
								minutes = duration.total_seconds() / 60
								opsgt = opsgt + 1
								if minutes > float(slot_timing):
									allow = False
									if booking_setting.allow_multiple_items:
										allow = True
									else:
										restrict, no_of_booking = frappe.db.get_value('Service', service, ['restrict_booking', 'max_bookings'])
										if restrict:
											check_bookings = frappe.db.get_all('Reservation Booking',filters={'docstatus': 1, 'reservation_date': str(d['date']), 'from_time': result.strftime("%H:%M:%S"), 'booking_type': 'Service', 'booking_service_id': service}, limit_page_length=1000)
											print("-----------ser")
											print(len(check_bookings))
											print(int(no_of_booking))
											print(service)
											if len(check_bookings) < int(no_of_booking):
												allow = True
											# else:
											# 	allow = False
											# 	break
										else:
											allow = True
									
									if blocked_timings:
										for blk in blocked_timings:
											if result >= blk['from_time'] and result <= blk['to_time']:
												allow = False
												break
											
									if allow:
										time.append(str(result.strftime("%I:%M %p")))
							booking_timings.append({'date': str(d['date']), 'time': time})
			return booking_timings
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store_singlevendor.services.api.get_booking_time_slot")

@frappe.whitelist()
def insert_bookings(booking_response, order_info):
	booking_settings = None
	if order_info.get('business'):
		booking_settings = get_settings_from_domain('Booking Settings', business=order_info.get('business'))
	slot_timing = booking_settings.time_slot_length
	if not booking_settings.allow_multiple_items:
		duration, slot = frappe.db.get_value('Service', item.item, ['service_duration_in_mins', 'time_slot_length'])
		if booking_settings.service_duration == 1 and duration:
			slot_timing = duration
		elif slot:
			slot_timing = slot
	bookings=frappe.new_doc('Reservation Booking')
	bookings.reservation_date=getdate(booking_response.get('booking_date'))
	if booking_response.get('slot_time'):
		start_time = frappe.utils.to_timedelta(booking_response.get('slot_time'))
		start_date = datetime.strptime(str(bookings.reservation_date)+' '+str(start_time),'%Y-%m-%d %H:%M:%S')
		bookings.from_time = start_date
		for item in order_info.get('order_item'):
			bookings.append('booking_item',{
				'booking_type': item.get('order_item_type'),
				'reference_doctype': item.get('order_item_type'),
				'booking_service_id': item.get('item'),
				'service_name': item.get('service_name'),
				'price': item.get('price')
				})
		bookings.to_time = start_date + timedelta(minutes=int(slot_timing))
		bookings.customer_id = order_info.get('customer')
		bookings.customer_name,bookings.customer_mobile = frappe.db.get_value('Customers',order_info.get('customer'),['full_name','phone'])
		bookings.no_of_persons = booking_response.get('no_of_persons') if booking_response.get('no_of_persons') else 1
		bookings.booking_status = booking_settings.default_booking_status if booking_settings else 'Awaiting Approval'
		if booking_response.get('service_person'):
			bookings.service_person = booking_response.get('service_person')
		if order_info.get('docstatus') == 1: bookings.docstatus = 1
		# Change done by shankar on 11-03-2020 to Submit booking reservation if Default booking status is confirmed
		if booking_settings.default_booking_status == 'Confirmed':
			bookings.docstatus = 1
		# end of changes
		bookings.business = order_info.get('business')
		bookings.save(ignore_permissions=True)
		if order_info.get('name'):
			frappe.db.set_value('Order',order_info.name,'booking_id',bookings.name)
		if booking_settings and booking_settings.cancel_booking:
			current_time = datetime.now()
			cancel_at = current_time + timedelta(seconds=int(booking_settings.cancel_after))
			node_cancel_order(bookings.name, cancel_at, 'ecommerce_business_store_singlevendor.services.api.cancel_booking', booking_settings.cancel_after, business=bookings.business)
		booking_info = bookings.as_dict()
		return booking_info

@frappe.whitelist(allow_guest=True)
def cancel_booking(order):
	try:
		booking_info = frappe.db.get_all('Reservation Booking', filters={'name': order}, fields=['booking_status'])
		if booking_info and booking_info[0].booking_status == 'Awaiting Approval':
			doc = frappe.get_doc('Reservation Booking', order)
			if doc.docstatus == 0:
				doc.docstatus = 1
			doc.booking_status = 'Cancelled'
			doc.save(ignore_permissions=True)

			order_info = frappe.db.get_all('Order', filters={'booking_id': order})
			if order_info:
				order_doc = frappe.get_doc('Order', order_info[0].name)
				if order_doc.docstatus == 0:
					order_doc.docstatus = 1
				order_doc.status = 'Cancelled'
				order_doc.save(ignore_permissions=True)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store_singlevendor.services.api.cancel_booking")

@frappe.whitelist(allow_guest=True)
def search_business(searchTxt, latitude, longitude):
	try:
		distance = get_settings_value_from_domain('Business Setting','nearby_distance')
		service_condition = ''
		services = frappe.db.sql_list('''select distinct business from `tabService` where service_title like %(txt)s''',{'txt': '%' + searchTxt + '%'})
		if services:
			service_condition = ' or b.name in ({0})'.format(','.join(['"' + x + '"' for x in services]))
		condition = ' and (b.restaurant_name like %(txt)s {0})'.format(service_condition)
		query='''SELECT distinct b.name,b.restaurant_name,b.business_phone,b.contact_number,b.city,b.country,b.contact_email,b.business_address,b.state,
				b.zip_code,b.restaurant_logo,b.banner_image,b.price_type,b.about_restaurant,b.latitude,b.longitude, SQRT(POW(69.1 * (latitude - {lat}), 2) + 
				POW(69.1 * ({lng} - longitude) * COS(latitude / 57.3), 2)) AS distance, avg(br.overall_rating) as business_rating,
				(select min(price) from `tabService` where is_active = 1 and business = b.name limit 1) as min_price, 
				(select max(price) from `tabService` where is_active = 1 and business = b.name limit 1) as max_price
				FROM `tabBusiness` b left join `tabBusiness Reviews` br on br.review_for = "Business" and br.business = b.name and br.is_approved = 1
				where b.show_in_website = 1 {condition} group by b.name HAVING distance < cast({distance} as decimal) order by distance
				limit 20'''.format(distance=distance, lat=latitude, lng=longitude, condition=condition)
		businesslist = frappe.db.sql(query,{'lat': latitude,'lng': longitude,'d': distance, 'txt': '%' + searchTxt + '%'}, as_dict=1)
		for business in businesslist:
			business = get_business_other_info(business)
		return businesslist
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store_singlevendor.services.api.search_business")

@frappe.whitelist()
def cancel_order_booking(order_id):
	try:
		booking_id = frappe.db.get_value('Order', order_id, 'booking_id')
		if booking_id:
			check_reservation = frappe.db.get_all('Reservation', filters={'booking_reference': booking_id}, fields=['name', 'reservation_status'])
			if check_reservation and check_reservation[0].reservation_status != 'Completed':
				doc = frappe.get_doc('Reservation', check_reservation[0].name)
				doc.reservation_status = 'Cancelled'
				if doc.docstatus == 0: doc.docstatus = 1
				doc.save(ignore_permissions=True)

				order_info = frappe.get_doc('Order', order_id)
				order_info.status = 'Cancelled'
				order_info.save(ignore_permissions=True)
				return {'status': 'Success'}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "ecommerce_business_store_singlevendor.services.api.cancel_order_booking")
