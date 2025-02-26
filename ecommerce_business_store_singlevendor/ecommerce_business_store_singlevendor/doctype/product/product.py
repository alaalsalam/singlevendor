# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, os, re, json
from frappe.website.website_generator import WebsiteGenerator
from frappe.utils import touch_file, encode
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt, getdate, nowdate, get_url, add_days
from datetime import datetime
from pytz import timezone
from frappe.utils import get_files_path
import pytz
from urllib.parse import unquote
from six import string_types
from ecommerce_business_store_singlevendor.utils.setup import get_settings, get_settings_value
from frappe.desk.reportview import get_match_cond, get_filters_cond

class Product(WebsiteGenerator):
	website = frappe._dict(
							condition_field = "show_in_website",
							no_cache = 1
						)

	def on_trash(self):
		delete_whoose_data(self)


	def autoname(self): 
		naming_series = "ITEM-"
		from frappe.model.naming import make_autoname
		self.name = make_autoname(naming_series + '.#####', doc = self)


	def validate(self):
		self.make_route()
		self.insert_search_words()
		self.validate_order_qty()
		self.item = self.item.lstrip()
		if not self.barcode:
			self.check_barcode()
		if self.old_price and self.old_price > 0 and self.price:
			if self.old_price < self.price:
				frappe.throw(_('Old Price must be greater than the Product Price'))
		if self.status != 'Approved':
			self.status = 'Approved'
		check_attr_combination_price(self)
		self.validate_attribute_options()
		if not self.meta_title:
			self.meta_title = self.item
		if not self.meta_keywords:
			self.meta_keywords = self.item.replace(" ", ", ")
		if not self.meta_description:
			self.meta_description = "About: {0}".format(self.item)
		if self.get("sku"):
			check_other = frappe.db.get_all("Product",
											filters = {
														"sku":self.get("sku"),
														"name":("!=",self.get("name")),
														"status":"Approved"
													})
			if check_other:
				frappe.msgprint("SKU already exist in the system.")
		if self.brand:
			check_brands = frappe.db.get_all("Product Brand Mapping",filters = {"parent":self.name})
			if check_brands:
				for x in self.product_brands:
					x.brand = self.brand
					x.brand_name = self.brand_name
					x.unique_name = self.brand_unique_name
			else:
				self.append("product_brands",{"brand":self.brand,"brand_name":self.brand_name,
								  						"unique_name":self.brand_unique_name})
		if not self.sku and self.has_variants == 0:
			self.sku = self.name.split('ITEM-')[1] + "000"
		self.set_default_image()

	def set_default_image(self):
		if self.product_images:
			cover_image=next((x for x in self.product_images if x.is_primary==1),None)
			if not cover_image:
				self.product_images[0].is_primary=1
			if self.image:
				check_image = next((x for x in self.product_images if x.list_image == self.image), None)
				if not check_image:
					self.image = None
			if not self.image:
				if cover_image:
					self.image=cover_image.list_image
					self.list_images = self.product_images[0].image_name
				else:
					self.image=self.product_images[0].list_image
			
			else:
				if self.image.startswith("/files"):
					file_name = self.image.split("/files/")[-1]
					if not os.path.exists(get_files_path(frappe.as_unicode(file_name.lstrip("/")))):
						self.image=""


	def insert_search_words(self):
		try:
			words = ''
			data = ''
			catalog_settings = get_settings('Catalog Settings')
			if catalog_settings.search_fields:
				count = 1
				for s in catalog_settings.search_fields:
					lenght = len(catalog_settings.search_fields)
					if (len(catalog_settings.search_fields) == 1):
						data += s.fieldname
					else:
						if(count != lenght):
							data += s.fieldname+','
						else:
							data += s.fieldname
					count=count+1
				products = frappe.db.sql('''SELECT {0} 
											FROM `tabProduct` 
											WHERE name = "{1}"
										'''.format(data, self.name), as_dict=1)
				if products:
					for item in products:
						for key, value in item.items():
							if value:
								words +=value
			else:
				if self.item:
					words += str(self.item)
			if catalog_settings.disable_search_keyword == 0:
				if self.search_keyword:
					for item in self.search_keyword:
						words += item.search_keywords
			p = re.compile(r'<.*?>')
			words = p.sub('', words)
			search_words = words.translate ({ord(c): " " for c in "!@#$%^&*()[]{};:,./<>?\|`~-=_+"})
			if search_words:
				self.search_words = search_words
		except Exception:
			frappe.log_error(frappe.get_traceback(), 
					"Error in product.insert_search_words")

	def check_barcode(self):
		try:
			catalog_settings = get_settings('Catalog Settings')
			if catalog_settings:
				if catalog_settings.generate_barcode_for_product:
					import barcode 
					from barcode.writer import ImageWriter
					EAN = barcode.get_barcode_class('code128')
					ean = EAN(self.name, writer=ImageWriter())
					fullname = ean.save(self.name)
					filename = randomStringDigits(18)
					path = 'public/files/{filename}.png'.format(filename=filename)
					touch_file(os.path.join(frappe.get_site_path(),path))
					f = open(os.path.join(frappe.get_site_path(),path), 'wb')
					ean.write(f)
					self.barcode = "/files/" + filename + ".png"
		except Exception:
			frappe.log_error(frappe.get_traceback(), 
					"Error in product.check_barcode")

	def validate_stock(self):
		if self.stock:
			if self.stock < 0:
				frappe.throw(_('Stock cannot be negative value'))
	

	def validate_order_qty(self):
		if self.minimum_order_qty and self.maximum_order_qty:
			if not int(self.minimum_order_qty)>0:
				frappe.throw(_("Minimum order quantity should be greater than zero"))
			if not int(self.maximum_order_qty) >= int(self.minimum_order_qty):
				frappe.throw(_("Maximum order quantity should be greater than minimum order quantity"))


	def make_route(self):
		if not self.route:
			self.route = self.scrub(self.item)
			check_category_exist = frappe.get_list('Product Category', fields=["route"], 
										  filters={"route": self.route},ignore_permissions =True)
			check_route = self.scrub(self.item) + "-" + str(len(check_category_exist))
			routes='"{route}","{check_route}"'.format(route=self.route,check_route=check_route)
			check_exist = frappe.db.sql('''SELECT name 
											FROM `tabProduct` 
											WHERE route IN ({0}) AND name != "{1}"
										'''.format(routes, self.name), as_dict=1)

			if check_exist and len(check_exist) > 0:
				st = str(len(check_exist))
				self.route = self.scrub(self.item) + "-" + st
			if check_category_exist and len(check_category_exist) >0:
				st = str(len(check_exist)+len(check_category_exist))
				self.route = self.scrub(self.item) + "-" + st

		
	def on_update(self):
		update_whoose_search(self)
		self.get_product_availability()
		media_settings = get_settings('Media Settings')
		category = None
		if self.product_categories: 
			category = sorted(
								self.product_categories,
								key = lambda x: x.idx,
								reverse = False
							)[0].category
		list_size = media_settings.list_thumbnail_size
		if category:
			size = frappe.db.get_value('Product Category',category,'product_image_size')
			if size and int(size) > 0:
				list_size = size
		if not self.return_policy:
			self.return_description = ""
		if self.has_variants:
			if self.variant_combination:
				if self.inventory_method != "Track Inventory By Product Attributes":
					self.inventory_method = "Track Inventory By Product Attributes"
		if not self.has_variants:
			if self.inventory_method != "Track Inventory":
				self.inventory_method = "Track Inventory"
		if self.has_variants == 1 and self.variant_combination and self.is_combinations_are_generated == 0:
			self.is_combinations_are_generated = 1
		if self.brand:
			check_brands = frappe.db.get_all("Product Brand Mapping",filters = {"parent":self.name})
			if check_brands:
				for x in self.product_brands:
					x.brand = self.brand
			else:
				self.append("product_brands",{"brand":self.brand})
			frappe.db.commit()
		self.update_product_mapping()
	
	def insert_combination_mapping(self):
		sku_no = 1
		sku_seq = frappe.db.get_all("Product Variant Combination",
									filters = {"parent":self.name},
									fields = ['sku'],
									order_by = "sku desc",
									limit_page_length = 1
								)
		if sku_seq:
			if sku_seq[0].sku:
				l_sku = sku_seq[0].sku
				sku_no = int(l_sku[-3:])+1
		for v in self.variant_combination:
			if not v.sku:
				v_sku = self.name.split("ITEM-")[1]+'%03d' % sku_no
				frappe.db.set_value("Product Variant Combination",v.name,"sku",v_sku)
				v.sku = v_sku
				sku_no = sku_no+1
			if v.product_title:
				v.product_title = v.product_title.rstrip('/')
				v.product_title = v.product_title.rstrip(',')
			if v.disabled==0:
				attribute_ids = v.attribute_id.split('\n')
				for opt in attribute_ids:
					if opt:
						if not frappe.db.get("Combination Option Mapping",
							filters = {"product_id":self.name,"combination_id":v.name,"option_id":opt}):
							frappe.get_doc({
											"doctype": "Combination Option Mapping",
											"product_id": self.name,
											"combination_id": v.name,
											"option_id":opt,
										}).insert()
		frappe.db.commit()  


	def update_product_mapping(self):
		if not self.sku:
			self.sku = self.name.split('ITEM-')[1]+"000"
		if self.variant_combination:
			self.insert_combination_mapping()
		if self.product_brands:
			for x in self.product_brands:
				if not x.unique_name:
					frappe.db.set_value("Product Brand Mapping",x.name,
						 				"unique_name",self.scrub(x.brand))
			frappe.db.commit()  
		if self.attribute_options:
			for x in self.attribute_options:
				if not x.unique_name:
					frappe.db.set_value("Product Attribute Option",x.name,"unique_name",
						 self.scrub(frappe.db.get_value(
														"Product Attribute",
														x.attribute,
									  					"attribute_name"
													).lstrip())+"_" + self.scrub(x.option_value.lstrip()))
				if not x.attribute_id:
					p_attr_id = frappe.db.get_all("Product Attribute Mapping",
								   filters={"parent":self.name,"product_attribute":x.attribute})
					if p_attr_id:
						x.attribute_id = p_attr_id[0].name
			frappe.db.commit()
		if self.product_attributes:
			for x in self.product_attributes:
				if not x.attribute_unique_name:
					frappe.db.set_value("Product Attribute Mapping",x.name,
						 "attribute_unique_name",self.scrub(x.attribute.lstrip()))    
			frappe.db.commit()
		if self.product_categories:
			frappe.enqueue('ecommerce_business_store_singlevendor.\
				  ecommerce_business_store_singlevendor.doctype.product.product.\
				  update_category_data_json',queue = 'short',at_front = True,doc = self)

	def validate_attribute_options(self):
		if self.product_attributes:
			lists = ''
			for item in self.product_attributes:
				if not item.get('__islocal'):
					check_attributes = frappe.db.sql('''SELECT name 
														FROM `tabProduct Attribute Option` 
														WHERE attribute_id = %(name)s
													''', {'name': item.name})

					if not check_attributes and (item.control_type != "Text Box" and \
								  item.control_type != "Multi Line Text"):
						lists += '<li>{0}</li>'.format(item.product_attribute)


	def get_product_availability(self):
		if self.stock and self.stock > 0 and self.inventory_method == 'Track Inventory':
			notification_product = frappe.db.get_all("Product Availability Notification",
											fields=['product','is_email_send','name','attribute_id'], 
											filters={'is_email_send': 0, 'product': self.name})
			if notification_product:
				for stock_avail in notification_product:
					availability = frappe.get_doc("Product Availability Notification",stock_avail.name)
					availability.is_email_send=1
					availability.save(ignore_permissions=True)
		if self.inventory_method == 'Track Inventory By Product Attributes' and \
											len(self.variant_combination)>0:
			notification_product = frappe.db.get_all("Product Availability Notification",
											fields=['product','is_email_send','name','attribute_id'], 
											filters={'is_email_send': 0, 'product': self.name})
			if notification_product:
				for stock_avail in notification_product:
					if stock_avail.attribute_id:
						attribute_id = stock_avail.attribute_id.strip()
						check_data = next((x for x in self.variant_combination \
						 		if x.attribute_id == stock_avail.attribute_id), None)
						if check_data and check_data.stock > 0:
							availability = frappe.get_doc("Product Availability Notification",
									 			stock_avail.name)
							availability.is_email_send=1
							availability.save()


	def get_context(self, context):
		try:
			page_builder = frappe.db.get_all("Web Page Builder",
									filters={"published":1,"document":"Product"},
									fields=['file_path'])
			if page_builder:
				context.template = page_builder[0].file_path
			from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.product \
				import get_product_price
			catalog_settings = context.catalog_settings
			price_details = get_product_price(self)
			orgprice = self.price
			self.check_price_details(context,price_details,orgprice)
			if self.meta_keywords:
				context.meta_keywords=self.meta_keywords if self.meta_keywords else self.item
			else:
				context.meta_keywords = context.catalog_settings.meta_keywords
			self.get_product_mapping(context,catalog_settings,orgprice)
			self.get_custom_fields(context,catalog_settings)
		except Exception:
			frappe.log_error('Error in product.product.get_context', frappe.get_traceback())
	
	

	def get_product_variant_combination(self,context,productattributes,video_list,
									 size_chart,size_charts,size_chart_params,
									 product_attributes,attr_product_title):
		for attribute in productattributes:
			if attribute.size_chart:
				data = self.get_size_chart_content(size_charts,attribute)
				size_charts = data[0]
				size_chart_params = data[1]
			options = frappe.db.get_all("Product Attribute Option",fields=['*'],
					filters={'parent':self.name,'attribute':attribute.product_attribute,
					'attribute_id':attribute.name},order_by='display_order',limit_page_length=50)           
			for op in options:
				txt = '"%' + op.name + '%"'
				varients = frappe.db.sql("""SELECT name, attributes_json, attribute_id, 
												option_color, parent, image_list 
											FROM `tabProduct Variant Combination` 
											WHERE parent = "{0}" 
												AND attribute_id LIKE "{1}" 
											ORDER BY idx ASC
										""".format(self.name, txt), as_dict=1)
				if op.is_pre_selected == 1:
					if op.product_title and op.product_title != '-':
						attr_product_title = op.product_title
				image = self.get_product_attribute_option(context,op,varients,video_list)

			product_attributes.append({
										"attribute":attribute.product_attribute,
										"attribute_name":attribute.attribute,
										"is_required":attribute.is_required,
										"control_type":attribute.control_type,
										"attribute_chart":attribute.size_chart,
										"options":options,
										"size_charts":size_charts,
										'size_chart':size_chart,
										'size_chart_params':size_chart_params
									})
		context.product_title = attr_product_title
		context.attr_image = image
		

	def get_size_chart_content(self,size_charts,attribute):
		size_charts = frappe.db.get_all('Size Chart',
										filters = {'name':attribute.size_chart},
										fields = ['size_chart_image','name'])
		size_chart = frappe.db.sql('''SELECT TRIM(attribute_values) AS attribute_values, 
										chart_title, chart_value, name 
									FROM `tabSize Chart Content` 
									WHERE parent = %(parent)s 
									ORDER BY display_order
								''', {'parent': attribute.size_chart}, as_dict=1)
		unique_sizes = list(set([x.chart_title for x in size_chart]))
		unique_attr = []
		for uni in size_chart:
			if uni.attribute_values not in unique_attr:
				unique_attr.append(uni.attribute_values)
		size_chart_list = []
		for attr in unique_attr:
			sizes_list = list(filter(lambda x: x.attribute_values == attr, size_chart))
			arr = {}
			if sizes_list:
				arr['attribute'] = attr
				for sz in unique_sizes:
					check = next((x for x in sizes_list if x.chart_title == sz), None)
					if check:
						arr[sz] = check.chart_value
					else:
						arr[sz] = ''
				size_chart_list.append(arr)
		size_chart = size_chart_list
		size_chart_params = unique_sizes
		return [size_charts,size_chart_params]

	def get_product_attribute_option(context,op,varients,video_list):
		if op.image_list:
			images = json.loads(op.image_list)
			if len(images) > 0:
				images = sorted(images, key=lambda x: x.get('is_primary'), reverse=True)
				op.image_attribute = images[0].get('thumbnail')
				if op.is_pre_selected == 1:                     
					image = []
					for im in images:
						image.append({
										'original_image': im.get('image'), 
										'detail_image': im.get('detail_thumbnail'), 
										'detail_thumbnail': im.get('thumbnail')
									})
		if len(varients) >0:
			combination_img = varients[0]
			if combination_img.image_list:
				images = json.loads(combination_img.image_list)
				if len(images) > 0:
					images = sorted(
									images, 
									key = lambda x: x.get('is_primary'),
									reverse = True
								)
					image=[]
					for im in images:
						image.append({'original_image': im.get('image'),
										'detail_image': im.get('detail_thumbnail'),
										'detail_thumbnail': im.get('thumbnail')
									})
			attribute_video = frappe.get_all('Product Attribute Option Video',
											filters = {"option_id":combination_img.name},
											fields = ["youtube_video_id","video_type"])
			if attribute_video:
				for video in attribute_video:
					if video.youtube_video_id:
						video_list.append({
											'video_link':video.youtube_video_id,
											'video_type':video.video_type
										})
		if op.is_pre_selected == 1:
			attribute_video = frappe.get_all('Product Attribute Option Video',
												filters = {"option_id":op.name},
												fields = ["youtube_video_id","video_type"])
			if attribute_video:
				for video in attribute_video:
					if video.youtube_video_id:
						video_list.append({
											'video_link':video.youtube_video_id, 
											'video_type':video.video_type
											})
		return image
			
	def get_product_brand(self,context):
		if self.status != 'Approved':
			frappe.local.flags.redirect_location = '/404'
			raise frappe.Redirect
		context.brands = frappe.db.sql('''SELECT B.name, B.brand_name, B.brand_logo, B.route, 
											B.warranty_information AS warranty_info, B.description 
										FROM `tabProduct Brand` AS B 
										INNER JOIN `tabProduct Brand Mapping` AS PBM 
											ON B.name = PBM.brand 
										WHERE PBM.parent = %(parent)s 
										GROUP BY B.name 
										ORDER BY PBM.idx ''', {'parent': self.name}, as_dict = 1)
		self.get_product_reviews(context)
		productattributes = frappe.db.get_all('Product Attribute Mapping',
												fields = ["*"], 
												filters = {"parent":self.name},
												order_by = "display_order",
												limit_page_length = 50
											)
		image = []
		if self.product_images:
			for item in self.product_images:
				image.append({
								"original_image":item.product_image,
								"product_image":item.detail_image,
								"detail_image":item.detail_image,
								"detail_thumbnail":item.detail_thumbnail
							})
		if self.product_images:
			context.og_image = self.product_images[0].product_image
		path1 = frappe.local.request.path
		context.page_url = get_url() + path1
		return productattributes
			

	def get_specification_group(self,context,catalog_settings,product_attributes,video_list):
		if catalog_settings.product_thumbnail_image_position:
			context.image_position = catalog_settings.product_thumbnail_image_position
		context.catalog_settings = catalog_settings
		context.attributes=product_attributes
		from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.product \
											import get_enquiry_product_detail
		context.type_of_category = get_enquiry_product_detail(self.name)
		specification_group = []
		specification_attribute = frappe.db.sql_list('''SELECT DISTINCT SAM.spec_group_name,
															SG.display_order 
														FROM  `tabSpecification Group` SG 
														INNER JOIN 
															`tabProduct Specification Attribute Mapping` SAM 
															ON SG.name = SAM.spec_group_name1 
														WHERE SAM.parent = %(name)s 
														ORDER BY SAM.idx
													''', {'name': self.name})
		if specification_attribute:
			for item in specification_attribute:
				groups = frappe.db.get_all('Product Specification Attribute Mapping',
											fields = ['specification_attribute','options'], 
											filters = {"parent":self.name,'spec_group_name':item},
											order_by = 'idx')
				specification_group.append({"name":item, "groups":groups})
		context.specification_attribute_grouping = specification_group
		demovideo = frappe.db.get_all('Product Video',
										fields = ["*"], 
										filters = {"parent":self.name},
										order_by = "display_order")
		context.demo_video = demovideo
		if len(video_list)>0:
			context.demo_video = video_list
		if frappe.session.user != 'Guest':
			update_customer_recently_viewed(self.name)
		context.page_path = get_url()
			

	def check_price_details(self,context,price_details,orgprice):
		if price_details:
			if price_details.get('discount_amount'):
				orgprice = price_details.get('rate')
			context.discount_rule = price_details.get('discount_rule')
			context.discount_label = price_details.get('discount_label')
		if flt(orgprice) != flt(self.price):
			context.old_price=self.price
			context.price=orgprice
		if self.disable_add_to_cart_button == 1:
			self.set_product_availability(0, 'Out of Stock', context)
		elif self.inventory_method=='Dont Track Inventory':
			self.set_product_availability(1, 'In Stock', context)
		elif self.inventory_method=='Track Inventory':
			if self.stock == 0:
				self.set_product_availability(0, 'Out of Stock', context)
			elif self.stock > 0:
				self.set_product_availability(1, 'In Stock', context)
		else:
			self.set_product_availability(1, 'In Stock', context)
		if self.meta_title:
			context.meta_title=self.meta_title if self.meta_title else self.item
		else:
			context.meta_title = context.catalog_settings.meta_title
		if self.meta_description:        
			context.meta_description=self.meta_description if self.meta_description else self.item 
		else:
			context.meta_description = context.catalog_settings.meta_description


	def get_custom_fields(self,context,catalog_settings):
		custom_values = []
		if catalog_settings.display_custom_fields == 1:
			if frappe.db.get_all("Custom Field",filters={"dt":"Product"}):
				custom_fields = frappe.db.sql('''SELECT label, fieldname 
													FROM `tabCustom Field` 
													WHERE dt = "Product" 
														AND fieldtype <> "Table" 
														AND fieldtype <> "Section Break" 
														AND fieldtype <> "Column Break" 
														AND fieldtype <> "HTML"  
														AND fieldtype <> "Check" 
														AND fieldtype <> "Text Editor" 
											''', as_dict=1)
				for field in custom_fields:
					query = f"""SELECT '{field.fieldname}'
								FROM `tabProduct`
								WHERE name = '{self.name}'
							"""
					custom_value = frappe.db.sql(query,as_dict=1)
					custom_values.append({
											"field":field.fieldname,
											"label":field.label,
											"value":custom_value[0][field.fieldname]
										})
		context.custom_values = custom_values
		context.product_name = self.item.replace("'","").replace('"','')
		recent_products = []
		best_sellers_list = []
		if catalog_settings.detail_page_template == "Default Layout":
			recent_products = get_recent_products()
			from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.product \
				import get_bestsellers
			best_sellers_list = get_bestsellers(None,limit=5)
		context.recent_products = recent_products
		context.best_sellers = best_sellers_list
		context.product_category = context.item_categories
		if not self.return_policy:
			context.return_description = ""


	def get_product_mapping(self,context, catalog_settings, orgprice):
		allow_review = 0
		if frappe.session.user != 'Guest':
			allow_review = 1
		else:
			if context.catalog_settings.allow_anonymous_users_to_write_product_reviews:
				allow_review = 1
		context.allow_review = allow_review
		ziprange = frappe.request.cookies.get("ziprange")
		context.ziprange = ziprange
		categories_list = frappe.db.sql('''SELECT category, category_name 
											FROM `tabProduct Category Mapping` 
											WHERE parent = %(parent)s 
											ORDER BY idx 
											LIMIT 1 ''', {'parent': self.name}, as_dict=1)
		if categories_list:
			product_category = frappe.db.get_all('Product Category',
												fields = ["*"], 
												filters = {"name":categories_list[0].category},
												order_by = "display_order",
												limit_page_length = 1)
			context.item_categories = product_category[0]
		self.set_tax_rate(context,catalog_settings,orgprice)
		if context.map_api:
			self.check_website_product_available(context)
		product_enquiry = get_product_scroll(self.name, 1, 5)
		context.product_enquiry = product_enquiry
		context.mobile_page_title = self.item
		if self.product_attributes:
			for item in self.product_attributes:
				if not "Table" in item.control_type:
					context.control_type_check = 1
		advance_amount = 0
		context.advance_amount = advance_amount


	def get_product_reviews(self, context):     
		context.approved_reviews = get_product_reviews_list(self.name, 0, 10)
		if context.catalog_settings.upload_review_images:
			review_images = frappe.db.sql('''SELECT RI.review_thumbnail, RI.image, RI.list_image, 
								 				RI.parent, RI.name, PR.product 
											FROM `tabProduct Review` PR 
											INNER JOIN `tabReview Image` RI ON PR.name = RI.parent 
											WHERE PR.product = %(product)s
										''', {'product': self.name}, as_dict=1)
			context.review_img = review_images


	def set_product_availability(self,allow_cart,stock_availability,context):
		context.allow_cart=allow_cart
		context.stock_availability=stock_availability


	def set_tax_rate(self, context,catalog_settings,orgprice):
		try:
			tax_rate1 = 0
			overall_tax_rates = 0
			if self.tax_category:
				tax_template=frappe.get_doc('Product Tax Template',self.tax_category)
				if tax_template and tax_template.tax_rates:
					item_tax = 0
					for tax in tax_template.tax_rates:
						if catalog_settings.included_tax:
							item_tax = item_tax + round(orgprice * tax.rate / (100 + tax.rate), 2)
						else:
							item_tax = item_tax + round(orgprice * tax.rate / 100, 2)
						overall_tax_rates = overall_tax_rates + tax.rate
					context.tax_rate1 = tax_rate1 + item_tax       
					context.overall_tax_rates = overall_tax_rates
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Error in doctype.product.set_tax_rate")

	def check_website_product_available(self, context):
		zipcode = state = country = city = None
		if context.customer_address:
			address = None
			if frappe.request.cookies.get('addressId'):
				address = next((x for x in context.customer_address if x.name == \
					frappe.request.cookies.get('addressId')), None)
			elif not frappe.request.cookies.get('guestaddress'):
				address = context.customer_address[0]
			if address:
				zipcode, city = address.zipcode, address.city
				state, country = address.state, address.country
		if not zipcode and frappe.request.cookies.get('guestaddress'):
			addr = unquote(frappe.request.cookies.get('guestaddress'))
			if addr.find(',') > -1:
				zipcode = addr.split(',')[0]
				state = addr.split(',')[1]
				country = addr.split(',')[2]
				city = addr.split(',')[3]
			else:
				zipcode = addr
				frappe.log_error("Zipcode",zipcode)          
				zipcode, city, state, country = get_location_details(zipcode)
				frappe.local.cookie_manager.set_cookie("guestaddress", '{0},{1},{2},{3}'.\
										   format(zipcode,state,country,city))
		if not zipcode:
			zipcode = '600001'
			city, state, country = 'Chennai', 'Tamil Nadu', 'India'
			frappe.local.cookie_manager.set_cookie("guestaddress", '{0},{1},{2},{3}'.\
										  format(zipcode,state,country,city))
		if zipcode:
			html = "zipcode :" + str(zipcode) + "\n"
			html += "state :" + str(state) + "\n"
			html += "country :" + str(country) + "\n"
			from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.product \
				import check_user_location_delivery
			res = check_user_location_delivery(zipcode, state, country)
			html += "res :" + str(res) + "\n"
			if res:
				context.delivery_area = res.get('allow')
				delivery_days = res.get('delivery_days')
				if delivery_days and type(delivery_days) == int:
					from_date = getdate(nowdate())
					to_date = add_days(from_date, int(delivery_days))
					context.delivery_date = '{0}'.format(to_date.strftime('%a, %b %d'))
				context.zipcode = zipcode
				context.city = city 


	def check_commission(self):     
		if self.commission_category:
			commission=frappe.db.sql('''SELECT * 
										FROM `tabVendor Detail` 
										WHERE parent = %(category)s 
											AND (CASE WHEN product IS NOT NULL 
												THEN product = %(product)s ELSE 1 = 1 END)
									''', {'product': self.name, 'category': self.commission_category}, 
										as_dict = 1)
			if commission:
				self.commission_rate=commission[0].rate
				self.commission_amount=self.price*commission[0].rate/100
			else:
				cmm=frappe.get_doc('Commission Settings',self.commission_category)
				self.commission_rate=cmm.default_rate
				self.commission_amount=self.price*cmm.default_rate/100


	def validate_availability(self):
		from frappe.utils import add_to_date
		if not self.current_availability and not self.next_available_at:
			system_settings = frappe.get_single('System Settings')
			actual_date = datetime.now(timezone(system_settings.time_zone))
			dtfmt = '%Y-%m-%d %H:%M:%S'
			day=actual_date.strftime('%A')
			new_date=actual_date.replace(tzinfo=None)
			if not self.all_time:
				if self.menu_item_timings:
					for item in self.menu_item_timings:
						from_date = datetime.strptime(str(actual_date.date())+' '+\
															str(item.from_time),dtfmt)
						to_date=datetime.strptime(str(actual_date.date())+' '+str(item.to_time),dtfmt)
						if from_date > new_date and not self.next_available_at:
							self.next_available_at = from_date
						elif not self.next_available_at and len(self.menu_item_timings) == 1:
							self.next_available_at = add_to_date(from_date, days=1)
	

def remove_html_tags(text):
	try:
		"""Remove html tags from a string"""
		import re
		return re.sub(re.compile('<.*?>'), '', text)
	except Exception:
		frappe.log_error(frappe.get_traceback(), 
				   ' Error in product.events.remove_html_tags')


@frappe.whitelist(allow_guest=True)
def get_location_details(zipcode):
	city = state = country = None
	from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.utils.google_maps \
																import get_geolocation
	response = get_geolocation(zipcode)
	if response and response.get('address_components'):
		for item in response.get('address_components'):
			if "country" in item.get('types'):
				country = item.get('long_name')
			elif "administrative_area_level_1" in item.get('types'):
				state = item.get('long_name')
			elif "postal_code" in item.get('types'):
				zipcode = item.get('long_name')
			elif "locality" in item.get('types'):
				city = item.get('long_name')
			elif "administrative_area_level_2" in item.get('types'):
				city = item.get('long_name')
	return zipcode, city, state, country


@frappe.whitelist()
def get_related_option(addon,parent):
	try:
		Group = frappe.db.sql("""SELECT option_name 
								FROM `tabItem Option` 
								WHERE add_on = %s AND parent = %s
							""", (addon, parent))
		return Group
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.get_related_option") 


@frappe.whitelist()
def get_all_tags():
	""" get the tags set in the  """
	tags = frappe.get_all("Product Tag",
		fields=["title"], distinct=True)

	active_tags = [row.get("title") for row in tags]
	return active_tags


@frappe.whitelist()
def get_relatedoption(addon):
	try:
		Group = frappe.db.sql("""SELECT option_name 
								FROM `tabItem Option` 
								WHERE add_on = %s """, (addon))
    
		return Group
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.get_relatedoption") 


@frappe.whitelist()
def get_product_attribute_options(attribute,product,attribute_id):
	try:
		attributeoptions = frappe.db.sql("""SELECT * 
											FROM `tabProduct Attribute Option` 
											WHERE parent = %(product)s 
											AND attribute = %(attribute)s 
											AND attribute_id = %(attribute_id)s
										""", {"product": product, "attribute": attribute, 
											"attribute_id": attribute_id}, as_dict = 1)
		return attributeoptions
	except Exception:
		frappe.log_error(frappe.get_traceback(),
				   "Error in doctype.product.get_product_attribute_options") 


@frappe.whitelist()
def get_parent_product_attribute_options(attribute,product):
	try:
		query = f"""SELECT *
					FROM `tabProduct Attribute Option`
					WHERE parent = '{product}' AND attribute = '{attribute}'
					ORDER BY idx ASC
				"""
		attributeoptions = frappe.db.sql(query, as_dict = 1)
		return attributeoptions
	except Exception:
		frappe.log_error(frappe.get_traceback(),
				   "Error in doctype.product.get_product_attribute_options") 


@frappe.whitelist()
def get_product_specification_attribute_options(attribute):
	try:
		attributeoptions = frappe.db.sql(""" SELECT option_value 
											FROM `tabSpecification Attribute Option` 
											WHERE parent = %(attribute)s 
											ORDER BY display_order
										""", {"attribute": attribute}, as_dict = 1)
		return attributeoptions
	except Exception:
		frappe.log_error(frappe.get_traceback(),
				"Error in doctype.product.get_product_specification_attribute_options") 


@frappe.whitelist()
def insert_product_attribute_options(attribute,product,option,display_order,price_adjustment,
									weight_adjustment,image,pre_selected,attribute_color,
									product_title,parent_option=None,attribute_id = None,
									disable=None,available_datetime=None):
	try:
		attributeoptions = frappe.db.sql("""SELECT * 
											FROM `tabProduct Attribute Option` 
											WHERE parent = %(product)s 
								   			AND attribute = %(attribute)s 
								   			AND attribute_id = %(attribute_id)s
										""", {"product": product, "attribute": attribute, 
												"attribute_id": attribute_id}, as_dict = 1)
		if len(attributeoptions) == 0:
			pre_selected = 1
		else:
			if int(pre_selected) == 1:
				for optionitem in attributeoptions:
					option_doc = frappe.get_doc("Product Attribute Option",optionitem.name)
					option_doc.is_pre_selected = 0
					option_doc.save()
		insert_product_attribute_option(attribute,product,option,display_order,price_adjustment,
									weight_adjustment,image,pre_selected,attribute_color,product_title,
									parent_option,attribute_id,disable,available_datetime)
		return frappe.db.sql("""SELECT * 
								FROM `tabProduct Attribute Option` 
								WHERE parent = %(product)s 
								AND attribute = %(attribute)s 
								AND attribute_id = %(attribute_id)s
							""", {"product": product, "attribute": attribute, 
			 					"attribute_id": attribute_id}, as_dict = 1)
	except Exception:
		frappe.log_error(frappe.get_traceback(),
				   "Error in doctype.product.insert_product_attribute_options")


def insert_product_attribute_option(attribute,product,option,display_order,price_adjustment,
									weight_adjustment,image,pre_selected,attribute_color,
									product_title,parent_option=None,attribute_id = None,
									disable=None,available_datetime=None):
	doc=frappe.get_doc({
			"doctype": "Product Attribute Option",
			"attribute":attribute,
			"attribute_id":attribute_id,
			"display_order":display_order,
			"price_adjustment":price_adjustment,
			"weight_adjustment":weight_adjustment,
			"attribute_color":attribute_color,
			"parent":product,
			"parenttype":'Product',
			"parentfield":'attribute_options',
			"option_value":option,
			"product_title":product_title,
			"image":image,
			"is_pre_selected":pre_selected,
			"parent_option":parent_option })
	doc.disable = int(disable)
	if int(disable)==1:
		doc.available_datetime = available_datetime
	doc.insert()
		

@frappe.whitelist()
def update_product_attribute_options(attribute,product,option,display_order,price_adjustment,
									weight_adjustment,optionid,image,pre_selected,attribute_color,
									product_title,parent_option=None,attribute_id = None, 
									disable=None,available_datetime=None):
	try:
		attributeoptions = frappe.db.sql("""SELECT * 
											FROM `tabProduct Attribute Option` 
											WHERE parent = %(product)s 
								   			AND attribute = %(attribute)s 
								   			AND attribute_id = %(attribute_id)s
										""", {"product": product, "attribute": attribute, 
											"attribute_id": attribute_id}, as_dict = 1)

		update_product_attribute_option(attributeoptions,attribute,product,option,display_order,
									price_adjustment,weight_adjustment,optionid,image,pre_selected,
									attribute_color,product_title,parent_option=None,
									attribute_id = None,disable=None,available_datetime=None)
		attributeoptions = frappe.db.sql("""SELECT * 
											FROM `tabProduct Attribute Option` 
											WHERE parent = %(product)s 
											AND attribute = %(attribute)s 
											AND attribute_id = %(attribute_id)s
										""", {"product": product, "attribute": attribute, 
											"attribute_id": attribute_id}, as_dict = 1)
		return attributeoptions
	except Exception:
		frappe.log_error(frappe.get_traceback(),
				   "Error in doctype.product.update_product_attribute_options") 


def update_product_attribute_option(attributeoptions,attribute,product,option,display_order,
									price_adjustment,weight_adjustment,optionid,image,pre_selected,
									attribute_color,product_title,parent_option=None,
									attribute_id = None,disable=None,available_datetime=None):
	if int(pre_selected) == 1:
		for x in attributeoptions:
			opt = frappe.get_doc("Product Attribute Option", x.name)
			opt.is_pre_selected = 0
			opt.save()
	doc=frappe.get_doc("Product Attribute Option",optionid)
	doc.attribute=attribute
	doc.attribute_id=attribute_id
	doc.display_order=display_order
	doc.parent=product
	doc.price_adjustment=price_adjustment
	doc.weight_adjustment=weight_adjustment
	doc.attribute_color=attribute_color
	doc.product_title=product_title
	doc.option_value=option
	doc.parent_option = parent_option
	doc.disable = int(disable)
	if int(disable)==1:
		doc.available_datetime = available_datetime
	doc.image=image
	doc.is_pre_selected=pre_selected
	doc.save()


@frappe.whitelist()
def get_all_brands():
	try:
		return frappe.db.sql('''SELECT brand_logo, name, brand_name, published 
								FROM `tabProduct Brand` 
								WHERE published = 1 
								ORDER BY brand_name''')
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.get_all_brands") 


@frappe.whitelist(allow_guest=True)
def get_all_category_list():    
	try:
		lists=[]
		cat = frappe.db.sql('''SELECT category_image, category_name, parent_category_name, is_active, name 
								FROM `tabProduct Category` 
								WHERE is_active = 1 
					  			AND (parent_product_category IS NULL OR parent_product_category = "")
							''', as_dict=1)
		if cat:
			for sub in cat:
				sub.indent = 0
				lists.append(sub)
				sub.subcat = get_sub_category_list(sub.name)
				if sub.subcat:
					for subsub in sub.subcat:
						subsub.indent = 1
						lists.append(subsub)
						subsub.subsubcat = get_sub_category_list(subsub.name)
						if subsub.subsubcat:
							for listcat in subsub.subsubcat:
								listcat.indent=2
								lists.append(listcat)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.get_all_category_list") 


@frappe.whitelist()
def get_sub_category_list(category):    
	try:
		s = frappe.db.sql('''SELECT 
								category_image, category_name, parent_category_name, is_active, name 
							FROM `tabProduct Category` 
							WHERE is_active = 1 AND parent_product_category = %(category)s
						''', {"category": category}, as_dict=1)
		return s
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.get_sub_category_list") 


@frappe.whitelist()
def approve_products(names,status):
	try:
		import json
		data = json.loads(names)
		if len(data)==0:
			frappe.msgprint(_('Please select any items'))
		else:
			for item in data:
				frappe.db.set_value('Product',item,'status',status)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.approve_products") 


@frappe.whitelist() 
def save_as_template(names, selected_business):
	try:
		import json
		data = json.loads(names)
		if len(data)==0:
			frappe.msgprint(_('Please select any items'))
		else:
			for item in data:
				doc = frappe.get_doc('Product', item).as_dict()
				if doc.template_saved!=1:
					vertical_name = re.sub('[^a-zA-Z0-9 ]', '', selected_business).lower().replace(' ','_')
					vertical_name1 = vertical_name+".json"
					path = frappe.get_module_path("ecommerce_business_store_singlevendor")
					path_parts=path.split('/')
					path_parts=path_parts[:-1]
					url='/'.join(path_parts)
					if not os.path.exists(os.path.join(url,'verticals')):
						frappe.create_folder(os.path.join(url,'verticals'))
					file_path = os.path.join(url, 'verticals', vertical_name1)
					data = []
					if os.path.exists(file_path):
						with open(file_path, 'r') as f:
							data = json.load(f)
							data.append(doc)
						with open(os.path.join(url,'verticals', (vertical_name+'.json')), "w") as f:
							f.write(frappe.as_json(data))
					else:
						doc1 = []
						doc1.append(doc)
						with open(os.path.join(url,'verticals', (vertical_name+'.json')), "w") as f:
							f.write(frappe.as_json(doc1))
					frappe.db.set_value('Product',item,'template_saved',1)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.save_as_template") 


@frappe.whitelist()
def get_product_attributes_with_options(product):
	attributes=frappe.db.get_all('Product Attribute Mapping',filters={'parent':product},
							  fields=['name','product_attribute','is_required','control_type',
				 				'attribute_unique_name','attribute'],order_by='display_order')
	if attributes:
		for item in attributes:
			item.options=get_product_attribute_options(item.product_attribute,product,item.name)            
	return attributes


@frappe.whitelist()
def create_variant_combinations(attributes):
	try:
		import json
		options = []
		all_options = []
		response = json.loads(attributes)
		p_combinations = frappe.db.get_all("Product Variant Combination",
										filters={"parent":json.loads(attributes)[0].get("product")},
										fields=['attribute_id'])
		for item in response:
			if item.get('attroptions'):
				li = [x.get('option_value') for x in item.get('attroptions')]
				options.append(li)
			all_options += item.get('attroptions')
		import itertools
		combination = list(itertools.product(*options))
		lists = []
		sku_seq = frappe.db.get_all("Product Variant Combination",
								filters={"parent":json.loads(attributes)[0].get("product")},
								fields=['sku'],order_by="sku desc",limit_page_length=1)
		lists = get_combination_list(sku_seq,combination,all_options,p_combinations,attributes,lists)
		return lists
	except Exception:
		frappe.log_error(title = "create_variant_combinations", message = frappe.get_traceback())
		frappe.response.status = "failed"
	
def get_combination_list(sku_seq,combination,all_options,p_combinations,attributes,lists):
	sku_no = 0
	if sku_seq:
		if sku_seq[0].sku:
			l_sku = sku_seq[0].sku
			sku_no = int(l_sku[-3:])+1
	for item in combination:
		html=''
		ids=''
		price=0
		variant_text = ""
		attributes_json = []
		for li in item:
			check=next((x for x in all_options if x.get('option_value')==li),None)
			if check and check.get('name'):
				attribute_name = frappe.db.get_value("Product Attribute", \
										 check.get('attribute'), "attribute_name")
				ids+=check.get('name')+'\n'
				html+='<div data-name="'+str(ids)+'" class="btn btn-default btn-xs btn-link-to-form" \
					style="border: 1px solid #d1d8dd;margin: 2px;min-width: 50px;text-align: left;">\
					<p style="text-align: left;margin: 0px;font-size: 11px;">'+attribute_name+'</p> \
					<span style="font-weight: 700;">'+li+'</span></div>'
				price+=check.get('price_adjustment')
				variant_text+= li+" , "
				attributes_json.append(check.get('name'))
		if ids:
			if not any(obj['attribute_id'] == ids for obj in p_combinations):
				v_sku = json.loads(attributes)[0].get("product").split("ITEM-")[1]+'%03d' % sku_no
				p_title = frappe.db.get_value("Product",json.loads(attributes)[0].\
								  get("product"),"item")+" - "+get_attributes_text(attributes_json)
				lists.append({'sku':v_sku,'product_title':p_title,'attribute_html':html,\
				  'attribute_id':ids, 'stock': 1,'price':price, 'attributes_json': attributes_json})
				sku_no = sku_no + 1
		else:
			frappe.throw(_("Please add and save the attribute options to create the combinations"))
	return lists

@frappe.whitelist()
def get_attributes_text(attributes_json):
	combination_txt=""
	if attributes_json:
		variant = (attributes_json)
		attribute_html = ""
		for obj in variant:
			if attribute_html:
				attribute_html +=", "
			option_value, attribute = frappe.db.get_value("Product Attribute Option", obj, \
												 ["option_value","attribute"])
			attribute_name = frappe.db.get_value("Product Attribute", attribute, "attribute_name")
			attribute_html += attribute_name+":"+option_value
		combination_txt = attribute_html
	return combination_txt
@frappe.whitelist()
def get_category_based_attributes(txt,filters):
	condition=''
	if filters.get('productId'):
		category_list = frappe.db.sql('''SELECT GROUP_CONCAT(CONCAT('"', category, '"')) category 
										FROM `tabProduct Category Mapping` 
										WHERE parent = %(product)s
									''', {'product': filters.get('productId')}, as_dict=1)
		if txt:
			condition += ' and (a.name like %(txt)s or a.attribute_name like %(txt)s)'      
		cat_list = '""'
		if category_list and category_list[0].category:
			cat_list = category_list[0].category
		return frappe.db.sql('''SELECT A.name, A.attribute_name 
								FROM `tab{doctype}` A 
								LEFT JOIN `tabBusiness Category` C 
								ON A.name = C.parent 
								WHERE (CASE WHEN C.category IS NOT NULL 
										THEN C.category IN ({category}) ELSE 1=1 END ) {condition}
							'''.format(category=cat_list, doctype=filters.get('type'), 
								condition=condition), {'txt': '%' + txt + '%'})
	return frappe.db.sql('''SELECT name 
							FROM 
								`tab{doctype}` '''.format(doctype=filters.get('type')))


@frappe.whitelist()
def get_vendor_based_tax_templates():
	return frappe.db.sql('''SELECT name 
							FROM 
								`tabProduct Tax Template` ''')


@frappe.whitelist()
def get_vendor_based_return_policy():
	return frappe.db.sql('''SELECT name 
							FROM 
								`tabReturn Policy` ''')


@frappe.whitelist()
def update_image(imageId,image_name,is_primary):
	doc=frappe.get_doc('Product Image',imageId)
	doc.image_name=image_name
	doc.is_primary=is_primary
	doc.save(ignore_permissions=True)


@frappe.whitelist()
def delete_product_attribute_option(option):
	try:
		attribute_video = frappe.db.sql('''SELECT name, option_id 
											FROM 
												`tabProduct Attribute Option Video` 
											WHERE 
												option_id = %(option_id)s
										''', {'option_id': option}, as_dict=1)
		if attribute_video:
			for video in attribute_video:
				video_doc = frappe.get_doc('Product Attribute Option Video',video.name)
				video_doc.delete()
		doc=frappe.get_doc("Product Attribute Option", option)
		if doc.get('image_list'):
			images = json.loads(doc.get('image_list'))
			from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.product \
				import delete_attribute_image
			for im in images:
				delete_attribute_image(im)
		doc.delete()
		return {'status':'success'}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 
				   "Error in doctype.product.product.delete_product_attribute_option")

@frappe.whitelist()
def delete_product_attribute_option_image(ref_doctype, file_url):
	try:
		frappe.db.sql('''DELETE FROM `tabFile` 
						WHERE 
							attached_to_doctype = %(ref_doctype)s 
							AND file_url = %(file_url)s
					''', {'file_url': file_url, 'ref_doctype': ref_doctype})
		return {'status': "Success"}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(),
			"Error in doctype.product.product.delete_product_attribute_option_image")


def randomStringDigits(stringLength=6):
	import random
	import string
	lettersAndDigits = string.ascii_uppercase + string.digits
	return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


@frappe.whitelist(allow_guest=True)
def update_product_categories(category1,name):
	frappe.db.sql('''DELETE 
					FROM `tabProduct Category Mapping` 
					WHERE 
						parent = %(name)s ''', {'name': name})
	for x in json.loads(category1):
		paper_question = frappe.new_doc("Product Category Mapping")
		paper_question.category=x['category']
		paper_question.category_name=x['category_name']
		paper_question.parent=name
		paper_question.parentfield="product_categories"
		paper_question.parenttype="Product"
		paper_question.save()


@frappe.whitelist(allow_guest=True)
def update_product_categories1(category1,name):
	frappe.db.sql('''DELETE FROM 
						`tabProduct Category Mapping` 
					WHERE 
						parent = %(name)s ''', {'name': name})

	for x in json.loads(category1):
		paper_question = frappe.new_doc("Product Category Mapping")
		paper_question.category=x
		paper_question.parent=name
		paper_question.parentfield="product_categories"
		paper_question.parenttype="Product"
		paper_question.save()


@frappe.whitelist()
def update_image(count,image_name,primary,childname):
	if image_name:
		frappe.db.set_value('Product Image', childname, 'idx', count)
		frappe.db.set_value('Product Image', childname, 'image_name', image_name)
		frappe.db.set_value('Product Image', childname, 'is_primary', primary)


def format_convertion(price=None):
	magnitude = 0
	num = flt(price)
	while abs(num) >= 100000:
		magnitude += 1
		num /= 100000.0
	rounded_amt = ('%.2f%s' % (num, ['','L'][magnitude]))
	return rounded_amt


@frappe.whitelist(allow_guest = True)
def get_product_scroll(item, page_no, page_len):
	try:
		start = (int(page_no) - 1) * int(page_len)
		product_enquiry = frappe.db.sql('''SELECT PQ.name, PQ.user_name, PQ.email, PQ.phone, 
												PQ.product, PQ.question, 
												DATE_FORMAT(PQ.creation, "%d, %b %Y") as creation,
												GROUP_CONCAT(PA.answer SEPARATOR ";") as ans_list 
											FROM 
												`tabProduct Enquiry` PQ 
											LEFT JOIN 
												`tabProduct Enquiry Answers` PA 
											ON 
												PQ.name = PA.parent 
											WHERE 
												PQ.product = "{name}" 
												AND is_approved=1 
											GROUP BY 
												PQ.name 
											LIMIT {start}, {limit}
										'''.format(start=start, limit=page_len, name=item), as_dict=1)
		return product_enquiry
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.product.get_product_scroll")


@frappe.whitelist(allow_guest=True)
def get_review_scroll(item, page_no, page_len):
	start=(int(page_no)-1)*int(page_len)
	dateformat='%b %d, %Y'
	Reviews=frappe.db.sql('''SELECT RI.review_thumbnail,RI.image,RI.list_image, PR.customer,RI.email,
								DATE_FORMAT(PR.creation, %(format)s) as date,
								PR.review_title,PR.review_message,PR.rating,PR.name 
							FROM 
								`tabProduct Review` PR 
							INNER JOIN 
								`tabReview Image` RI 
							ON 
								PR.name = RI.parent 
							WHERE 
								PR.product = %(item)s 
							ORDER BY 
								PR.creation DESC 
							LIMIT {start}, {limit}
						'''.format(start=start, limit=page_len), {'item': item, 
												'format': dateformat}, as_dict=1)
	return Reviews


@frappe.whitelist(allow_guest=True) 
def get_review_images(name,product):
	dateformat='%b %d, %Y'
	approved_reviews1 = frappe.db.sql('''SELECT RI.review_thumbnail,RI.image,RI.list_image,RI.name,
											RI.parent,PR.*,
											DATE_FORMAT(PR.creation, %(format)s) as date 
										FROM 
											`tabProduct Review` PR 
										INNER JOIN 
											`tabReview Image` RI 
										ON 
											PR.name = RI.parent 
										WHERE 
											PR.product = %(product)s
									''', {'product': product, 'format': dateformat}, as_dict=1)
	return approved_reviews1


@frappe.whitelist(allow_guest=True)
def get_curreview_images(name):
	dateformat='%b %d, %Y'
	approved_review = frappe.db.sql('''SELECT RI.review_thumbnail,RI.image,RI.list_image,RI.parent,PR.*,
											DATE_FORMAT(PR.creation, %(format)s) as date 
										FROM 
											`tabProduct Review` PR 
										INNER JOIN 
											`tabReview Image` RI 
										ON 
											PR.name = RI.parent 
										WHERE 
											PR.name = %(name)s
									''', {'name': name, 'format': dateformat}, as_dict=1)
	return approved_review


@frappe.whitelist(allow_guest=True)
def check_product_attribute_options(product_attributes = None):
	if product_attributes:
		attribute_len = frappe.get_list("Product Attribute Option",fields = ['name'],
								  filters={'attribute_id' : product_attributes})
		if attribute_len > 0:
			return "true"
		else:
			return "false"
	else:
		pass


@frappe.whitelist(allow_guest=True)
def get_product_reviews_list(product, page_no=0, page_len=10):
	start = int(page_no) * int(page_len)
	dateformat='%b %d, %Y'
	reviews = frappe.db.sql('''SELECT name,customer, email, review_title, review_message, rating, 
									DATE_FORMAT(creation, %(format)s) as date, 
									creation 
								FROM 
									`tabProduct Review` 
								WHERE 
									product = %(product)s 
									AND is_approved = 1 
								ORDER BY 
									creation DESC 
								LIMIT {start}, {limit}
							'''.format(start=start, limit=page_len), {'product': product, 
												 'format': dateformat}, as_dict=1)
	upload_image = get_settings_value('Catalog Settings', 'upload_review_images')
	if upload_image:
		for image in reviews:
			image.review_images=frappe.db.get_all('Review Image',fields=['review_thumbnail',
									'image','list_image','name'],filters={'parent':image.name})
	return reviews


@frappe.whitelist(allow_guest=True)
def update_customer_recently_viewed(product, customer=None):
	enable_recently_viewed = get_settings_value('Catalog Settings', 'enable_recetly_viewed_products')
	if enable_recently_viewed:
		if not customer:
			if frappe.request.cookies.get('customer_id'):
				customer = unquote(frappe.request.cookies.get('customer_id'))
		if customer:
			check_already_viewed = frappe.get_all("Customer Viewed Product",
										 filters={'parent':customer,'product':product})
			if not check_already_viewed:
				customer_viewed_product = frappe.new_doc("Customer Viewed Product")
				customer_viewed_product.parent = customer
				customer_viewed_product.parenttype = "Customers"
				customer_viewed_product.parentfield = "viewed_products"
				customer_viewed_product.product = product
				customer_viewed_product.product_name = frappe.db.get_value('Product', product, 'item')
				customer_viewed_product.viewed_date = getdate(nowdate())
				customer_viewed_product.viewed_count = 1
				customer_viewed_product.save(ignore_permissions=True)
				frappe.db.commit()
			else:
				check_already_viewed_update = check_already_viewed[0]
				customer_viewed_product = frappe.get_doc("Customer Viewed Product", 
											 	check_already_viewed_update.name)
				customer_viewed_product.viewed_date = getdate(nowdate())
				customer_viewed_product.viewed_count = int(customer_viewed_product.viewed_count) + 1
				customer_viewed_product.save(ignore_permissions=True)
				frappe.db.commit()


@frappe.whitelist()
def show_attribute_err(attribute_id):
	attribute_option = frappe.get_list("Product Attribute Option", 
									fields = ["attribute_id"], 
									filters = {"attribute_id": attribute_id})
	if attribute_option:
		return attribute_option
	else:
		return "Failed"


@frappe.whitelist()
def check_attr_combination(self):
	if len(self.variant_combination) > 0:
		for i in self.variant_combination:
			att_id = '"' + '","'.join(i.attribute_id.split("\n"))[:-2]
		options = frappe.db.sql('''SELECT name 
									FROM 
										`tabProduct Attribute Option` 
									WHERE 
										parent = %(parent)s 
										AND name NOT IN ({0})
								'''.format(att_id), {'parent': self.name}, as_dict = 1)
		if options:
			pass
		else:
			frappe.throw("Please delete Attribute combinations and then try to delete attribute")


@frappe.whitelist()
def delete_attribute_option_alert(option):
	combination = frappe.db.sql('''SELECT name, attribute_id 
									FROM 
										`tabProduct Variant Combination` ''', as_dict = 1)
	att_id_arr = []
	for i in combination:
		att_id = (i.attribute_id.split("\n"))[:-2]
		for item in att_id:
			att_id_arr.append(str(item))
	attributes = frappe.get_doc("Product Attribute Option", option)
	if option  in att_id_arr:   
		frappe.throw("Cannot delete because Product Attribute Option " + attributes.option_value+ "is \
			   												linked with Product Attribute Combination")
	else:
		return "Success"


@frappe.whitelist()
def show_attribute_deletion_err(item, row_id):
	combination = frappe.db.sql('''SELECT name, attribute_id 
									FROM 
										`tabProduct Variant Combination` 
									WHERE 
										parent = %(parent)s
								''', {'parent': item}, as_dict = 1)
	att_id_arr = '""'
	for i in combination:
		att_id = (i.attribute_id.split("\n"))
		att_id_arr = ",".join(['"' + x + '"' for x in att_id if x])
	attributes = frappe.db.sql('''SELECT name, attribute_id 
									FROM 
										`tabProduct Attribute Option` 
									WHERE 
										attribute_id = %(attr_id)s 
										AND name IN ({lists})
								'''.format(lists=att_id_arr), {'attr_id': row_id}, as_dict = 1)
	if attributes:
		return 'Failed'


@frappe.whitelist()
def check_attr_combination_price(self):
	if len(self.variant_combination) > 0:
		for i in self.variant_combination:
			if flt(i.price)<flt(self.price):
				frappe.throw("Attribute combination price should be greater than or equal to base price")

@frappe.whitelist()
def delete_attribute_options(dt, dn):
	try:
		doc = frappe.get_doc(dt, dn)
		attribute_options = get_product_attribute_options(doc.product_attribute, doc.parent, doc.name)
		for item in attribute_options:
			attribute_video1 = frappe.db.sql('''SELECT 
													name, 
													option_id 
												FROM 
													`tabProduct Attribute Option Video` 
												WHERE 
													option_id = %(option_id)s
											''', {'option_id': item.name}, as_dict=1)
			if attribute_video1:
				for video1 in attribute_video1:
					frappe.db.sql('''DELETE FROM 
										`tabProduct Attribute Option Video` 
									WHERE 
										name = %(name)s
								''', {'name': video1.name})
			if item.get('image_list'):
				from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.product \
																		import delete_attribute_image
				images = json.loads(item.get('image_list'))
				for im in images:
					delete_attribute_image(im)
			frappe.db.sql('''DELETE FROM 
								`tabProduct Attribute Option` 
							WHERE 
								name = %(name)s
						''', {'name': item.name})
		return {'status': 'success'}
	except Exception as e:
		return {'status': 'Failed'}


@frappe.whitelist(allow_guest=True)
def insert_attribute_option_video(option_id,video_id,video_type):
	attribute_option_video = frappe.new_doc("Product Attribute Option Video")
	attribute_option_video.option_id = option_id
	attribute_option_video.youtube_video_id = video_id
	attribute_option_video.video_type = video_type
	attribute_option_video.save(ignore_permissions=True)
	attributeoptions_video = frappe.db.sql("""SELECT * 
											FROM 
												`tabProduct Attribute Option Video` 
											WHERE 
												option_id = %(option_id)s
										""", {"option_id": option_id}, as_dict = 1)

	if attributeoptions_video:
		return attributeoptions_video

@frappe.whitelist()     
def get_attribute_option_videos(option_id):
	attributeoptions_video = frappe.db.sql("""SELECT * 
											FROM 
												`tabProduct Attribute Option Video` 
											WHERE 
												option_id = %(option_id)s
										""", {"option_id": option_id}, as_dict = 1)
	if attributeoptions_video:
		return attributeoptions_video


@frappe.whitelist()
def delete_product_attribute_option_video(name):
	doc = frappe.get_doc('Product Attribute Option Video', name)
	doc.delete()
	return {'status': "Success"}

@frappe.whitelist()
def update_attribute_option_video(name,video_id,option_id,video_type):
	frappe.db.set_value('Product Attribute Option Video',name,'youtube_video_id',video_id)
	frappe.db.set_value('Product Attribute Option Video',name,'video_type',video_type)
	attributeoptions_video = frappe.db.sql("""SELECT * 
											FROM 
												`tabProduct Attribute Option Video` 
											WHERE 
												option_id = %(option_id)s
										""", {"option_id": option_id}, as_dict = 1)
	if attributeoptions_video:
		return attributeoptions_video


@frappe.whitelist(allow_guest=True)   
def get_all_category_lists(product_group=None):
	item_group = frappe.db.get_all("Product Category", fields=["*"], filters={"is_active":1})
	for n in item_group:
		child_groups = ", ".join(['"' + frappe.db.escape(i[0]) + '"' for i in get_child_groups(n.name)])
		parent_category = get_parent_item_groups(n.name)
		

@frappe.whitelist()
def get_parent_item_groups(item_group_name):
	item_group = frappe.get_doc("Product Category", item_group_name)
	return frappe.db.sql("""SELECT name, category_name 
							FROM 
								`tabProduct Category`
							WHERE 
								lft <= %s 
								AND rgt >= %s
								AND is_active = 1
							ORDER BY 
								lft ASC
						""", (item_group.lft, item_group.rgt), as_dict=True)


def get_child_groups(item_group_name):
	item_group = frappe.get_doc("Product Category", item_group_name)
	return frappe.db.sql("""SELECT name, category_name 
							FROM 
								`tabProduct Category`
							WHERE 
								lft >= %(lft)s 
								AND rgt <= %(rgt)s
								AND is_active = 1
						""", {"lft": item_group.lft, "rgt": item_group.rgt})


def get_child_categories1(category):
	try:
		lft, rgt = frappe.db.get_value('Product Category', category, ['lft', 'rgt'])
		return frappe.db.sql('''SELECT name 
								FROM 
									`tabProduct Category`
								WHERE 
									is_active = 1 
									AND disable_in_website = 0 
									AND lft >= {lft} 
									AND rgt <= {rgt}
							'''.format(lft=lft, rgt=rgt), as_dict=1)
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'Error in api.get_child_categories')


@frappe.whitelist()
def get_category_list(reference_doc, reference_fields, filters=None, page_no=1, page_len=20, 
					  								search_txt=None, search_field="name"):
	reference_field = json.loads(reference_fields)
	condition = ''
	start = (int(page_no) - 1) * int(page_len)
	if search_txt:
		searchKey = '"%' + search_txt + '%"'
		condition += ' and {search_field} like {search_txt}'.format(search_field=search_field, 
															  search_txt=searchKey)
	fields = ','.join([x for x in reference_field])
	list_len = frappe.db.sql('''SELECT {field} 
								FROM 
									`tab{dt}`
								WHERE 
									is_active = 1 
									{cond} 
								ORDER BY 
									lft
							'''.format(field=fields, dt=reference_doc, cond=condition), as_dict=1)
	list_name = frappe.db.sql('''SELECT {field} 
								FROM 
									`tab{dt}` 
								WHERE 
									is_active = 1 {cond} 
								ORDER BY 
									lft 
								LIMIT 
									{page_no}, {page_len}
							'''.format(field=fields, dt=reference_doc, cond=condition, 
				  						page_no=start, page_len=page_len), as_dict=1)
	if list_name:
		for content in list_name:
			if content.name:
				parent_groups = get_parent_item_groups(content.name)
				if parent_groups:
					parent = ''
					for i in range(0,len(parent_groups)):
						if i != len(parent_groups)-1:
							parent += str(parent_groups[i].category_name)+' >> '
						else:
							parent += str(parent_groups[i].category_name)
					content.parent_categories = parent  
	return {"list_name":list_name, "list_len":len(list_len)}


@frappe.whitelist(allow_guest=True)
def get_category_attributes(reference_doc, reference_fields, filters=None,page_no=1, page_len=20, 
															search_txt=None, search_field="name"):
	condition = ''
	category = ''
	start = (int(page_no) - 1) * int(page_len)
	user = frappe.session.user
	if isinstance(filters, string_types):
		filters = json.loads(filters)
	if filters:
		category = ','.join('"{0}"'.format(r["category"]) for r in filters)
	if search_txt:
		searchKey = '"%' + search_txt + '%"'
		condition += ' and A.{search_field} like {search_txt}'.format(search_field=search_field, 
																			search_txt=searchKey)

	query = '''SELECT A.name, A.attribute_name 
				FROM 
					`tabProduct Attribute` A 
				WHERE 
					A.name != "" {condition} 
				GROUP BY 
					A.name, 
					A.attribute_name 
				LIMIT 
					{page_no}, {page_len}
			'''.format(category=category, condition=condition, page_no=start, page_len=page_len)
	list_name = frappe.db.sql('''{query}'''.format(query=query), as_dict=True)
	list_len = frappe.db.sql('''SELECT A.name, A.attribute_name 
								FROM 
									`tabProduct Attribute` A 
								WHERE 
									A.name != "" {condition} 
								GROUP BY 
									A.name, 
									A.attribute_name 
							'''.format(condition=condition), as_dict=True)
	return {"list_name":list_name, "list_len":len(list_len)}


@frappe.whitelist()
def get_returnpolicy_list(reference_doc, reference_fields, filters=None,page_no=1, 
						  		page_len=20, search_txt=None, search_field="name"):
	start = (int(page_no) - 1) * int(page_len)
	reference_field = json.loads(reference_fields)
	condition = ''
	if search_txt:
		searchKey = '"%' + search_txt + '%"'
		condition += ' and {search_field} like {search_txt}'.format(search_field=search_field, 
															  search_txt=searchKey)
	if filters:
		condition += filters
	fields = ','.join([x for x in reference_field])
	if reference_doc=="Product":
		condition += " and is_active=1 and status='Approved' "
	list_name = frappe.db.sql('''SELECT {field} 
								FROM 
									`tab{dt}` 
								WHERE 
									name != "" {cond} 
								LIMIT 
									{page_no}, {page_len}
							'''.format(field=fields, dt=reference_doc, cond=condition, 
				  						page_no=start, page_len=page_len), as_dict=1)
	list_len = frappe.db.sql('''SELECT {field} 
								FROM 
									`tab{dt}` 
								WHERE 
									name != "" {cond}
							'''.format(field=fields, dt=reference_doc, cond=condition), as_dict=1)
	return {"list_name":list_name, "list_len":len(list_len)}


@frappe.whitelist()
def get_specification_list(reference_doc, reference_fields, filters=None,page_no=1, page_len=20, 
						   									search_txt=None, search_field="name"):
	start = (int(page_no) - 1) * int(page_len)
	reference_field = json.loads(reference_fields)
	condition = ''
	if search_txt:
		searchKey = '"%' + search_txt + '%"'
		condition += ' and {search_field} like {search_txt}'.format(search_field=search_field, 
															  search_txt=searchKey)
	fields = ','.join([x for x in reference_field])
	list_name_query = '''SELECT {field} 
				FROM 
					`tab{dt}` 
				WHERE 
					name != "" {cond} 
				LIMIT 
					{page_no}, {page_len}
			'''.format(field=fields, dt=reference_doc, cond=condition, page_no=start, page_len=page_len)
	frappe.log_error("list_name_query",list_name_query)
	list_name = frappe.db.sql(list_name_query, as_dict=1)
	list_len_query = '''SELECT {field} 
								FROM 
									`tab{dt}` 
								WHERE 
									name != "" {cond}
							'''.format(field=fields, dt=reference_doc, cond=condition)
	frappe.log_error("list_len_query",list_len_query)
	list_len = frappe.db.sql(list_len_query, as_dict=1)
	
	return {"list_name":list_name, "list_len":len(list_len)}


@frappe.whitelist()
def get_brand_list(reference_doc, reference_fields, filters=None, page_no=1, page_len=20, 
				   									search_txt=None, search_field="name"):
	start = (int(page_no) - 1) * int(page_len)
	reference_field = json.loads(reference_fields)
	fields = ','.join([x for x in reference_field])
	condition = ''
	if search_txt:
		searchKey = '"%' + search_txt + '%"'
		condition += ' and {search_field} like {search_txt}'.format(search_field=search_field, 
															  search_txt=searchKey)
	list_name = frappe.db.sql('''SELECT {field} 
								FROM 
									`tab{dt}` 
								WHERE 
									published = 1 {cond} 
								LIMIT 
									{page_no}, {page_len}
							'''.format(field=fields, dt=reference_doc, cond=condition, page_no=start, 
				  													page_len=page_len), as_dict=1)

	list_len = frappe.db.sql('''SELECT {field} 
								FROM 
									`tab{dt}` 
								WHERE 
									published = 1 {cond}
							'''.format(field=fields, dt=reference_doc, cond=condition), as_dict=1)
	return {"list_name":list_name, "list_len":len(list_len)}


@frappe.whitelist()
def get_recent_products():
	try:
		role = frappe.get_roles(frappe.session.user)
		roles = ','.join('"{0}"'.format(r) for r in role)
		recent_products=frappe.db.sql(f'''SELECT P.name,P.price,P.item,P.route,P.image AS detail_thumbnail
										FROM 
											`tabProduct` P 
										WHERE 
											is_active = 1 
											AND status = "Approved"
										ORDER BY 
											creation DESC 
										LIMIT 5 ''', as_dict=1)
		return recent_products
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'Error in doctype.product.product.get_recent_products')


@frappe.whitelist()
def insert_attribute_template(attribute,product_attr,message):
	try:
		template = frappe.db.sql('''SELECT name 
									FROM 
										`tabProduct Attribute Template` 
									WHERE 
										attribute_id = %(attribute_id)s
								''', {'attribute_id': attribute}, as_dict=1)
		if template:
			check_already_value = frappe.delete_doc("Product Attribute Template",template[0].name)
		attribute_option = frappe.new_doc('Product Attribute Template')
		attribute_option.attribute_id = attribute
		attribute_option.attribute_name = product_attr
		attribute_options = []
		attribute_option.save(ignore_permissions=True)
		if attribute_option:
			docs = json.loads(message)
			for item in docs:
				doc=frappe.get_doc({
					"doctype": "Attribute Option",
					"attribute":item['attribute'],
					"attribute_id":item['attribute_id'],
					"option_value":item['option_value'],
					"display_order":item['display_order'],
					"price_adjustment":item['price_adjustment'],
					"parent":attribute_option.name,
					"parenttype":'Product Attribute Template',
					"parentfield":'attribute_options',
					"parent_option":item['parent_option'],
					"is_pre_selected": item['is_pre_selected'] })
				doc.insert(ignore_permissions=True)
		return "Success"
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'Error in doctype.product.product.insert_attribute_template')


@frappe.whitelist()
def select_attribute_template(template_name,attribute,product,attribute_id):
	try:
		option_template = frappe.db.sql('''SELECT name,attribute_id,attribute_name 
											FROM 
												`tabProduct Attribute Template` 
											WHERE 
												name = %(name)s ''', {'name': template_name}, as_dict=1)
		if option_template:
			opt_temp = frappe.db.sql('''SELECT * 
										FROM 
											`tabAttribute Option` 
										WHERE 
											parent = %(parent)s
									''', {'parent': option_template[0].name}, as_dict=1)
			if opt_temp:
				for item in opt_temp:
					doc=frappe.get_doc({
						"doctype": "Product Attribute Option",
						"attribute":attribute,
						"attribute_id":attribute_id,
						"display_order":item.display_order,
						"price_adjustment":item.price_adjustment,
						"weight_adjustment":item.weight_adjustment,
						"attribute_color":item.attribute_color,
						"parent":product,
						"parenttype":'Product',
						"parentfield":'attribute_options',
						"option_value":item.option_value,
						"parent_option":item.parent_option,
						"is_pre_selected":item.pre_selected,
						"disable":item.disable,
						"available_datetime":item.available_datetime })
					doc.insert(ignore_permissions=True)
				return frappe.db.sql("""SELECT * 
										FROM 
											`tabProduct Attribute Option` 
										WHERE 
											parent = %(product)s 
											AND attribute = %(attribute)s 
											AND attribute_id = %(attribute_id)s
									""", {"product": product,"attribute":attribute,"attribute_id":attribute_id}, as_dict = 1)
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'Error in doctype.product.product.select_attribute_template')


@frappe.whitelist()
def delete_option(name):
	frappe.db.sql('''DELETE FROM 
						`tabProduct Attribute Mapping` 
					WHERE 
						name = %(name)s ''', {'name': name})
	return "success"


@frappe.whitelist()
def insert_json(selected_business,name):
	doc = frappe.get_doc('Product', name).as_dict()
	vertical_name = re.sub('[^a-zA-Z0-9 ]', '', selected_business).lower().replace(' ','_')
	vertical_name1 = vertical_name+".json"
	path = frappe.get_module_path("ecommerce_business_store_singlevendor")
	path_parts=path.split('/')
	path_parts=path_parts[:-1]
	url='/'.join(path_parts)
	if not os.path.exists(os.path.join(url,'verticals')):
		frappe.create_folder(os.path.join(url,'verticals'))
	file_path = os.path.join(url, 'verticals', vertical_name1)
	data = []
	if os.path.exists(file_path):
		with open(file_path, 'r') as f:
			data = json.load(f)
			data.append(doc)
		with open(os.path.join(url,'verticals', (vertical_name+'.json')), "w") as f:
			f.write(frappe.as_json(data))
	else:
		doc1 = []
		doc1.append(doc)
		with open(os.path.join(url,'verticals', (vertical_name+'.json')), "w") as f:
			f.write(frappe.as_json(doc1))
	frappe.db.set_value('Product',doc.name,'template_saved',1)


@frappe.whitelist()
def get_order_settings():
	check_file_uploader = 0
	apps = frappe.get_installed_apps()
	if 'frappe_s3_attachment' in apps:
		s3_settings = frappe.get_single("S3 File Attachment")
		if s3_settings.aws_key and s3_settings.aws_secret and (not s3_settings.disable_s3_file_attachment or s3_settings.disable_s3_file_attachment==0):
			check_file_uploader = 1
	return {"order_settings":get_settings('Order Settings'),
			"s3_enable":check_file_uploader}


@frappe.whitelist()
def get_role_list(doctype, txt, searchfield, start, page_len, filters):
	condition=''
	if filters.get('productId'):
		category_list = frappe.db.sql('''SELECT group_concat(concat('"', category, '"')) category 
										FROM 
											`tabProduct Category Mapping` 
										WHERE 
											parent = %(product)s
									''', {'product': filters.get('productId')}, as_dict=1)
		if txt:
			condition += ' and (A.name like %(txt)s or A.attribute_name like %(txt)s)'      
		cat_list = '""'
		if category_list and category_list[0].category:
			cat_list = category_list[0].category
		return frappe.db.sql('''SELECT A.name, A.attribute_name 
								FROM 
									`tab{doctype}` A 
								LEFT JOIN 
									`tabBusiness Category` C ON A.name = C.parent 
								WHERE (CASE 
										WHEN C.category IS NOT NULL THEN C.category IN ({category}) 
										ELSE 1 = 1 END) {condition}
							'''.format(category=cat_list, doctype=filters.get('type'), 
				  						condition=condition), {'txt': '%' + txt + '%'})
	conditions = []
	return frappe.db.sql("""SELECT name 
							FROM 
								`tabRole`
							WHERE 
								disabled = 0 
								AND name NOT IN ("System Manager", "Administrator")
								AND ({key} LIKE %(txt)s)
								{fcond} {mcond}
							ORDER BY
								IF(LOCATE(%(_txt)s, name), 
									LOCATE(%(_txt)s, name), 99999), idx DESC,name
							LIMIT %(start)s, %(page_len)s
						""".format(**{'key': searchfield,'fcond': get_filters_cond(doctype, filters, conditions),
							'mcond': get_match_cond(doctype)}), {'txt': "%%%s%%" % txt,
							'_txt': txt.replace("%", ""),'start': start,'page_len': page_len})


@frappe.whitelist()
def get_models(reference_doc, reference_fields):
	reference_field = json.loads(reference_fields)
	list_name = frappe.db.get_all(reference_doc,fields=reference_field,filters={"is_active":1},
							   									limit_page_length=2000)
	return {"list_name":list_name}


@frappe.whitelist()
def get_all_products_with_attributes(category=None, brand=None, item_name=None, active=None, featured=None,):
	try:
		lists=[]
		subcat=get_products(category=category, brand=brand, item_name=item_name, active=active, 
					  														featured=featured)
		if subcat:
			for subsub in subcat:
				subsub.indent=0
				subsub.doctype="Product"
				lists.append(subsub)
				subsub.subsubcat=get_product_attributes(subsub.name)
				if subsub.subsubcat:
					for listcat in subsub.subsubcat:
						listcat.indent=1
						listcat.doctype="Product Attribute Option"
						lists.append(listcat)
		return lists
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.get_all_products_with_attributes") 
	

@frappe.whitelist()
def get_product_attributes(name):   
	try:
		query = '''SELECT AO.name AS docname,
						CONCAT_WS(' - ', PA.attribute, AO.parent_option) AS name,
						AO.option_value AS item, AO.parent_option,AO.price_adjustment AS price,AO.attribute 
					FROM 
						`tabProduct Attribute Option` AO 
					INNER JOIN 
						`tabProduct Attribute Mapping` PA 
					ON 
						AO.attribute_id = PA.name 
					WHERE 
						PA.parent = "{parent}" 
					ORDER BY 
						PA.display_order, name '''.format(parent=name)
		s= frappe.db.sql(query,as_dict=1)
		return s
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.get_product_attributes") 


@frappe.whitelist()
def get_products(category=None,brand=None,cat_doctype=None,brand_doctype=None,item_name=None,
				 												active=None,featured=None):
	if category or brand:
		filters = ''
		joins = ''
		if category:
			joins += ' inner join `tabProduct Category Mapping` PCM on PCM.parent=P.name'
			filters += " and PCM.category='{category}'".format(category=category)
		if brand:
			joins += ' inner join `tabProduct Brand Mapping` PBM on PBM.parent=P.name'
			filters += ' and PBM.brand="{brand}"'.format(brand=brand)
		if item_name:
			item_name = '"%' + item_name + '%"'
			filters += ' and P.item like %s' % (item_name)
		if active:
			if active=="Yes":
				active=1
			else:
				active=0
			filters += ' and P.is_active=%s' % (active)
		if featured:
			if featured=="Yes":
				featured=1
			else:
				featured=0
			filters += ' and P.display_home_page=%s' % (featured)
		query = '''SELECT P.name,P.item,P.price,P.sku,P.old_price,P.stock,
						P.inventory_method,P.name AS docname,
						CASE 
							WHEN P.is_active > 0 THEN 'Yes' 
							ELSE 'No' 
						END AS is_active,
						CASE 
							WHEN P.display_home_page > 0 THEN 'Yes' 
							ELSE 'No' 
						END AS display_home_page,
						P.name AS id,P.name AS name1 
					FROM `tabProduct` P {joins} 
					WHERE P.name != '' {condition}
				'''.format(condition=filters, joins=joins)
		p = frappe.db.sql(query,as_dict=1)
		for items in p:
			images = frappe.db.sql('''	SELECT detail_thumbnail,detail_image 
										FROM `tabProduct Image` 
										WHERE parent = %(name)s 
										ORDER BY is_primary DESC
									''', {'name': items.name}, as_dict=1)
			image = '<div class="row">'
			for img in images:
				if img.detail_thumbnail:
					image += '<div class="col-md-4 popup" data-poster="'+img.detail_image+'\
						" data-src='+img.detail_image+' style="margin-bottom:10px;padding-left:0px;\
							padding-right:0px;"><a href="'+img.detail_image+'"><img class=\
								"img-responsive" id="myImg" src="'+ img.detail_thumbnail +'"\
									onclick=showPopup("'+img.detail_image+'")></a></div>'
			image+='</div>'
			items.image = image
	else:
		filters = ''
		if item_name:
			item_name = '"%' + item_name + '%"'
			filters += ' and P.item like %s' % (item_name)
		if active:
			if active=="Yes":
				active=1
			else:
				active=0
			filters += ' and P.is_active=%s' % (active)
		if featured:
			if featured=="Yes":
				featured=1
			else:
				featured=0
			filters += ' and P.display_home_page=%s' % (featured)
		query = '''SELECT P.name,P.item,P.price,P.sku,P.old_price,P.stock,
						P.inventory_method,P.name AS docname,
						CASE 
							WHEN P.is_active > 0 THEN 'Yes' 
							ELSE 'No' 
						END AS is_active,
						CASE 
							WHEN P.display_home_page > 0 THEN 'Yes' 
							ELSE 'No' 
						END AS display_home_page,
						P.name AS id,P.name AS name1 
					FROM`tabProduct` P 
					WHEREP.name != '' {condition} '''.format(condition=filters)
		p = frappe.db.sql(query,as_dict=1)
		for items in p:
			images = frappe.db.sql('''SELECT detail_thumbnail,detail_image 
										FROM `tabProduct Image` 
										WHERE parent = %(name)s 
										ORDER BY is_primary DESC
									''', {'name': items.name}, as_dict=1)
			image = '<div class="row">'
			for img in images:
				if img.detail_thumbnail:
					image += '<div class="col-md-4 popup" data-poster="'+img.detail_image+'"\
						  data-src='+img.detail_image+' style="margin-bottom:10px;padding-left:0px;\
							padding-right:0px;"><a href="'+img.detail_image+'"><img class=\
								"img-responsive" id="myImg" src="'+ img.detail_thumbnail +'" \
									onclick=showPopup("'+img.detail_image+'")></a></div>'
			image+='</div>'
			items.image = image
	return p


@frappe.whitelist()
def update_bulk_data(doctype,docname,fieldname,value):
	try:
		if doctype=="Product Attribute Option":
			if fieldname== "price":
				fieldname = "price_adjustment"
			if fieldname== "item":
				fieldname = "option_value"
		if doctype=="Product":
			if fieldname== "is_active" or fieldname== "display_home_page":
				if value=="Yes":
					value=1
				elif value=="No":
					value=0
		frappe.db.set_value(doctype,docname,fieldname,value)
		doc = frappe.get_doc(doctype,docname)
		return doc
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.update_bulk_data") 


@frappe.whitelist()
def get_gallery_list(parent, name=None):
	condition = ""
	if parent:
		condition += 'where parent =%(parent)s'
	if name:
		condition += 'and name =%(name)s'
	else:
		name = ""
	return frappe.db.sql('''SELECT * 
							FROM 
								`tabProduct Image` 
							{condition} 
							ORDER BY 
								idx ASC
						''', {"parent": parent, "name" : name}, as_dict=1)


@frappe.whitelist()
def get_product_template(name=None):
	user = frappe.session.user
	if name:
		return frappe.get_doc("Product", name)
	return frappe.db.get_all("Product", fields=["*"], filters={"is_template":1})


@frappe.whitelist()
def get_product_templates(name=None):
	if name:
		return frappe.get_doc("Product", name)
	return frappe.db.get_all("Product", fields=["*"], filters={"is_template":1})


@frappe.whitelist()
def save_gallery_changes(data):
	doc = data
	if isinstance(doc, string_types):
		doc = json.loads(doc)
	ret = frappe.get_doc(doc.get('doc_type'),doc.get('doc_name'))
	ret.image_name= doc.get('img_name')
	ret.title= doc.get('img_caption')
	ret.save()
	return ret


@frappe.whitelist()
def upload_img():
	try:
		files = frappe.request.files
		content = None
		dt = frappe.form_dict.doctype
		dn = frappe.form_dict.docname
		if 'files[]' in files:
			file = files['files[]']
			content = file.stream.read()
			filename = file.filename
		if content:
			ret = frappe.get_doc({
					"doctype": "File",
					"attached_to_name": dn,
					"attached_to_doctype": dt,
					"file_name":frappe.form_dict.name,
					"is_private": 0,
					"content": content})
			ret.save(ignore_permissions=True)
			frappe.db.commit()
			return ret.as_dict()
	except Exception as e:
		frappe.log_error(frappe.get_traceback(),"Error in doctype.product.upload_img")


def get_query_condition(user):
	if not user: 
		user = frappe.session.user
	
			
@frappe.whitelist()
def get_record_count(dt):
	condition = ''
	d = frappe.db.sql('''SELECT (CASE 
								WHEN is_test_record = 0 THEN "actual" 
								ELSE "test" 
							END) AS record_type, 
							COUNT(*) count 
						FROM 
							`tab{dt}` {cond} 
						GROUP BY 
							is_test_record'''.format(dt=dt, cond=condition), as_dict=1)
	out = {}
	for item in d:
		out[item.record_type] = item.count
	return out


@frappe.whitelist()
def clear_test_records(dt):
	test_records = frappe.db.get_all(dt, filters={'is_test_record': 1}, limit_page_length=500, 
								  						order_by='creation desc')
	docs = len(test_records)
	for i, item in enumerate(test_records):
		frappe.delete_doc(dt, item.name)
		frappe.publish_progress(float(i) * 100 / docs, title='Deleting sample records', 
						  							description='Please wait...')
	return {'status': 'Success'}


@frappe.whitelist(allow_guest=True)
def product_detail_onscroll(productid, layout, domain=None):
	from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.V2.product \
		import get_product_other_info, get_customer_recently_viewed_products
	contexts = {}
	catalog_settings=get_settings('Catalog Settings')
	contexts['catalog_settings']= catalog_settings
	contexts['currency']= frappe.cache().hget('currency','symbol')
	active_theme = None
	if not active_theme:
		theme = frappe.db.get_all('Web Theme', filters={'is_active': 1})
		if theme:
			active_theme = theme[0].name
	if active_theme:
		theme_settings = frappe.get_doc('Web Theme', active_theme)
	if theme_settings.grid_product_box:
		contexts['product_box'] = frappe.db.get_value('Product Box', theme_settings.grid_product_box, 'route')
	elif catalog_settings.product_boxes:
		contexts['product_box'] = frappe.db.get_value('Product Box', catalog_settings.product_boxes, 'route')
	else:
		contexts['product_box'] = None
	categories_list = frappe.db.sql('''SELECT PCMcategory, PCMcategory_name, 
											(SELECT C.route 
												FROM 
													`tabProduct Category` C 
												WHERE 
													C.name = PCM.category) AS route 
										FROM 
											`tabProduct Category Mapping` PCM 
										WHERE 
											PCM.parent = %(parent)s 
										ORDER BY 
											PCM.idx 
										LIMIT 1 ''', {'parent': productid}, as_dict=1)
	for category in categories_list:
		check_product_box = frappe.db.get_value("Product Category",category.category,
										  				'product_box_for_list_view')
		if check_product_box:
			contexts['product_box']=frappe.db.get_value('Product Box',check_product_box,'route')
		else:
			from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.product \
																		import get_parent_categorie
			parent_categories = get_parent_categorie(category.category)
			for parent_category in parent_categories:
				check_product_box = frappe.db.get_value("Product Category",parent_category.name,\
																	'product_box_for_list_view')
				if check_product_box:
					contexts['product_box']=frappe.db.get_value('Product Box',check_product_box,'route')
	a_related_products = a_best_seller_category = a_products_purchased_together = []
	a_product_category = categories_list[0] if categories_list else {}
	if catalog_settings.customers_who_bought or catalog_settings.enable_best_sellers or \
														catalog_settings.enable_related_products:
		additional_info = get_product_other_info(productid, domain)
		a_related_products = additional_info['related_products']
		a_best_seller_category = additional_info['best_seller_category']
		a_products_purchased_together = additional_info['products_purchased_together']
	contexts['related_products'] = a_related_products
	contexts['bestseller_item'] = a_best_seller_category
	contexts['show_best_sellers'] = a_products_purchased_together
	contexts['product_category'] = a_product_category
	contexts['recent_viewed_products'] = get_customer_recently_viewed_products(domain=domain)
	if layout=="Meat Layout":
		product_enquiry = get_product_scroll(productid, 1, 5)
		contexts['product_enquiry'] = product_enquiry
		contexts['approved_reviews'] = get_product_reviews_list(productid, 0, 10)
		contexts['approved_total_reviews'] = frappe.db.get_value('Product',productid,'approved_total_reviews')
		if catalog_settings.upload_review_images:
			review_images = frappe.db.sql('''SELECT RI.review_thumbnail,RI.image,RI.list_image,
												RI.parent,RI.name,PR.product 
											FROM 
												`tabProduct Review` PR 
											INNER JOIN 
												`tabReview Image` RI 
											ON 
												PR.name = RI.parent 
											WHERE 
												PR.product = %(product)s ''', {'product': productid}, as_dict=1)
			contexts['review_img'] = review_images
		template = frappe.render_template(
						"/templates/pages/DetailPage/detailpage_otherinfo_meat.html", contexts)
	else:
		template = frappe.render_template(
						"/templates/pages/DetailPage/additional_product_info.html", contexts)
	return template


@frappe.whitelist()
def insert_product_attribute_and_options(doc):
	try:
		if isinstance(doc, string_types):
			doc = json.loads(doc)
		for item in doc:
			if item.get('product_attribute') and item.get('attribute'):
				if item.get('name'):
					attr = frappe.get_doc("Product Attribute Mapping", item.get('name'))
				else:
					attr = frappe.new_doc("Product Attribute Mapping")
					attr.parent = item.get('product')
					attr.parenttype = "Product"
					attr.parentfield = "product_attributes"
				attr.idx= item.get('idx')
				attr.attribute= frappe.db.get_value("Product Attribute",
										item.get('product_attribute'), "attribute_name")
				attr.attribute_unique_name= frappe.db.get_value("Product Attribute",
										item.get('product_attribute'), "unique_name")
				attr.control_type= item.get('control_type')
				attr.display_order= item.get('display_order')
				attr.is_required= item.get('is_required')
				attr.product_attribute= item.get('product_attribute')
				attr.quantity= item.get('quantity')
				if item.get('name'):
					attr.save()
					frappe.db.commit()
				else:
					attr.insert()
					frappe.db.commit()
				if item.get('attroptions'):
					for opt in item.get('attroptions'):
						if opt.get('name'):
							docs = frappe.get_doc("Product Attribute Option", opt.get('name'))
						else: 
							docs= frappe.new_doc("Product Attribute Option")
							docs.parent=attr.parent
							docs.parenttype='Product'
							docs.parentfield='attribute_options'
						docs.idx=opt.get('idx')
						docs.attribute=attr.product_attribute
						docs.attribute_id=attr.name
						docs.display_order=opt.get('display_order')
						docs.price_adjustment=opt.get('price_adjustment')
						docs.weight_adjustment=opt.get('weight_adjustment')
						docs.attribute_color=opt.get('attribute_color')
						docs.option_value=opt.get('option_value')
						docs.product_title=opt.get('product_title')
						docs.image=opt.get('image')
						docs.is_pre_selected=opt.get('is_pre_selected')
						docs.parent_option=opt.get('parent_option')
						docs.disable = int(opt.get('disable'))
						docs.ignore_permissions = True
						if int(opt.get('disable'))==1:
							docs.available_datetime = opt.get('available_datetime')
						if opt.get('name'):
							docs.save()
							frappe.db.commit()
						else:
							docs.insert()
							frappe.db.commit()
		return doc
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Error in doctype.product.insert_product_attribute_and_options") 


@frappe.whitelist()
def get_doc_images(dt, dn):
	if dt == "Product Category":        
		products = frappe.db.sql_list('''SELECT M.parent 
										FROM 
											`tabProduct Category Mapping` M 
										INNER JOIN 
											tabProduct P ON P.name = M.parent 
										WHERE M.category = %(name)s 
										GROUP BY P.name ''', {'name': dn})
	elif dt == "Product Brand":
		products = frappe.db.sql_list('''SELECT M.parent 
										FROM 
											`tabProduct Brand Mapping` M 
										INNER JOIN 
											tabProduct P ON P.name = M.parent 
										WHERE M.brand = %(name)s 
										GROUP BY P.name ''', {'name': dn})
	elif dt == "Product":
		products = [dn]
	if products and len(products) > 0:
		product_list = ",".join(['"' + i + '"' for i in products])
		return frappe.db.sql('''SELECT list_image, detail_thumbnail AS thumbnail, product_image 
								FROM 
									`tabProduct Image` 
								WHERE parent IN ({PRODUCT}) 
								ORDER BY idx'''.format(PRODUCT=product_list), as_dict=1)
	return []


@frappe.whitelist(allow_guest=True)
def get_attributes_combination(product):
	combination=frappe.db.get_all('Product Variant Combination',filters={'parent':product},fields=['*'])
	productdoc=frappe.db.get_all('Product',fields=['*'],filters={'name':product})
	return combination,productdoc


@frappe.whitelist(allow_guest=True)
def get_attributes_name(attribute_id,product):
	combination=frappe.db.get_all('Product Variant Combination',
							   filters={
								   'parent':product,
								   'attribute_id':attribute_id.replace(",","\n")if attribute_id else "",},
								   fields=['*'])  
	return combination


@frappe.whitelist()
def create_product(source_name, target_doc=None):
	doc = get_mapped_doc('Product', source_name, {
		'Product': {
			'doctype': 'Product'
		},
		'Product Image': {
			'doctype': 'Product Image',
		},
		'Product Video': {
			'doctype': 'Product Video',
		},
		'Product Category Mapping': {
			'doctype': 'Product Category Mapping',
		},
		'Product Brand Mapping': {
			'doctype': 'Product Brand Mapping',
		},
		'Product Attribute Mapping': {
			'doctype': 'Product Attribute Mapping',
		},
		'Product Variant Combination': {
			'doctype': 'Product Variant Combination',
		},
		'Product Specification Attribute Mapping': {
			'doctype': 'Product Specification Attribute Mapping',
		},
		'Product Search Keyword': {
			'doctype': 'Product Search Keyword',
		},
	}, target_doc)
	return doc


@frappe.whitelist()
def delete_current_img(childname, doctype):
	try:
		image_doc = 'Product Image'
		if childname:
			getimg = frappe.db.get_all(image_doc, fields=['*'],
					filters={'name': childname})
			if getimg:
				img = frappe.get_doc(image_doc, childname)
				if doctype == 'Product':
					from ecommerce_business_store_singlevendor.utils.utils import delete_file
					filename = img.product_image
					delete_file(img.list_image)
					delete_file(img.detail_thumbnail)
					delete_file(img.detail_image)
					delete_file(img.email_thumbnail)
					delete_file(img.mini_cart)
					delete_file(img.cart_thumbnail)
				img.delete()
				if getimg[0].is_primary == 1 and image_doc == 'Product Image':
					frappe.db.set_value(getimg[0].parenttype,
										getimg[0].parent, 'image', '')
				if filename:
					getimg1 = frappe.get_list('File', fields=['*'],
												filters={'file_url': filename})
					if getimg1:
						fle = frappe.get_doc('File', getimg1[0].name)
						fle.delete()
	except Exception:
		frappe.log_error(frappe.get_traceback(), 'delete_current_img')


@frappe.whitelist()
def check_exist_sku(doc):
	doc = json.loads(doc)
	if doc.get("sku"):
		check_other = frappe.db.get_all("Product",filters={"sku":doc.get("sku"),
										"name":("!=",doc.get("name")),"status":"Approved"})
		return check_other
	return []


def update_whoose_search(self):
	try:
		delete_whoose_data(self)
		if self.product_categories:
			cat_route = frappe.db.get_value("Product Category",self.product_categories[0].category,"route")
			from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.whoosh \
				import insert_update_search_data
			send__data = []
			dict__ = {}
			if self.is_active==1 and self.status=="Approved":
				p_prices = frappe.db.sql("""SELECT product
											FROM 
												`tabProduct Price` PP 
											INNER JOIN 
												`tabPrice List` PL ON PP.price_list = PL.name
											WHERE PP.product = %(product)s 
											GROUP BY product """, {"product": self.name}, as_dict=1)
				if p_prices:
					for x in p_prices:   
						dict__['name'] = self.name
						dict__['product_id'] = self.name
						dict__['title'] = self.item
						dict__['route'] = cat_route + "/" +self.route if cat_route else self.route
						dict__['type'] = "Product"
						dict__['search_keyword'] = self.item
						dict__['product_image'] = self.image
						send__data.append(dict__)
						dict__ = {}
						if self.search_keyword:
							for s__ in self.search_keyword:
								dict__['name'] = s__.name
								dict__['title'] = self.item
								dict__['product_id'] = self.name
								dict__['route'] = cat_route + "/" +self.route if cat_route else self.route
								dict__['type'] = "Product"
								dict__['product_image'] = self.image
								dict__['search_keyword'] = s__.search_keywords
								send__data.append(dict__)
								dict__ = {}
					insert_update_search_data(send__data)
	except Exception:
		frappe.log_error(title="Error in update product search data",message = frappe.get_traceback())

@frappe.whitelist()
def delete_combination(dt, dn):
	frappe.delete_doc(dt, dn)
	frappe.db.commit()

@frappe.whitelist()
def update_attr_options():
	p_list = frappe.db.sql("""SELECT P.name 
							FROM 
								`tabProduct Attribute Option` O 
							INNER JOIN 
								`tabProduct` P ON P.name = O.parent 
							WHERE O.attribute_id IS NULL OR O.attribute_id = '' 
							GROUP BY P.name """, as_dict=1)
	for p in p_list:
		p_doc = frappe.get_doc("Product",p.name)
		if p_doc.attribute_options:
			for x in p_doc.attribute_options:
				if not x.unique_name:
					frappe.db.set_value("Product Attribute Option",x.name,"unique_name",
						 p_doc.scrub(frappe.db.get_value("Product Attribute",
									   x.attribute,"attribute_name").lstrip())+"_"+p_doc.scrub(
										   x.option_value.lstrip()))
				if not x.attribute_id:
					p_attr_id = frappe.db.get_all("Product Attribute Mapping",
								   filters={"parent":p_doc.name,"product_attribute":x.attribute})
					if p_attr_id:
						x.attribute_id = p_attr_id[0].name
			p_doc.save(ignore_permissions=True)


@frappe.whitelist()
def update_product_variant_combinations():
	p_list = frappe.db.get_all("Product",filters={"has_variants":1})
	for p in p_list:
		p_doc = frappe.get_doc("Product",p.name)
		if not p_doc.variant_combination:
			product_attributes = []
			for attr in p_doc.product_attributes:
				product_attribute = {"product": p_doc.name,
									"attribute": frappe.db.get_value("Product Attribute",\
													attr.attribute,'attribute_name'),
									"control_type": "Radio Button List",
									"display_order": attr.idx,
									"is_required": "Yes",
									"product_attribute": attr.attribute,
									"name":attr.name }
				product_attribute["attroptions"] = []
				options = frappe.db.get_all("Product Attribute Option",fields=['*'],
								filters={'parent':p_doc.name,'attribute':attr.product_attribute,
				 				'attribute_id':attr.name},order_by='display_order',limit_page_length=50)  
				for p_attr_opt_doc in options:
					product_attribute["attroptions"].append(p_attr_opt_doc)
				if product_attribute["attroptions"]:
					product_attributes.append(product_attribute)
			combinations = generate_combinations(p_doc.name,product_attributes)
			if combinations:
				p_doc.variant_combination=[]
			frappe.log_error(title=p_doc.name,message=combinations)
			for c in combinations:
				p_doc.append("variant_combination",{
					"product_title": c.get("product_title"),
					"attributes_json": json.dumps(c.get("attributes_json")),
					"attribute_id": c.get("attribute_id"),
					"attribute_html": c.get("attribute_html"),
					"sku": c.get("sku"),
					"show_in_market_place": 1,
					"price": p_doc.price})
			if combinations:
				p_doc.save(ignore_permissions=True)
				frappe.db.commit()


def generate_combinations(product_id,attributes):
	options=[]
	all_options=[]
	response = attributes
	p_combinations = frappe.db.get_all("Product Variant Combination",
									filters={"parent":product_id},fields=['attribute_id'])
	for item in response:
		if item.get('attroptions'):
			li=[x.get('option_value') for x in item.get('attroptions')]
			options.append(li)
		all_options+=item.get('attroptions')
	import itertools
	combination=list(itertools.product(*options))
	lists=[]
	sku_no = 1
	sku_seq = frappe.db.get_all("Product Variant Combination",
							 filters={"parent":product_id},fields=['sku'],
							 order_by="sku desc",limit_page_length=1)
	if sku_seq:
		if sku_seq[0].sku:
			l_sku = sku_seq[0].sku
			sku_no = int(l_sku[-3:])+1
	for item in combination:
		html=''
		ids=''
		price=0
		variant_text = ""
		attributes_json = []
		for li in item:
			check=next((x for x in all_options if x.get('option_value')==li),None)
			if check and check.get('name'):
				attribute_name = frappe.db.get_value("Product Attribute", 
										 check.get('attribute'), "attribute_name")
				ids+=check.get('name')+'\n'
				html+='<div data-name="'+str(ids)+'" class="btn btn-default btn-xs btn-link-to-form" \
					style="border: 1px solid #d1d8dd;margin: 2px;min-width: 50px;text-align: left;">\
					<p style="text-align: left;margin: 0px;font-size: 11px;">'+attribute_name+'</p> \
						<span style="font-weight: 700;">'+li+'</span></div>'
				price+=check.get('price_adjustment')
				variant_text+= li+" / "
				attributes_json.append(check.get('name'))
		if ids:
			if not any(obj['attribute_id'] == ids for obj in p_combinations):
				v_sku = product_id.split("ITEM-")[1]+'%03d' % sku_no
				p_title = frappe.db.get_value("Product",product_id,"item")+" - "+variant_text[:-1]
				lists.append({'sku':v_sku,'product_title':p_title,
							'attribute_html':html,'attribute_id':ids, 'stock': 1,
							'price':price, 'attributes_json': attributes_json})
				sku_no = sku_no+1
	return lists


@frappe.whitelist()
def update_category_data_json(doc):
	from frappe.utils import get_files_path	
	path = get_files_path()
	if doc.product_categories:
		for x in doc.product_categories:
			cat_route = frappe.db.get_value("Product Category",x.category,"route")
			cat_route = cat_route.replace("/","-")
			if not os.path.exists(os.path.join(path,cat_route+"-"+x.category)):
				frappe.create_folder(os.path.join(path,cat_route+"-"+x.category))
			from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.category \
				import get_category_filters_json
			filters_resp = get_category_filters_json(category=x.category)
			if filters_resp.get("attribute_list"):
				with open(os.path.join(path,(cat_route+"-"+x.category), 'attributes.json'), "w") as f:
					content = json.dumps(filters_resp.get("attribute_list"), separators=(',', ':'))
					f.write(content)
			if filters_resp.get("brand_list"):
				with open(os.path.join(path,(cat_route+"-"+x.category), 'brands.json'), "w") as f:
					content = json.dumps(filters_resp.get("brand_list"), separators=(',', ':'))
					f.write(content)
			if filters_resp.get("category_list"):
				with open(os.path.join(path,(cat_route+"-"+x.category), 'categories.json'), "w") as f:
					content = json.dumps(filters_resp.get("category_list"), separators=(',', ':'))
					f.write(content)


@frappe.whitelist()
def update_attr_options_unique_names():
	p_list = frappe.db.get_all("Product",filters={"has_variants":1})
	for p in p_list:
		p_doc = frappe.get_doc("Product",p.name)
		if p_doc.attribute_options:
			for x in p_doc.attribute_options:
				frappe.db.set_value("Product Attribute Option",x.name,
						"unique_name",p_doc.scrub(frappe.db.get_value("Product Attribute",
						x.attribute,"attribute_name").lstrip())+"_"+p_doc.scrub(x.option_value.lstrip()))
			frappe.db.commit()


def delete_whoose_data(self):
	try:
		from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.whoosh \
			import remove_deleted_data
		send__data = []
		send__data.append(self.name)
		if self.search_keyword:
			for s__ in self.search_keyword:
				send__data.append(s__.name)
		remove_deleted_data(send__data)
	except Exception:
		frappe.log_error(title="Error in delete product search data",message = frappe.get_traceback())
