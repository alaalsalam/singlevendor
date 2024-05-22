# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate
from datetime import timedelta


class SiteLoadingPopup(Document):
	def validate(self):
		if self.end_date < self.start_date:
			frappe.throw("Start Date should be greater than end date")
		if self.one_time == 1:
			today = getdate(nowdate())
			expire_date = today + timedelta(days = int(self.expire_days))
			self.expire_date = expire_date