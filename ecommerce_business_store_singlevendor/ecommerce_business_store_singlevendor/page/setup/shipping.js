frappe.require("assets/ecommerce_business_store_singlevendor/css/toggle-slider.css");
class ShippingMethod {
	constructor(opts) {
		$.extend(this, opts);
		this.page.set_title('Shipping Method');
		this.shipping_methods = [];
		this.shipping_rate_methods = [];
		this.active_rate_method = null;
		this.is_edit = false;
		this.is_activated = true;
		this.make();
	}

	make() {
		let me = this;
		this.set_primary_action();
		this.$div = $(`<div class="container-fluid" id="shipping">
				<div class="row">
					<div class="col-md-8">
						<p style="margin-top: 15px;">${__("You can configure your own shipping methods and charges for each method.")}</p>
					</div>
					<div class="col-md-4">
						<div class="text-right" style="padding: 5px 0;">
							<button class="btn btn-primary rate-config">${__("Configure Rate Method")}</button>
						</div>
					</div>
				</div>
				<div class="row items-div"></div>
			</div>
			<style>
				#page-setup #shipping .items-div {
					padding: 15px;
				}
				#page-setup #shipping .items-div .outerDiv {
					border: 1px solid #ddd;
					padding: 20px;
					margin-bottom: 10px;
					min-height: 100px;
				}
				#page-setup #shipping .items-div .outerDiv .item-title {
					font-size: 15px;
					font-weight: 600;
				}
				#page-setup #shipping .items-div .outerDiv .item-title span {
					font-size: 13px;
					font-weight: normal;
				}
				#page-setup #shipping .items-div .outerDiv .item-desc {
					font-size: 13px;
					margin-top: 5px;
				}
			</style>`).appendTo(this.wrapper);
		this.$itemsDiv = this.$div.find('.items-div');
		this.check_progress();
		this.get_shipping_details();
		this.$div.find('.rate-config').click(function() {
			me.activate_shipping_rates();
		})
	}

	set_primary_action() {
		this.page.set_primary_action(__("Add"), ()=> {
			this.is_edit = false;
			this.ship_method = undefined;
			this.add_edit_method();
		}, 'fa fa-plus');
	}

	get_shipping_details() {
		let me = this;
		frappe.call({
			method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.setup.setup.get_shipping_details',
			args: {},
			callback: function(r) {
				me.shipping_methods = r.message.shipping_methods;
				me.shipping_rate_methods = r.message.shipping_rate_methods;
				let check = me.shipping_rate_methods.find(obj => obj.is_active == 1);
				if(check)
					me.active_rate_method = check;
				me.make_html()
			}
		})
	}

	make_html() {
		let me = this;
		this.$itemsDiv.empty();
		this.shipping_methods.map(f => {
			let businessDiv = '';
			if(has_common(frappe.user_roles, ['System Manager', 'Admin']) && f.business)
				businessDiv = ` <span>(${f.business_name} - ${f.business})</span>`;
			let row = $(`<div class="col-md-12 outerDiv">
					<div class="col-md-5">
						<div class="item-title">${f.shipping_method_name}${businessDiv}</div>
						<div class="item-desc">${(this.active_rate_method && this.active_rate_method.shipping_rate_method) || ''}</div>
					</div>
					<div class="col-md-3 text-center">
						<div class="btn-group">
							<button class="btn btn-default configure"><span class="fa fa-cog"></span> ${__("Configure Rates")}</button>
							<div class="btn-group" style="border-left: 1px solid #ddd;display: none;">
								<button class="btn btn-default dropdown-toggle" data-toggle="dropdown">
									<span class="caret"></span>
								</button>
								<ul class="dropdown-menu" role="menu">
									<li><a>Change</a></li>
								</ul>
							</div>
						</div>
					</div>
					<div class="col-md-4 text-right bttns"></div>
				</div>`);
			if(f.show_in_website) {
				row.find('.bttns').append(`<button class="btn btn-danger delete-item"><span class="fa fa-trash"></span></button>
					<button class="btn btn-primary"><span class="fa fa-edit"></span> Edit</button>
					<button class="btn btn-warning deactivate"><span class="fa fa-trash"></span> Deactivate</button>`);
			} else {
				row.find('.bttns').append(`<button class="btn btn-danger delete-item"><span class="fa fa-trash"></span></button>
					<button class="btn btn-success">Activate</button>`);
				row.find('.btn-group').addClass('hide');
			}
			row.find('.delete-item').click(function() {
				frappe.confirm(__("Do you really want to delete this shipping method?"), ()=> {
					frappe.call({
						method: 'frappe.client.delete',
						args: {
							doctype: 'Shipping Method',
							name: f.name
						},
						callback: function(r) {
							me.get_shipping_details();
						}
					})
				})
			});
			row.find('.btn-primary').click(function() {
				me.is_edit = true;
				me.ship_method = f;
				me.add_edit_method();
			});
			row.find('.configure').click(function() {
				if(me.active_rate_method) {
					let filters = {};
					if(f.business)
						filters = {'business': f.business};
					frappe.set_route('Form', 'Shipping Rate Method', me.active_rate_method.name);
				} else {
					me.activate_shipping_rates();
				}					
			});
			row.find('.btn-success').click(function() {
				if(f.business && !me.is_activated) {
					me.activate_shipping_rates(f);
				} else {
					me.enable_shipping(f);
				}
			});
			row.find('.deactivate').click(function() {
				me.disable_shipping(f);
			})
			row.find('.btn-group').find('.dropdown-menu').find('a').click(function() {
				me.activate_shipping_rates();
			})
			this.$itemsDiv.append(row);
		});
	}

	add_edit_method() {
		let is_vendor = false;
		if(frappe.session.user != 'Administrator' && has_common(frappe.user_roles, ['Vendor']))
			is_vendor = true;
		let me = this;
		let title = this.is_edit ? 'Edit Shipping Method' : 'Add Shipping Method';
		let dialog = new frappe.ui.Dialog({
			title: title,
			fields: [
				{
					'fieldname': 'shipping_method_name', 
					'fieldtype': 'Data', 'label': __('Shipping Method Name'), 'reqd': 1, 
					'default': this.is_edit ? this.ship_method.shipping_method_name : '',
					'description': __('Name of the shipping method')
				},
				{
					'fieldname': 'display_order', 'reqd': 1,
					'fieldtype': 'Int', 'label': __('Display Order'), 
					'default': this.is_edit ? this.ship_method.display_order : 1,
					'description': __('The sequence in which this method will be displayed')
				},
				{
					'fieldname': 'is_deliverable', 
					'fieldtype': 'Check', 'label': __('Is Deliverable?'), 
					'default': this.is_edit ? this.ship_method.is_deliverable : 0
				},
				{
					'fieldname': 'business', 'fieldtype': 'Link', 'options': 'Business',
					'label': __('Business'), 'hidden': is_vendor ? 1 : 0,
					'default': is_vendor ? frappe.boot.user.defaults.business : ''
				},
				{ 'fieldtype': 'Column Break', 'fieldname': 'cb1' },
				{
					'fieldname': 'description', 
					'fieldtype': 'Text Editor', 'label': __('Description'), 
					'default': this.is_edit ? this.ship_method.description : null
				}
			],
			primary_action_label: this.is_edit ? __('Update') : __('Save'),
			primary_action(values) {
				values.doctype = 'Shipping Method';
				let method = 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.mobileapi.insert_doc';
				if(me.is_edit){
					values.name = me.ship_method.name;
					method = 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.mobileapi.update_doc';
				}
				frappe.call({
					method: method,
					args: {'doc': JSON.stringify(values)},
					callback: function(r) {
						dialog.hide();
						me.get_shipping_details();
					}
				})
			}
		});
		dialog.show();
		if(this.is_edit){
			dialog.set_value({'business': this.ship_method.business, 'display_order': this.ship_method.display_order});
		}
		if($(window).width() > 920)
			dialog.$wrapper.find('.modal-dialog').css({'width': '900px', 'margin': '15px auto'});
	}

	check_progress() {
		let me = this;
		let business = frappe.boot.user.defaults.business;
		if(business) {
			let business_setup = frappe.boot.sysdefaults.business_defaults[business];
			if(business_setup) {
				let opts = JSON.parse(business_setup);
				if(opts.indexOf('Shipping') < 0) {
					me.is_activated = false;
				}
			}
		}
	}

	update_progress() {
		let me = this;
		let business = frappe.boot.user.defaults.business;
		if(business) {
			let business_setup = frappe.boot.sysdefaults.business_defaults[business];
			if(business_setup) {
				let opts = JSON.parse(business_setup);
				if(opts.indexOf('Shipping') < 0) {
					opts.push('Shipping');
					frappe.boot.sysdefaults.business_defaults[business] = JSON.stringify(opts);
					core.update_default(business, JSON.stringify(opts));
					me.is_activated = true;
					frappe.ui.toolbar.clear_cache();
				}
			}
		}
	}

	activate_shipping_rates(shipping_method) {
		let me = this;
		let options = ['', 'Shipping By Weight', 'Shipping By Total', 'Fixed Rate Shipping'];
		let rateDialog = new frappe.ui.Dialog({
			title: __('Shipping Rate Configuration Methods'),
			fields: [
				{'fieldname': 'rate_html', 'fieldtype': 'HTML'},
				{
					'fieldname': 'shipping_rate_method', 'fieldtype': 'Select', 
					'label': __('Shipping Rate Method'), 'hidden': 1, 
					'options': options
				}
			]
		});
		rateDialog.show();
		rateDialog.get_close_btn().addClass('hide');
		let wrapper = rateDialog.fields_dict.rate_html.$wrapper.empty();
		$(`<div class="container-fluid">
				<div class="row rates-div"></div>
				<div class="text-right">
					<button class="btn btn-primary">Confirm</button>
				</div>
			</div>
			<style>
				.modal-dialog div[data-fieldname="rate_html"] .iconsdiv {
					/*background: #fde1e1;*/
					/*border-radius: 50%;*/
					/*padding: 10px;*/
					text-align: center;
					font-size: 30px;
					/*height: 65px;*/
					/*width: 65px;*/
				}
				.modal-dialog div[data-fieldname="rate_html"] .mths {
					border: 1px solid #ccc;
					padding: 15px;
					margin-bottom: 15px;
				}
				.modal-dialog div[data-fieldname="rate_html"] .mths .title-txt {
					font-weight: 600;
					font-size: 15px;
				}
				.modal-dialog div[data-fieldname="rate_html"] .mths .desc {
					font-size: 13px;
					margin-top: 5px;
					color: #808080;
				}
				.modal-dialog div[data-fieldname="rate_html"] .mths input.popupCheckBox:checked + .slider {
					background-color: #5eb149;
				}
				.modal-dialog div[data-fieldname="rate_html"] .mths .slider {
					background-color: #ca8383;
				}
			</style>`).appendTo(wrapper);
		options.map(f => {
			if(f != '') {
				let obj = this.get_icons(f);
				let $icon = `<span class="${obj.icon}"></span>`;
				if(obj.image) {
					$icon = `<img src="${obj.image}" />`;
				}
				let row = $(`<div class="col-md-12 mths">
						<div class="col-md-2" style="padding: 0;">
							<div class="iconsdiv">${$icon}</div>
						</div>
						<div class="col-md-8">
							<div class="title-txt">${f}</div>
							<div class="desc">${obj.description}</div>
						</div>
						<div class="col-md-2 text-right">
							<label class="switch">
								<input type="checkbox" class="popupCheckBox" name="ship_method" value="${f}">
								<span class=" slider round"></span>
							</label>
						</div>
					</div>`);
				row.find('input[type="checkbox"]').change(function() {
					let check = this;
					if($(this).prop('checked')) {
						wrapper.find('input[type="checkbox"]').each(function() {
							if(this.value != check.value) {
								$(this).prop('checked', false);
							}
						});
						rateDialog.set_value('shipping_rate_method', check.value);
					} else {
						rateDialog.set_value('shipping_rate_method', '');
					}
				})
				wrapper.find('.rates-div').append(row);
			}
		});
		if(this.active_rate_method) {
			wrapper.find('input[type="checkbox"][value="' + this.active_rate_method.shipping_rate_method + '"]').prop('checked', true);
			rateDialog.set_value('shipping_rate_method', this.active_rate_method.shipping_rate_method);
		}
		wrapper.find('.btn-primary').click(function() {
			let values = rateDialog.get_values();
			if(values && values.shipping_rate_method) {
				let check = me.shipping_rate_methods.find(obj => obj.shipping_rate_method == values.shipping_rate_method);
				if(check) {
					check.doctype = 'Shipping Rate Method';
					check.is_active = 1
					let method = 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.mobileapi.update_doc';
					frappe.call({
						method: method,
						args: {'doc': JSON.stringify(check)},
						callback: function(r) {
							rateDialog.hide();
							if(shipping_method)
								me.enable_shipping(shipping_method);
							me.update_progress();
						}
					})
				}
			} else {
				frappe.throw(__('Please select any one method.'))
			}
		});
	}

	get_icons(method) {
		let obj = '';
		switch (method) {
			case "Shipping By Weight":
				obj = { 
					icon: 'fa fa-balance-scale',
					image: '/assets/ecommerce_business_store_singlevendor/images/weight.svg',
					description: "Charge fees to your customers based on product weight that is to be shipped."
				};
				break;
			case "Shipping By Total":
				obj = { 
					icon: 'fa fa-dollar',
					image: '/assets/ecommerce_business_store_singlevendor/images/total.svg',
					description: "Based on the customer order total (X value) and zone, the shipment fee is configured."
				};
				break;
			case "Fixed Rate Shipping":
				obj = { 
					icon: 'fa fa-money',
					image: '/assets/ecommerce_business_store_singlevendor/images/fixed-rate.svg',
					description: "Zone or location-based shipment fixed prices are charged for customers."
				};
				break;
			default:
				obj = { 
					icon: 'fa fa-money',
					description: "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s"
				};
				break;
		}
		return obj;
	}

	enable_shipping(shipping_method) {
		this.set_value('Shipping Method', shipping_method.name, 'show_in_website', 1);
	}

	disable_shipping(shipping_method) {
		this.set_value('Shipping Method', shipping_method.name, 'show_in_website', 0);
	}

	set_value(dt, dn, df, val) {
		let me = this;
		frappe.call({
			method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.mobileapi.update_value',
			args: {
				doctype: dt,
				name: dn,
				fieldname: df,
				value: val
			},
			callback: function(r) {
				me.get_shipping_details();
			}
		})
	}
}