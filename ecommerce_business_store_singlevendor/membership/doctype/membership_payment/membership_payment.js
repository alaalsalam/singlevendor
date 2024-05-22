// Copyright (c) 2020, Tridots Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Membership Payment', {
	refresh: function(frm) {
		frappe.call({
            method: 'ecommerce_business_store_singlevendor.utils.setup.get_settings_from_domain',
            args: {
                dt: 'Membership Settings',
                business: frm.doc.business
            },
            callback: function(r) {
                if(r.message) {
                	if(r.message.payment_type == 'Date Range') {
                		frm.toggle_display(['pay_month', 'pay_year'], false);
                		frm.toggle_display(['from_date', 'to_date'], true);
                		frm.toggle_reqd(['pay_month', 'pay_year'], false);
                	} else {
                		frm.toggle_display(['pay_month', 'pay_year'], true);
                		frm.toggle_display(['from_date', 'to_date'], false);
                		frm.toggle_reqd(['pay_month', 'pay_year'], true);
                		frm.trigger('set_year_month_filters');
                	}
                }
            }
        });
        if(frm.doc.docstatus == 1 && frm.doc.paid == 0) {
        	frm.add_custom_button(__("Make Payment"), () => {
    			frappe.model.open_mapped_doc({
		            method: "ecommerce_business_store_singlevendor.membership.doctype.membership_payment.membership_payment.get_payment_args",
		            frm: cur_frm,
		            as_dict: 1
		        })
        	})
        }
	},
	set_year_month_filters: function(frm) {
		frappe.call({
    		method: 'ecommerce_business_store_singlevendor.membership.api.get_year_filters',
    		args: {},
    		callback: function(r) {
    			frm.set_df_property('pay_year', 'options', r.message);
    			let date = new Date();
    			let current_year = date.getFullYear();
    			if(frm.doc.__islocal)
    				frm.set_value('pay_year', current_year);
    			frm.trigger('set_month_filter');
    		}
    	})
	},
	set_month_filter(frm) {
    	frm.months_list = ["January", "February", "March", "April", "May",
            "June", "July", "August", "September", "October", "November", "December"
        ];
        frm.set_df_property('pay_month', 'options', frm.months_list);
        if(frm.doc.__islocal){
        	let d = new Date();
        	let month = d.getMonth();
        	frm.set_value('pay_month', frm.months_list[month]);
        }
    },
    pay_year: function(frm) {
    	frm.trigger('pay_month');
    },
    pay_month: function(frm) {
        if (frm.doc.pay_month) {
            frappe.provide('frappe.datetime');
            frappe.defaultDateFormat = "YYYY-MM-DD";
            let start = new Date(parseInt(frm.doc.pay_year), frm.months_list.indexOf(frm.doc.pay_month), 1);
            let end = new Date(parseInt(frm.doc.pay_year), frm.months_list.indexOf(frm.doc.pay_month) + 1, 0);
            frm.set_value('from_date', frappe.datetime.obj_to_str(start));
            frm.set_value('to_date', frappe.datetime.obj_to_str(end));
        }
    }
});
