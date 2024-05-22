frappe.provide("frappe.setupDoc");

frappe.pages['setup'].refresh = function() {
	let route = frappe.get_route();
	if(route.length == 1)
		frappe.set_route('setup', 'shipping');
	frappe.setupDoc.doc_type = route[1];
	frappe.setupDoc.refresh();
}
{% include 'ecommerce_business_store_singlevendor/ecommerce_business_store_singlevendor/page/setup/payment.js' %}
{% include 'ecommerce_business_store_singlevendor/ecommerce_business_store_singlevendor/page/setup/shipping.js' %}
class SetupDoc {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.make();
		this.doc_type = '';
	}

	make() {
		this.page = frappe.ui.make_app_page({
			parent: this.wrapper,
			title: 'Setup',
			single_column: true
		});
		this.page.set_secondary_action(__("Refresh"), () => {
			this.refresh();
		});
		this.content_html = $(`<div class="mainbar"></div>`).appendTo(this.page.main);
		$(`<style>
				#page-setup .layout-main-section {
					border: 0;
				}
			</style>`).appendTo(this.page.main);
	}

	refresh() {
		this.content_html.empty();
		this.page.clear_primary_action();
		this.page.clear_fields();
		this.page.main.find('.page-form').addClass('hide');
		if(this.doc_type == 'shipping') {
			new ShippingMethod({wrapper: this.content_html, page: this.page});
		} else if(this.doc_type == 'payment') {
			new PaymentMethod({wrapper: this.content_html, page: this.page});
		}
	}
}

frappe.pages['setup'].on_page_load = function(wrapper) {
	frappe.setupDoc = new SetupDoc(wrapper);
}