# -*- coding: utf-8 -*-
# Copyright (c) 2020, Tridots Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe
from frappe.model.document import Document

class BusinessArea(Document):
	def autoname(self):
		self.name=self.area_name+' - '+self.location
