# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

month_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"fieldname": "member",
			"fieldtype": "Link",
			"options": "Member",
			"label": _("Member")
		},
		{
			"fieldname": "member_name",
			"label": _("Member Name"),
			"width": 150
		},
		{
			"fieldname": "membership_type",
			"label": _("Membership Type")
		}
	]
	for item in month_list:
		columns.append({
			"fieldname": item.lower(),
			"label": _(item),
			"width": 100
			})
	return columns

def get_data(filters):
	conditions = get_conditions(filters)
	data = []
	results = frappe.db.sql('''select m.name as member, m.member_name, m.membership_type from `tabMember` m where active = 1 {}'''.format(conditions), as_dict=1)
	for item in results:
		_val = [item.member, item.member_name, item.membership_type]
		payments = frappe.db.sql('''select paid, docstatus, monthname(from_date) as month from 
			`tabMembership Payment` where docstatus <> 2 and year(from_date) = %(year)s and 
			member = %(member)s order by from_date asc''', {'year': filters.get('year'), 'member': item.member}, as_dict=1)
		for mt in month_list:
			check_record = next((x for x in payments if x.month == mt), None)
			if check_record:
				if check_record.docstatus == 1:
					_val.append('<span class="indicator green"></span>Paid')
				elif check_record.docstatus == 0 and check_record.paid == 1:
					_val.append('<span class="indicator orange"></span>Pending Approval')
				else:
					_val.append('')
			else:
				_val.append('')
		data.append(_val)
	return data

def get_conditions(filters):
	condition = ''
	if filters.get('business'):
		condition += ' and m.business = "{}"'.format(filters.get('business'))
	if filters.get('membership_type'):
		condition += ' and m.membership_type = "{}"'.format(filters.get('membership_type'))
	return condition

@frappe.whitelist()
def get_year_list():
	year_list = frappe.db.sql_list('''select distinct year(from_date) from `tabMembership Payment`''')
	return year_list