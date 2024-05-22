# -*- coding: utf-8 -*-
# Copyright (c) 2018, info@valiantsystems.com and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class BusinessReviews(Document):
	def validate(self):
		if (self.review_for and self.business):
			selected_field = frappe.db.get_all('Party Name List',fields=['party_name_field'],
											filters={'parent':'Party Settings','party_type':self.review_for})
			if selected_field:
				res = frappe.db.get_value(self.review_for,self.business,selected_field[0].party_name_field)
				self.business_name = res
			else:
				self.business_name = ""
		if self.score_value:
			total_rating = 0
			for item in self.score_value:
				if item.rating:
					total_rating = total_rating + float(item.rating)
			self.overall_rating=(total_rating/len(self.score_value))


@frappe.whitelist()
def approve_review(name):
	frappe.db.set_value('Business Reviews', name, 'is_approved', 1)
	return {
		'status': 'Success'
  	}
