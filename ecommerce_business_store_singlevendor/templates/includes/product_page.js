// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ready(function() {
	window.item = $('[itemscope] [itemprop="productID"]').text().trim();
	var qty = 0;

	frappe.call({
		type: "POST",
		method: "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.product.product.get_product_info_for_website",
		args: {
			item: get_item()
		},
		callback: function(r) {
			if(r.message) {
				
				if(r.message.product_info.price) {
					$(".item-price")
						.html(r.message.product_info.price.formatted_price_sales_uom + "<div style='font-size: small'>\
							(" + r.message.product_info.price.formatted_price + " / " + r.message.product_info.uom + ")</div>");

					if(r.message.product_info.in_stock==0) {
						$(".item-stock").html("<div style='color: red'> <i class='fa fa-close'></i> {{ _("Not in stock") }}</div>");
					}
					else if(r.message.product_info.in_stock==1) {
						var qty_display = "{{ _("In stock") }}";
						if (r.message.product_info.show_stock_qty) {
							qty_display += " ("+r.message.product_info.stock_qty+")";
						}
						$(".item-stock").html("<div style='color: green'>\
							<i class='fa fa-check'></i> "+qty_display+"</div>");
					}

					if(r.message.product_info.qty) {
						qty = r.message.product_info.qty;
						toggle_update_cart(r.message.product_info.qty);
					} else {
						toggle_update_cart(0);
					}
				}
			}
		}
	})
})