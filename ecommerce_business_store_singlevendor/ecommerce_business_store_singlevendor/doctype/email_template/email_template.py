# Copyright (c) 2024, Tridotstech Private Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EmailTemplate(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		response: DF.TextEditor | None
		response_html: DF.Code | None
		subject: DF.Data
		use_html: DF.Check
	# end: auto-generated types
	pass
