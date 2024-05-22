// Copyright (c) 2019, Tridots Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Web Theme', {
	after_save: function(frm){
		cur_frm.reload_doc();
	},
	authorize_api_indexing_access: function(frm) {
		let reauthorize = 0;
		if (frm.doc.authorization_code) {
			reauthorize = 1;
		}
		frappe.call({
			method: "ecommerce_business_store_singlevendor.utils.google_indexing.authorize_access",
			args: {
				"g_indexing": frm.doc.name,
				"reauthorize": reauthorize
			},
			callback: function(r) {
				if (!r.exc) {
					frm.save();
					window.open(r.message.url);
				}
			}
		});
	},
	enable_view_tracking: function(frm) {
		frappe.boot.website_tracking_enabled = frm.doc.enable_view_tracking;
	}
});
