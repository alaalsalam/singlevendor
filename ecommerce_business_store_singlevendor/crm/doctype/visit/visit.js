// Copyright (c) 2023, Tridots Tech and contributors
// For license information, please see license.txt
	
frappe.ui.form.on('Visit', {

	"refresh":function(frm){
		if (frm.doc.cus_type != "New Prospect"){
			frm.set_query('purpose_of_visits', function(doc, cdt, cdn) {
				return {
					filters: {
						'type': frm.doc.cus_type
					}
				}
			})
		}
	},

	cus_type:function(frm){
		if (frm.doc.cus_type != "New Prospect"){
			frm.set_query('purpose_of_visits', function(doc, cdt, cdn) {
				return {
					filters: {
						'type': frm.doc.cus_type
					}
				}
			})
		}
		frm.set_value("purpose_of_visits", []);
		frm.set_value("purpose_of_visit_list", "");
	},

	lead_id:function(frm){
		frappe.db.get_value("Customer Registration",frm.doc.lead_id,'store_name').then(r=>{
			 cur_frm.set_value("store_name", r.message.store_name);
		});
	},

	customer_id:function(frm){
		frappe.db.get_value("Customers",frm.doc.customer_id,'store_name').then(r=>{
			 cur_frm.set_value("store_name", r.message.store_name);
		});
	},

	purpose_of_visits:function(frm){
		 if(frm.doc.purpose_of_visits){
			  frappe.call({
				method: "ecommerce_business_store_singlevendor.crm.doctype.visit.visit.purpose_of_visits",
				type: "GET",
				args: {"purpose_of_visits": JSON.stringify(frm.doc.purpose_of_visits)},
				callback: function (r) {
					var data = r.message;
					if(data.length>0){
						var visist_txt = "";
						for(var k=0;k<data.length;k++){
							visist_txt += data[k].vis_of_purps+","
						}
						visist_txt = visist_txt.substring(0,visist_txt.length-1);
						frm.set_value("purpose_of_visit_list", visist_txt);
					}
					else{
						frm.set_value("purpose_of_visit_list", "");
					}
				}
			});
		}
	}
	
});