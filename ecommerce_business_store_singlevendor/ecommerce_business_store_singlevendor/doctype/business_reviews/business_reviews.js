// Copyright (c) 2019, sivaranjani and contributors
// For license information, please see license.txt

frappe.ui.form.on('Business Reviews', {
	refresh: function(frm) {
		if(frm.doc.review_for){
			frm.set_df_property('business','label',frm.doc.review_for)
			frm.set_df_property('business_name','label',frm.doc.review_for+" Name")
		}
		if(has_common(frappe.user_roles, ['Vendor']) && frm.doc.is_approved != 1){
			frm.add_custom_button(__('Approve'), function() {
                frm.set_value('is_approved', 1);
                frappe.call({
                	method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.business_reviews.business_reviews.approve_review',
                	args:{
                		name: frm.doc.name
                	},
                	freeze: true,
                	freeze_message: 'Saving',
                	callback: function(r){
                		if(r.message.status == 'Success'){
                			cur_frm.reload_doc();
                		}
                	}
                })
            });
		}
	},
	review_for: function(frm) {
		if(frm.doc.review_for){
			frm.set_df_property('business','label',frm.doc.review_for)
			frm.set_df_property('business_name','label',frm.doc.review_for + " Name")
		}
	}
});
