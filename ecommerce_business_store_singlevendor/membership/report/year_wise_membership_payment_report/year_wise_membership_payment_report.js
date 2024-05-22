// Copyright (c) 2016, Tridots Tech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Year-wise Membership Payment Report"] = {
	"filters": [
		{
			"fieldname": "business",
			"label": __("Business"),
			"fieldtype": "Link",
			"options": "Business",
			"reqd": 1,
			"default": (frappe.boot.user.defaults.business || ''),
		},
		{
			"fieldname": "year",
			"fieldtype": "Select",
			"label": __("Year"),
			"options": "2020\n2021",
			"reqd": 1
		},
		{
			"fieldname": "membership_type",
			"label": __("Membership Type"),
			"options": "Membership Payment",
			"fieldtype": "Link"
		}
	],
	"onload": function() {
		frappe.call({
			method: 'ecommerce_business_store_singlevendor.membership.report.year_wise_membership_payment_report.year_wise_membership_payment_report.get_year_list',
			args: {},
			callback: function(r) {
				if(r.message && r.message.length > 0) {
					let year_filter = frappe.query_report.get_filter('year');
					year_filter.df.options = r.message;
					year_filter.refresh();
				}
			}
		})
	}
};
