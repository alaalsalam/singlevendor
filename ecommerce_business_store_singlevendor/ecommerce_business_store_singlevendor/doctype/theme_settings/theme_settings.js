// Copyright (c) 2019, sivaranjani and contributors
// For license information, please see license.txt

frappe.ui.form.on('Theme Settings', {
    validate: function(frm) {
        if (frm.doc.page_css.length > 8000) {
            frappe.throw('Maximum Number of Character is 8000')
        }
    },
    page_css(frm){
        if (frm.doc.page_css.length > 8000) {
            frappe.throw('Maximum Number of Character is 8000')
        }
    }
});