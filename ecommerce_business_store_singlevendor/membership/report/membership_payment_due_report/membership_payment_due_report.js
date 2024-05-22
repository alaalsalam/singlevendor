// Copyright (c) 2016, Tridots Tech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Membership Payment Due Report"] = {
	"filters": [
		{
			"fieldname": "business",
			"label": __("Business"),
			"fieldtype": "Link",
			"options": "Business",
			"reqd": 1,
			"default": (frappe.boot.user.defaults.business || '')
		},
		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": __("From Date"),
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": __("To Date"),
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "membership_type",
			"label": __("Membership Type"),
			"options": "Membership Payment",
			"fieldtype": "Link"
		}
	],
	"onload": function() {
		if(frappe.boot.sysdefaults.active_fiscal_year) {
			let fiscal_year = frappe.boot.sysdefaults.active_fiscal_year
			frappe.query_report.set_filter_value('from_date', fiscal_year.year_start_date);
			frappe.query_report.set_filter_value('business', fiscal_year.year_end_date);
		}
	}
};
