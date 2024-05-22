# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe, json
from frappe import _
from google_play_scraper import app

@frappe.whitelist()
def get_app_details():
	try:
		app_id = "com.meatstoday"
		result = app(
		    app_id,
		    lang='en', # defaults to 'en'
		    country='us' # defaults to 'us'
		)
		return result 
	except Exception as e:
		frappe.log_error(str(e), "get_app_details")
	