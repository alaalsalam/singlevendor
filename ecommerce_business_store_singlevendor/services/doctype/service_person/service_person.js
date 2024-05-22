// Copyright (c) 2020, Tridots Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Person', {
	refresh: function(frm) {
		frm.set_query('service', 'service_mapping', function(doc, cdt, cdn){
			return {
				'filters': {
					'business': frm.doc.business
				}
			}
		})
	}
});
