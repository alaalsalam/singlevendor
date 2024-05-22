// Copyright (c) 2020, Tridots Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Member', {
    setup: function(frm) {
        if(frm.get_field('member_type')) {
            frm.toggle_display(['member_type', 'house_flat_unit', 'block'], false);
        }
    },
	refresh: function(frm) {
		frm.set_query("newsletter", function(doc) {
            return {
                'query': 'ecommerce_business_store_singlevendor.membership.doctype.member.member.get_newsletter_based_email'               
            }
        });
        frm.set_query("temple", function(doc) {
            return {
                'query': 'ecommerce_business_store_singlevendor.membership.doctype.member.member.get_temple_based_email'               
            }
        });
        frappe.call({
            method: 'ecommerce_business_store_singlevendor.utils.setup.get_settings_from_domain',
            args: {
                dt: 'Membership Settings',
                business: frm.doc.business
            },
            callback: function(r) {
                if(r.message) {
                    frm.membership_settings = r.message;
                    frm.set_df_property('membership_expiry_date', 'hidden', 1 ? (r.message.enable_expiry != 1) : 0);
                    if(r.message.membership_vertical == 'Appartment / Housing') {
                        frm.trigger('housing_vertial');                        
                    } else if(r.message.membership_vertical == 'Family') {
                        frm.trigger('family_vertical')
                    }
                }
            }
        });        
	},
    membership_type: function(frm) {
        if(frm.doc.membership_type) {
            frappe.call({
                method: 'frappe.client.get_list',
                args: {
                    'doctype': 'Membership Type',
                    'filters': {'name': frm.doc.membership_type},
                    'fields': ['has_associated_member']
                },
                callback: function (r) {
                    if(r.message && r.message.length > 0)
                        frm.set_value('has_associated_member', r.message[0].has_associated_member)
                }
            })
        }            
    },
    housing_vertial: function(frm) {
        frm.toggle_display(['member_type', 'house_flat_unit', 'block'], true);
        frm.set_df_property('membership_type', 'label', __("House Type"));
        frm.set_df_property('membership_type', 'reqd', false);
        frm.set_df_property('membership_type', 'read_only', true);
        frappe.meta.get_docfield('Associated Member', 'occupancy', cur_frm.doc.name).hidden = 0;
        if(frm.doc.has_associated_member == 1 && frm.doc.member_type != 'Rented Out') {
            frm.toggle_display(['associated_member'], false);
        } else {
            frm.toggle_display(['associated_member'], true);
        }
    },
    family_vertical: function(frm) {

    },
    member_type: function(frm) {
        if(frm.doc.has_associated_member == 1 && frm.doc.member_type != 'Rented Out') {
            frm.toggle_display(['associated_member'], false);
        } else {
            frm.toggle_display(['associated_member'], true);
        }
    }
});

frappe.ui.form.on('Associated Member', {
    associated_member_add: function(frm, cdt, cdn) {
        let item = locals[cdt][cdn];
        if(frm.membership_settings && frm.membership_settings.default_relation) {
            frappe.model.set_value(cdt, cdn, 'relation', frm.membership_settings.default_relation);
        }
    }
})
