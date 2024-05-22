class PaymentMethod {
	constructor(opts) {
		$.extend(this, opts);
		this.page.set_title('Payment Method');
		this.all_payments = [];
		this.active_payments = [];
		this.pay_options;
		this.business = null;
		this.is_edit = false;
		this.pay_method = undefined;
		if(has_common(frappe.user_roles, ['Vendor']) && frappe.session.user != 'Administrator') {
			this.business = frappe.boot.user.defaults.business;
		} else {
			this.page.add_field({
				'fieldtype': 'Link', 'fieldname': 'business', 'options': 'Business', 
				'label': __('Business'),
				onchange: ()=> {
					var val = this.page.fields_dict.business.value;
					if(val) {
						this.business = val;
						this.get_payment_details();
					}
				}
			})
		}	
		this.make();
	}

	make() {
		this.$div = $(`<div class="container-fluid" id="payment">
				<div class="row">
					<div class="col-md-12">
						<p>${__("You can activate/deactivate the payment methods that you prefer.")}</p>
					</div>
				</div>
				<div class="row items-div"></div>
			</div>
			<style>
				#page-setup #payment .items-div {
					padding: 15px;
				}
				#page-setup #payment .items-div .outerDiv {
					border: 1px solid #ddd;
				    padding: 20px;
				    margin-bottom: 10px;
				    min-height: 100px;
				}
				#page-setup #payment .items-div .outerDiv .item-title {
					font-size: 15px;
					font-weight: 600;
				}
				#page-setup #payment .items-div .outerDiv .item-title span {
					font-size: 13px;
					font-weight: normal;
				}
				#page-setup #payment .items-div .outerDiv .item-desc {
					font-size: 13px;
					margin-top: 5px;
					color: #696565;
				}
			</style>`).appendTo(this.wrapper);
		this.$itemsDiv = this.$div.find('.items-div');
		if(this.business)
			this.get_payment_details();
	}

	get_payment_details() {
		let me = this;
		frappe.call({
			method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.setup.setup.get_payment_details',
			args: {
				business: this.business
			},
			callback: function(r) {
				if(r.message) {
					me.all_payments = r.message.available_methods;
					me.active_payments = r.message.payment_methods;
					me.pay_options = r.message.pay_options;
					me.make_html();
				}
			}
		})
	}

	make_html() {
		let me = this;
		this.$itemsDiv.empty();
		this.all_payments.map(f => {
			let businessDiv = '';
			if(has_common(frappe.user_roles, ['System Manager', 'Admin']) && f.business)
				businessDiv = ` <span>(${f.business_name} - ${f.business})</span>`;
			let row = $(`<div class="col-md-12 outerDiv">
					<div class="col-md-2">
						<img src="${f.image}" class="img-responsive" style="height: 60px;" />
					</div>
					<div class="col-md-4">
						<div class="item-title">${f.gateway_type}${businessDiv}</div>
						<div class="item-desc">${f.description || ''}</div>
					</div>
					<div class="col-md-2 text-center">
						<button class="btn btn-default"><span class="fa fa-cog"></span> Configure</button>
					</div>
					<div class="col-md-4 text-right action-btn">
						
					</div>
				</div>`);
			let check_payment = this.active_payments.find(obj => obj.gateway_type == f.gateway_type);
			if(check_payment && !check_payment.disable) {
				$(`<button class="btn btn-danger">Deactivate</button>`).appendTo(row.find('.action-btn'));
			} else {
				$(`<button class="btn btn-success">Activate</button>`).appendTo(row.find('.action-btn'));
			}
			if(!check_payment)
				row.find('.btn-default').hide();
			row.find('.btn-danger').click(function() {
				frappe.confirm(__('Do you want to deactive this payment method?'), () => {
					frappe.call({
						method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.mobileapi.update_value',
						args: {
							doctype: 'Business Payment Gateway Settings',
							name: check_payment.name,
							fieldname: 'disable',
							value: 1
						},
						callback: function(r) {
							me.get_payment_details();
						}
					})
				})
			});
			row.find('.btn-success').click(function() {
				if(check_payment) {
					frappe.call({
						method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.mobileapi.update_value',
						args: {
							doctype: 'Business Payment Gateway Settings',
							name: check_payment.name,
							fieldname: 'disable',
							value: 0
						},
						callback: function(r) {
							me.get_payment_details();
						}
					})
				} else {
					me.is_edit = false;
					me.pay_method = undefined;
					if(f.gateway_type == 'Razorpay' && me.pay_options[f.dt].allow_partner_creation)
						me.show_partner_popup(f.gateway_type, me.pay_options[f.dt].send_email_to);
					else
						me.show_dialog(f.gateway_type);
				}					
			});
			row.find('.btn-default').click(function() {
				me.is_edit = true;
				me.pay_method = check_payment;
				me.show_dialog(f.gateway_type);
			})
			this.$itemsDiv.append(row);
		})
	}

	show_dialog(gateway_type) {
		let me = this;
		let title = __(gateway_type) + ' Settings';
		let dialog = new frappe.ui.Dialog({
			title: title,
			fields: this.get_fields(gateway_type),
			primary_action_label: this.is_edit ? __('Update') : __('Save'),
			primary_action(values) {
				values.doctype = 'Business Payment Gateway Settings';
				values.gateway_type = gateway_type;
				let method = 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.mobileapi.insert_doc';
				if(me.is_edit){
					values.name = me.pay_method.name;
					method = 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.mobileapi.update_doc';
				}
				frappe.call({
					method: method,
					args: {'doc': JSON.stringify(values)},
					callback: function(r) {
						dialog.hide();
						frappe.show_alert('Successfully updated!', 10);
						me.get_payment_details();
						me.update_progress();
					}
				})
			}
		})
		dialog.show();
	}

	show_partner_popup(gateway_type, send_email_to) {
		let me = this;
		let dialog = new frappe.ui.Dialog({
			title: '',
			fields: [{'fieldtype': 'HTML', 'fieldname': 'pay_html'}]
		});
		dialog.show();
		let wrapper = dialog.fields_dict.pay_html.$wrapper.empty();
		$(`<div>
			<div class="pay-opts" data-id="self">
				<div class="txt">${__("I have a Razorpay account or I can create on my own.")}</div>
			</div>
			<div class="pay-opts" data-id="merchant">
				<div class="txt">${__("I need assistance in creating a new Razorpay account")}</div>
			</div>
		</div>
		<style>
			div[data-fieldname="pay_html"] .pay-opts {
				border: 1px solid #ddd;
				margin: 15px 0;
				padding: 40px 0;
				cursor: pointer;
			}
			div[data-fieldname="pay_html"] .txt {
				text-align: center;
				font-size: 16px;
			}
			div[data-fieldname="pay_html"] .pay-opts:hover {
				box-shadow: 1px 1px 1px 1px #0000002e;
			}
		</style>`).appendTo(wrapper);
		wrapper.find('.txt').css({'text-align': 'center', 'font-size': '16px'});
		dialog.$wrapper.find('.modal-header').hide();
		wrapper.find('.pay-opts').click(function() {
			dialog.hide();
			if($(this).attr('data-id') == 'self') {
				me.show_dialog(gateway_type);
			} else {
				me.confirm_parter_registration(send_email_to);
			}
		})
	}

	confirm_parter_registration(send_email_to) {
		let me = this;
		let dialog = new frappe.ui.Dialog({
			title: __('Confirm registration of Razorpay submerchant'),
			fields: [
				{'fieldname': 'business_name', 'fieldtype': 'Data', 'label': __('Account Name'), 'read_only': 1},
				{'fieldname': 'email', 'fieldtype': 'Data', 'label': __('Email'), 'read_only': 1, 'default': frappe.session.user},
				{'fieldtype': 'Button', 'fieldname': 'edit_details', 'label': __('Edit Details')}
			],
			primary_action_label: __('Confirm'),
			primary_action(values) {
				if(values.business_name && values.email) {
					values.sender = send_email_to;
					values.website = window.location.origin;
					frappe.call({
						method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.setup.setup.send_razorpay_submerchant_email',
						args: values,
						callback: function(r) {
							if(r.message && r.message.status == 'success')
								frappe.msgprint(__('Soon, You will receive a mail to complete your razorpay account creation process.'))
							dialog.hide();
						}
					})
				}
			}
		})
		dialog.show();
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Business',
				docname: me.business,
				fieldname: 'restaurant_name',
				filters: {
					name: me.business
				}
			},
			callback: function(r) {
				dialog.set_value('business_name', r.message.restaurant_name);
			}
		})
		dialog.fields_dict.edit_details.onclick = function() {
			if(dialog.fields_dict.business_name.df.read_only == 1) {
				dialog.fields_dict.business_name.df.read_only = 0;
				dialog.fields_dict.email.df.read_only = 0;
				dialog.refresh();
			}
		}
	}

	get_fields(gateway_type) {
		let is_vendor = false;
		if(frappe.session.user != 'Administrator' && has_common(frappe.user_roles, ['Vendor']))
			is_vendor = true;
		let fields = [
			{
				'fieldname': 'display_name', 'fieldtype': 'Data', 'label': __('Display Name'), 
				'default': this.is_edit ? this.pay_method.display_name : gateway_type
			},
			{
				'fieldname': 'business', 'fieldtype': 'Link', 'options': 'Business', 'label': __('Business'),
				'default': this.business, 'reqd': 1, 'hidden': is_vendor ? 1 : 0
			},
		]
		if(gateway_type == 'Razorpay')
			$.merge(fields, this.get_razorpay_fields());
		if(gateway_type == 'Stripe')
			$.merge(fields, this.get_stripe_fields());
		if(gateway_type == 'Paypal')
			$.merge(fields, this.get_paypal_fields());
		return fields;
	}

	update_progress() {
		if(this.business) {
			let business_setup = frappe.boot.sysdefaults.business_defaults[this.business];
			if(business_setup) {
				let opts = JSON.parse(business_setup);
				if(opts.indexOf('Payment') < 0) {
					opts.push('Payment');
					frappe.boot.sysdefaults.business_defaults[this.business] = JSON.stringify(opts);
					core.update_default(this.business, JSON.stringify(opts));
					this.is_activated = true;
					frappe.ui.toolbar.clear_cache();
				}
			}
		}
	}

	get_razorpay_fields() {
		return [
			{
				'fieldname': 'api_key', 'label': __('API Key'), 'fieldtype': 'Data', 'reqd': 1,
				'default': this.is_edit ? this.pay_method.api_key : ''
			},
			{
				'fieldname': 'api_secret', 'label': __('API Secret'), 'fieldtype': 'Data', 'reqd': 1,
				'default': this.is_edit ? this.pay_method.api_secret : ''
			},
			{
				'fieldname': 'site_logo', 'label': __('Site Logo'), 'fieldtype': 'Attach Image',
				'default': this.is_edit ? this.pay_method.site_logo : ''
			}
		]
	}

	get_stripe_fields() {
		return [
			{
				'fieldname': 'publishable_key', 'label': __('Publishable Key'), 'fieldtype': 'Data', 'reqd': 1,
				'default': this.is_edit ? this.pay_method.publishable_key : ''
			},
			{
				'fieldname': 'secret_key', 'label': __('Secret Key'), 'fieldtype': 'Data', 'reqd': 1,
				'default': this.is_edit ? this.pay_method.secret_key : ''
			}
		]
	}

	get_paypal_fields() {
		return [
			{
				'fieldname': 'api_username', 'label': __('API Signature'), 'fieldtype': 'Data', 'reqd': 1,
				'default': this.is_edit ? this.pay_method.api_username : ''
			},
			{
				'fieldname': 'api_password', 'label': __('API Passoword'), 'fieldtype': 'Data', 'reqd': 1,
				'default': this.is_edit ? this.pay_method.api_password : ''
			},
			{
				'fieldname': 'signature', 'label': __('Signature'), 'fieldtype': 'Data', 'reqd': 1,
				'default': this.is_edit ? this.pay_method.signature : ''
			}
		]
	}
}