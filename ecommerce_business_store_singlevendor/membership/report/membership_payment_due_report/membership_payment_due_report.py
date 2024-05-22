# Copyright (c) 2013, Tridots Tech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
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
		},
		{
			"fieldname": "paid_amount",
			"label": _("Paid Amount"),
			"fieldtype": "Currency"
		},
		{
			"fieldname": "due_amount",
			"label": _("Due Amount"),
			"fieldtype": "Currency"
		}
	]

def get_data(filters):
	condition = ''
	if filters.get('membership_type'):
		condition += ' and m.membership_type = "%s"' % filters.get('membership_type')
	data = frappe.db.sql('''select m.name as member, m.member_name, m.membership_type, ifnull(sum(mp1.amount), 0) as paid_amount from 
		`tabMember` m left join `tabMembership Payment` mp1 on mp1.member = m.name and mp1.paid = 1 
		and mp1.from_date >= %(from_date)s and mp1.to_date <= %(to_date)s where m.active = 1 {} 
		group by m.name'''.format(condition), {'from_date': filters.get('from_date'), 'to_date': filters.get('to_date')}, as_dict=1)
	for item in data:
		due_amount = frappe.db.sql('''select sum(amount) from `tabMembership Payment` where member = %(member)s and from_date >= %(from_date)s and to_date <= %(to_date)s and paid = 0''', {'member': item.member, 'from_date': filters.get('from_date'), 'to_date': filters.get('to_date')})
		amt = 0
		if due_amount and due_amount[0] and due_amount[0][0]:
			amt = due_amount[0][0]
		item.update({'due_amount': amt})
	return data