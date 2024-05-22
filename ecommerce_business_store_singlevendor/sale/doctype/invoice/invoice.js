// Copyright (c) 2019, sivaranjani and contributors
// For license information, please see license.txt

frappe.ui.form.on('Invoice', {
    setup: function(frm){
        frm.set_query("party_type", function() {
			return{
				"filters": {
					"name": ["in", ["Business","Drivers"]]
				}
			}
		});
    },

	refresh: function(frm) {
			if(frm.doc.docstatus==1){
		if (flt(frm.doc.paid_amount)!=flt(frm.doc.grand_total)){
			frm.add_custom_button("Make Payment", function() {
			frm.trigger("make_payment");
				});
				}
		}
	},

	make_payment: function() {
		frappe.model.open_mapped_doc({
			method: "ecommerce_business_store_singlevendor.sale.doctype.invoice.invoice.make_payment",
			frm: cur_frm
		})
	},
	tax_template: function(frm){
		if(frm.doc.tax_template){
			frappe.call({
				method: "ecommerce_business_store_singlevendor.sales.doctype.invoice.invoice.get_taxrate",
				args: {
					item_tax_template:frm.doc.tax_template
				},
				callback: function(r) {
					frm.doc.taxes=[];
					refresh_field("taxes");    
					if (r.message) {
						console.log(r)                 
						$.each(r.message, function(i, s) {
							var taxvalue = frm.doc.net_total
							var taxamount = (taxvalue*(s.rate/100))
							var totalamount = taxamount + taxvalue; 
							var total_amount = 0;
							if(frm.doc.taxes){
								for(var i=0;i<frm.doc.taxes.length;i++) {
									total_amount += frm.doc.taxes[i].amount;
								} 
							}
							var total_tax_rate=total_amount+taxamount
							var final=total_tax_rate+frm.doc.net_total
							var row = frappe.model.add_child(frm.doc, "Sales Taxes and Charges", "taxes");
							row.type ="On Net Total"; 
							row.rate = s.rate; 
							row.amount = taxamount;  
							row.total = final;  
							row.menu_item = "";                
							refresh_field("taxes");                         
						}); 
					}
					if(frm.doc.taxes){
						var tax=0;
						for(var i=0;i<frm.doc.taxes.length;i++) {
							tax += frm.doc.taxes[i].amount;
						} 
						frm.set_value("taxes_and_charges_added", tax);  
						frm.set_value("grand_total", tax+frm.doc.net_total);  
						frm.set_value("total_taxes_and_charges", tax);  
					}
				}
			})
		}
	},
});
frappe.ui.form.on('Sales Invoice Item', {
	quantity: function(frm,cdt,cdn) {
		var d = frappe.get_doc(cdt, cdn);
		if(d.quantity && d.rate){
			var amt=d.quantity*d.rate;
			frappe.model.set_value(cdt, cdn, "amount", amt);
		}
		frappe.model.set_value(cdt, cdn, "stock_qty", d.quantity);
	},

	warehouse: function(frm) {
		if(frm.doc.warehouse){
			frm.events.copy_value_in_all_rows(frm.doc, frm.doc.doctype, frm.doc.name, "items", "warehouse");
		}
	},

	copy_value_in_all_rows: function(doc, dt, dn, table_fieldname, fieldname) {
		var d = locals[dt][dn];
		console.log(table_fieldname)
		if(d[fieldname]){
			var cl = doc[table_fieldname] || [];
			for(var i = 0; i < cl.length; i++) {
				if(!cl[i][fieldname]) cl[i][fieldname] = d[fieldname];
			}
		}
		refresh_field(table_fieldname);
	},

	rate: function(frm,cdt,cdn) {
 		var d = frappe.get_doc(cdt, cdn);
		if(d.quantity && d.rate){
			console.log(d.quantity)
			console.log(d.rate)
			var amt=d.quantity*d.rate;
			console.log(amt)
			frappe.model.set_value(cdt, cdn, "amount", amt);
		}
		var total_amount = 0;
		for(var i=0;i<frm.doc.items.length;i++) {
			total_amount += frm.doc.items[i].amount;
		}
		frm.set_value("grand_total", total_amount);
		frm.set_value("base_grand_total", total_amount);
	}
});