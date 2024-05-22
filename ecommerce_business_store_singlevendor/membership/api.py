#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from datetime import datetime
from frappe.utils import add_to_date, getdate, date_diff
from ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api import get_today_date

@frappe.whitelist(allow_guest=True)
def get_year_filters():
	today = datetime.now()
	membership = frappe.db.get_all('Membership Payment', fields=['creation'], order_by='creation asc')
	year_list = []
	if membership:
		start_year = membership[0].creation.year
		while start_year <= today.year:
			year_list.append(str(start_year))
			start_year = start_year + 1
	else:
		year_list = [str(today.year)]
	return year_list

@frappe.whitelist()
def create_memberships():
	def _create_membership(member, membership_type, from_date, to_date, pay_month=None, pay_year=None):
		frappe.get_doc({
			'doctype': 'Membership Payment',
			'member': member,
			'membership_type': membership_type,
			'from_date': from_date,
			'to_date': to_date,
			'pay_month': pay_month,
			'pay_year': pay_year,
			'amount': frappe.db.get_value('Membership Type', membership_type, 'amount'),
			'posting_date': getdate(get_today_date(replace=True)),
			'membership_status': 'Current'
			}).insert(ignore_permissions=True)
	try:
		membership_settings = frappe.db.sql('''select * from `tabMembership Settings` where enable_auto_membership = 1''', as_dict=1)
		is_saas = False
		today = get_today_date(replace=True)
		for setting in membership_settings:
			condition = ''
			if is_saas and setting.business:
				condition = ' where business = "{0}"'.format(setting.business)
			members_list = frappe.db.sql('''select name, membership_type from `tabMember` {0}'''.format(condition), as_dict=1)
			for item in members_list:
				membership = frappe.db.sql('''select name, from_date, to_date from `tabMembership Payment` where member = %(member)s order by from_date desc''', {'member': item.name}, as_dict=1)
				if membership:
					if setting.payment_type == 'Month Range':
						from_date = add_to_date(getdate(membership[0].from_date), months=1)
						to_date = add_to_date(getdate(membership[0].to_date), months=1)
						month = getdate(from_date).strftime('%B')
						year = getdate(from_date).strftime('%Y')
						if setting.create_membership_on == 'Days After':
							check_date = add_to_date(getdate(from_date), days=int(setting.days_before_or_after))
							if check_date > from_date and check_date == getdate(today):
								_create_membership(item.name, item.membership_type, from_date, to_date, month, year)
						elif setting.create_membership_on == 'Days Before':
							check_date = add_to_date(getdate(from_date), days=-int(setting.days_before_or_after))
							if check_date < from_date and check_date == getdate(today):
								_create_membership(item.name, item.membership_type, from_date, to_date, month, year)
					else:
						validity = frappe.db.get_value('Membership Type', item.membership_type, 'validity')
						from_date = add_to_date(getdate(membership[0].to_date), days=1)
						to_date = add_to_date(getdate(from_date), days=int(validity))
						if setting.create_membership_on == 'Days After':
							check_date = add_to_date(getdate(from_date), days=int(setting.days_before_or_after))
							if check_date > from_date and check_date == getdate(today):
								_create_membership(item.name, item.membership_type, from_date, to_date)
						elif setting.create_membership_on == 'Days Before':
							check_date = add_to_date(getdate(from_date), days=-int(setting.days_before_or_after))
							if check_date < from_date and check_date == getdate(today):
								_create_membership(item.name, item.membership_type, from_date, to_date)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), 'ecommerce_business_store_singlevendor.membership.api.create_memberships')

@frappe.whitelist()
def get_membership_due_report(from_date, to_date, membership_type=None):
	condition = ''
	if membership_type:
		condition += ' and m.membership_type = "%s"' % membership_type
	data = frappe.db.sql('''select m.name as member, m.member_name, m.membership_type, ifnull(sum(mp1.amount), 0) as paid_amount from 
		`tabMember` m left join `tabMembership Payment` mp1 on mp1.member = m.name and mp1.paid = 1 
		and mp1.from_date >= %(from_date)s and mp1.to_date <= %(to_date)s where m.active = 1 {} 
		group by m.name'''.format(condition), {'from_date': from_date, 'to_date': to_date}, as_dict=1)
	for item in data:
		due_amount = frappe.db.sql('''select sum(amount) from `tabMembership Payment` where member = %(member)s and 
			from_date >= %(from_date)s and to_date <= %(to_date)s and paid = 0''', 
			{'member': item.member, 'from_date': from_date, 'to_date': to_date})
		amt = 0
		if due_amount and due_amount[0] and due_amount[0][0]:
			amt = due_amount[0][0]
		item.update({'due_amount': amt})
	return data