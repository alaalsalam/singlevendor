frappe.pages['settings'].on_page_load = function(wrapper) {
	frappe.settingsEdit = new SettingsEdit(wrapper);
	frappe.require('/assets/ecommerce_business_store_singlevendor/plugins/FlexiColorPicker/colorpicker.js');
}

frappe.pages['settings'].refresh = function(wrapper) {
	let routes = frappe.get_route();
	let setting = '';
	if(routes.length == 1)
		frappe.set_route('settings', 'Web Theme');
	else
		setting = routes[1];
	frappe.settingsEdit.field.settings = setting;
	frappe.settingsEdit.refresh();
}
var SettingsEdit = Class.extend({
	init: function(parent) {
		this.parent = parent;
		this.field = {};
		this.fields_list = [];
		this.doclist = [];
		this.values_dict = {};
		this.active_settings = [];
		this.setting_val = {};
		this.default_color_type = 'HEX';
		this.make();
		this.setup_menu();
	},
	make: function() {
		this.page = frappe.ui.make_app_page({
			parent: this.parent,
			title: 'Settings',
			single_column: true
		});
		this.setup_filters();
		this.content_html = $(`<div style="min-height: 400px;">
				<div class="mainbar">
					<div class="row">
						<div class="col-md-2 tab__list">
							<div>
								<ul class="nav nav-tabs nav-stacked"></ul>
							</div>
						</div>
						<div class="col-md-10 tab__content">
							<div class="tab-content"></div>
						</div>
					</div>
				</div>
			</div>
			<style>
				#page-settings .layout-main-section {
					margin-bottom: 100px;
				}
				#page-settings .layout-main-section .no-rec {
					font-size: 14px;
					padding: 15%;
					text-align: center;
				}
				#page-settings .layout-main-section .nav-tabs {
					border-bottom: 0;
					padding-inline-start: 15px;
				}
				#page-settings .layout-main-section .nav-tabs li a{
					border: 0;
					margin-right: 0;
					border-radius: 0;
				}
				#page-settings .layout-main-section .nav-tabs li.active a {
					color: #2b10a5;
				}
				#page-settings .layout-main-section .tab__list,
				#page-settings .layout-main-section .tab__content {
					padding: 0;
				}
				#page-settings .layout-main-section .tab-content {
					padding: 10px 15px;
					border-left: 1px solid #ddd;
					padding-right: 30px;
				}
				#picker { width: 180px; height: 150px; float: left; }
				#slider { width: 30px; height: 150px; float: left; }
				#page-settings .layout-main-section .frappe-control {
					position: relative;
				}
				#page-settings .layout-main-section .section {
					border-bottom: 1px solid #ddd;
					margin-bottom: 10px;
				}
				#page-settings .layout-main-section .section:last-child {
					border-bottom: 0;
				}
				#page-settings .layout-main-section .section label {
					padding: 5px 0;
				}
				#page-settings .layout-main-section .color-picker-option {
					position: absolute;
					z-index: 1;
					background: #fff;
					display: none;
					border: 3px solid #222;
					padding: 3px;
				}
				#page-settings .layout-main-section .color-picker-option .color-options .color__opts {
					float: left;
					padding: 3px 12px;
					margin-right: 5px;
					background: #ddd;
					margin-top: 5px;
					font-size: 11px;
					cursor: pointer;
				}
				#page-settings .layout-main-section .color-picker-option .color-options .color__opts.active {
					background: #15a515;
					color: #fff;
				}
				#picker-indicator {
					width: 6px;
					height: 6px;
					position: absolute;
					border: 1px solid white;
					border-radius: 50%;
				}
				#slider-indicator {
					width: 100%;
					height: 6px;
					position: absolute;
					border: 2px solid black;
				}
				#slider-wrapper, #picker-wrapper {
					float: left;
					position: relative;
				}
			</style>`).appendTo(this.page.main);
		this.page.wrapper.on('click', function() {
			$('#page-settings').find('.color-picker-option').each(function() {
				$(this).hide();
			});
		});
	},
	setup_filters: function() {
		let me = this;
	},
	setup_menu: function() {
	},
	refresh: function() {
		let me = this;
		if(this.field && this.field.settings) {
			this.page.set_title(this.field.settings);
			this.content_html.find('.no-rec').hide();
		} else {
			this.content_html.find('.mainbar').append(`<div class="no-rec">Select any settings</div>`);
		}
		let allow = false;
		if(has_common(frappe.user_roles, ['Vendor']))
			this.field.business = frappe.boot.sysdefaults.business;
			allow = true;
		if(allow) {
			this.set_form();
		}
	},
	set_form: function() {
		frappe.run_serially([
			() => this.doclist = this.get_doctype_values(),
			() => {
				let check = this.doclist.find(obj => obj.doctype == this.field.settings);
				if(check && check.data){
					this.setting_val = check.data;
					this.set_fields();
				}
			}
		]);
	},
	get_doctype_values: function() {
		let me = this;
		let doclist = [];
		frappe.call({
			method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.settings.settings.get_settings_list',
			args: {
				business: this.field.business
			},
			async: false,
			freeze: true,
			freeze_message: __('Please wait...'),
			callback: function(r) {
				doclist = r.message;
			}
		});
		return doclist;
	},
	set_fields: function() {
		let me = this;
		this.active_settings = [];
		if(this.field.settings == 'Web Theme')
			this.active_settings = theme_variables;
		if(this.active_settings.length > 0)
			this.content_html.find('.no-rec').hide();
		$(me.content_html).find('.nav-tabs').html('');
		$(me.content_html).find('.tab-content').html('');
		$(this.active_settings).each((key, val) => {
			let cls = '', _cls = '';
			if(key == 0) {
				cls = 'class="active"';
				_cls = 'in active';
			}
			$(me.content_html).find('.nav-tabs').append(`<li ${cls}><a href="#${val.name}" data-toggle="tab"><i class="${val.icon}"></i> ${val.title}</a></li>`);
			let html = $(`<div id="${val.name}" class="tab-pane fade ${_cls}">
							<div class="fields__dict"></div>
						</div>`);
			$(me.content_html).find('.tab-content').append(html);
			let section_breaks = val.fields.filter(obj => obj.fieldtype == 'Section Break');
			$(section_breaks).each((s, sec) => {
				sec.idx = val.fields.findIndex(x => x.fieldname == sec.fieldname);
			});
			let active_section;
			let active_section_idx;
			let active_column;
			$(val.fields).each((k,v) => {
				if(k == 0 || v.fieldtype == 'Section Break') {
					active_section = $(`<div class="row section"></div>`);
					active_section_idx = k;
					if(v.fieldtype == 'Section Break' && v.label) {
						active_section.append(`<div class="col-md-12"><label>${__(v.label)}</label></div>`);
					}
					me.content_html.find('#' + val.name).find('.fields__dict').append(active_section);
					active_column = null;
				}
				let cls = 'col-md-12'
				if(section_breaks.length > 0) {
					let next_section = section_breaks.find(obj => obj.idx > active_section_idx);
					let end_idx = val.fields.length - 1;
					if(next_section) {
						end_idx = next_section.idx;
					}
					let cols = val.fields.slice((active_section_idx + 1), end_idx);
					let col_count = cols.filter(obj => obj.fieldtype == 'Column Break');
					cls = me.get_class(col_count.length.toString());
				} else {
					let col_count = val.fields.filter(obj => obj.fieldtype == 'Column Break');
					cls = me.get_class(col_count.length.toString());
				}
				if(has_common([v.fieldtype], ['Column Break', 'Section Break']) || !active_column) {
					active_column = $(`<div class="${cls}" data-ref="${v.fieldname}"></div>`).appendTo(active_section);
				}
				if(!has_common([v.fieldtype], ['Column Break', 'Section Break'])) {
					let input = frappe.ui.form.make_control({
						df: v,
						parent: active_column,
						only_input: false
					});
					input.make_input();
					if(v.description && v.description != '') {
						input.$wrapper.find('.control-label').html(`${__(v.label)} <span class="fa fa-question-circle form-tool" data-toggle="tooltip" data-original-title="${__(v.description)}" data-placement="right"></span>`)
						input.$wrapper.find('.label-area').html(`${__(v.label)} <span class="fa fa-question-circle form-tool" data-toggle="tooltip" data-original-title="${__(v.description)}" data-placement="right"></span>`)
					} else{
						input.$wrapper.find('.control-label').text(__(v.label));
						input.$wrapper.find('.label-area').text(__(v.label));
					}
					if(v.fieldtype == 'Check') {
						input.$wrapper.find('.disp-area').addClass('hide');
					}
					if(me.setting_val[v.fieldname])
						input.set_value(me.setting_val[v.fieldname]);
					input.$input.on('change', function() {
						let val = input.$input.val();
						me.setting_val[v.fieldname] = val;
					});
					let colorPicker;
					if(v.options == 'color') {
						input.$wrapper.append(`<div class="color-picker-option">
							<div id="picker-wrapper">
								<div id="picker"></div>
								<div id="picker-indicator"></div>
							</div>
							<div id="slider-wrapper">
								<div id="slider"></div>
								<div id="slider-indicator"></div>
							</div>
							<div class="color-options">
								<div class="color__opts ${(me.default_color_type == 'RGB') ? 'active': ''}">RGB</div>
								<div class="color__opts ${(me.default_color_type == 'HEX') ? 'active': ''}">HEX</div>
								<div class="color__opts ${(me.default_color_type == 'HSV') ? 'active': ''}">HSV</div>
							</div>
						</div>`);
						input.$wrapper.find('input').on('click', function(event) {
							event.stopPropagation();
							$('#page-settings').find('.color-picker-option').each(function() {
								$(this).hide();
							})
							if(!colorPicker) {
								ColorPicker.fixIndicators(
									input.$wrapper[0].querySelector('#slider-indicator'),
									input.$wrapper[0].querySelector('#picker-indicator')
								);
								colorPicker = ColorPicker(
									input.$wrapper[0].querySelector('#slider'), 
									input.$wrapper[0].querySelector('#picker'), 
									(hex, hsv, rgb, pickerCoordinate, sliderCoordinate) => {
										let val = '';
										if(me.default_color_type == 'RGB')
											val = `rgb(${rgb.r},${rgb.g},${rgb.b})`;
										else if(me.default_color_type == 'HSV')
											val = `hsv(${hsv.h},${hsv.s},${hsv.v})`;
										else if(me.default_color_type == 'HEX')
											val = hex;
										input.set_value(val);
										me.setting_val[v.fieldname] = val;
										ColorPicker.positionIndicators(
											input.$wrapper[0].querySelector('#slider-indicator'),
											input.$wrapper[0].querySelector('#picker-indicator'),
											sliderCoordinate, pickerCoordinate
										);
									}
								);
								setTimeout(() => {
									if(me.setting_val[v.fieldname]) {
										let clValue = me.setting_val[v.fieldname];
										if(clValue.indexOf('rgb') > -1) {
											let v_sub = clValue.split('(')[1].split(')')[0].split(',');
											colorPicker.setRgb({r: parseInt(v_sub[0]), g: parseInt(v_sub[1]), b: parseInt(v_sub[2])})
										} else if(clValue.indexOf('hsv') > -1) {
											let v_sub = clValue.split('(')[1].split(')')[0].split(',');
											colorPicker.setHsv({h: parseInt(v_sub[0]), s: parseInt(v_sub[1]), v: parseInt(v_sub[2])})
										} else if(clValue.indexOf('#') > -1) {
											colorPicker.setHex(clValue);
										}
									}
								}, 200);
							}
							input.$wrapper.find('.color-picker-option').show();
						});
						input.$wrapper.find('.color__opts').on('click', function () {
							let txt = $(this).text();
							me.default_color_type = txt;
							input.$wrapper.find('.color__opts.active').removeClass('active');
							$(this).addClass('active');
						});
						input.$wrapper.find('.color-picker-option').on('click', function(event) {
							event.stopPropagation();
						})
					}
				}	
			})
		});
		this.set_primary_button();
	},
	set_primary_button: function() {
		let me = this;
		this.page.set_primary_action(__('Update'), () => {
			frappe.call({
				method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.mobileapi.update_doc',
				args: {
					doc: JSON.stringify(me.setting_val)
				},
				freeze: true,
				freeze_message: __('Saving'),
				callback: function(r) {
					if(r.message && r.message.name){
						frappe.msgprint(__(`${me.field.settings} updated successfully!`));	
						me.setting_val = r.message;
					}
				}
			})
		})
	},
	get_class: function(len) {
		let cls = '';
		switch (len) {
			case '1':
				cls = 'col-md-6';
				break;
			case '2':
				cls = 'col-md-4';
				break;
			case '3':
				cls = 'col-md-3';
				break;
			case '4':
				cls = 'col-md-2';
				break;
			case '5':
				cls = 'col-md-2';
				break;
			default:
				cls = 'col-md-12';
				break;
		}
		return cls;
	}
});
let theme_variables = [
	{
		'name': 'general',
		'title': 'General',
		'icon': 'fa fa-sliders',
		'fields': [
			{'fieldname': 'body_bg_color', 'fieldtype': 'Data', 'label': 'Body Background Color', 'options': 'color'},
			{'fieldname': 'body_bg_image', 'fieldtype': 'Attach Image', 'label': 'Body Background Image', 'description':'Background image for whole website'},
			{'fieldname': 'body_text_color', 'fieldtype': 'Data', 'label': 'Body Text Color', 'options': 'color'},
			{'fieldname': 'cb1', 'fieldtype': 'Column Break'},
			{'fieldname': 'body_link_color', 'fieldtype': 'Data', 'label': 'Body Link Color', 'options': 'color'},
			{'fieldname': 'body_link_hover_color', 'fieldtype': 'Data', 'label': 'Body Link Hover Color', 'options': 'color'},
			{'fieldname': 'cb2', 'fieldtype': 'Column Break'},
			{'fieldname': 'body_theme_color', 'fieldtype': 'Data', 'label': 'Theme Color (For mobile device)', 'options': 'color'},
			{'fieldname': 'font_family', 'fieldtype': 'Data', 'label': 'Font Family'},
		]
	},
	{
		'name': 'header',
		'title': 'Header',
		'icon': 'fa fa-cube',
		'fields': [
			{'fieldname': 'sb1', 'label': 'Top Bar', 'fieldtype': 'Section Break'},
			{'fieldname': 'enable_top_bar', 'fieldtype': 'Check', 'label': 'Enable Top Bar?'},
			{'fieldname': 'sb1_cb1', 'fieldtype': 'Column Break'},
			{'fieldname': 'background_color', 'fieldtype': 'Data', 'label': 'Top Bar Background Color', 'options': 'color'},
			{'fieldname': 'sb1_cb2', 'fieldtype': 'Column Break'},
			{'fieldname': 'text_color', 'fieldtype': 'Data', 'label': 'Top Bar Text Color', 'options': 'color'},
			{'fieldname': 'sb1_cb3', 'fieldtype': 'Column Break'},
			{'fieldname': 'link_hover_color', 'fieldtype': 'Data', 'label': 'Top Bar Link Hover Color', 'options': 'color'},
			{'fieldname': 'sb2', 'label': 'Header', 'fieldtype': 'Section Break'},
			{'fieldname': 'header_bg_color', 'fieldtype': 'Data', 'label': 'Header Background Color', 'options': 'color'},
			{'fieldname': 'sb2_cb1', 'fieldtype': 'Column Break'},
			{'fieldname': 'header_text_color', 'fieldtype': 'Data', 'label': 'Header Text Color', 'options': 'color'},
			{'fieldname': 'header_hover_color', 'fieldtype': 'Data', 'label': 'Header Text Hover Color', 'options': 'color'},
			{'fieldname': 'sb2_cb2', 'fieldtype': 'Column Break'},
			{'fieldname': 'header_badge_color', 'fieldtype': 'Data', 'label': 'Header Badge Text Color', 'options': 'color'},
			{'fieldname': 'header_badge_bg_color', 'fieldtype': 'Data', 'label': 'Header Badge Background Color', 'options': 'color'},
			{'fieldname': 'sb3', 'label': 'Menu Bar', 'fieldtype': 'Section Break'},
			{'fieldname': 'menu_background', 'fieldtype': 'Data', 'label': 'Menu Background Color', 'options': 'color'},
			{'fieldname': 'menu_hover_background_color', 'fieldtype': 'Data', 'label': 'Menu Hover Background Color', 'options': 'color'},
			{'fieldname': 'sb3_cb1', 'fieldtype': 'Column Break'},
			{'fieldname': 'menu_text_color', 'fieldtype': 'Data', 'label': 'Menu Text Color', 'options': 'color'},
			{'fieldname': 'menu_hover_color', 'fieldtype': 'Data', 'label': 'Menu Text hover Color', 'options': 'color'},
			{'fieldname': 'sb3_cb2', 'fieldtype': 'Column Break'},
			{'fieldname': 'submenu_background_color', 'fieldtype': 'Data', 'label': 'Submenu Background Color', 'options': 'color'},
			{'fieldname': 'submenu_hover_background_color', 'fieldtype': 'Data', 'label': 'Submenu Hover Background Color', 'options': 'color'},
			{'fieldname': 'sb3_cb3', 'fieldtype': 'Column Break'},
			{'fieldname': 'submenu_text_color', 'fieldtype': 'Data', 'label': 'Submenu Text Color', 'options': 'color'},
			{'fieldname': 'submenu_hover_color', 'fieldtype': 'Data', 'label': 'Submenu Text Hover Color', 'options': 'color'},
		]
	},
	{
		'name': 'buttons',
		'title': 'Buttons',
		'icon': 'fa fa-bars',
		'fields': [
			{'fieldname': 'sb4', 'fieldtype': 'Section Break', 'label': 'Primary Button'},
			{'fieldname': 'primary_button_background_color', 'fieldtype': 'Data', 'label': 'Primary Button Background Color', 'options': 'color'},
			{'fieldname': 'sb4_cb1', 'fieldtype': 'Column Break'},
			{'fieldname': 'primary_button_hover_background_color', 'fieldtype': 'Data', 'label': 'Primary Button Hover Background Color', 'options': 'color'},
			{'fieldname': 'sb4_cb2', 'fieldtype': 'Column Break'},
			{'fieldname': 'primary_button_text_color', 'fieldtype': 'Data', 'label': 'Primary Button Text Color', 'options': 'color'},
			{'fieldname': 'sb4_cb3', 'fieldtype': 'Column Break'},
			{'fieldname': 'primary_button_hover_text_color', 'fieldtype': 'Data', 'label': 'Primary Button Hover Text Color', 'options': 'color'},
			{'fieldname': 'sb5', 'fieldtype': 'Section Break', 'label': 'Secondary Button'},
			{'fieldname': 'secondary_button_background_color', 'fieldtype': 'Data', 'label': 'Secondary Button Background Color', 'options': 'color'},
			{'fieldname': 'sb5_cb1', 'fieldtype': 'Column Break'},
			{'fieldname': 'secondary_button_hover_background_color', 'fieldtype': 'Data', 'label': 'Secondary Button Hover Background Color', 'options': 'color'},
			{'fieldname': 'sb5_cb2', 'fieldtype': 'Column Break'},
			{'fieldname': 'secondary_button_text_color', 'fieldtype': 'Data', 'label': 'Secondary Button Text Color', 'options': 'color'},
			{'fieldname': 'sb5_cb3', 'fieldtype': 'Column Break'},
			{'fieldname': 'secondary_button_hover_text_color', 'fieldtype': 'Data', 'label': 'Secondary Button Hover Text Color', 'options': 'color'},
			{'fieldname': 'sb6', 'fieldtype': 'Section Break', 'label': 'Warning Button'},
			{'fieldname': 'warning_button_background_color', 'fieldtype': 'Data', 'label': 'Warning Button Background Color', 'options': 'color'},
			{'fieldname': 'sb6_cb1', 'fieldtype': 'Column Break'},
			{'fieldname': 'warning_button_hover_background_color', 'fieldtype': 'Data', 'label': 'Warning Button Hover Background Color', 'options': 'color'},
			{'fieldname': 'sb6_cb2', 'fieldtype': 'Column Break'},
			{'fieldname': 'warning_button_text_color', 'fieldtype': 'Data', 'label': 'Warning Button Text Color', 'options': 'color'},
			{'fieldname': 'sb6_cb3', 'fieldtype': 'Column Break'},
			{'fieldname': 'warning_button_hover_text_color', 'fieldtype': 'Data', 'label': 'Warning Button Hover Text Color', 'options': 'color'},
			{'fieldname': 'sb7', 'fieldtype': 'Section Break', 'label': 'Danger Button'},
			{'fieldname': 'danger_button_background_color', 'fieldtype': 'Data', 'label': 'Danger Button Background Color', 'options': 'color'},
			{'fieldname': 'sb7_cb1', 'fieldtype': 'Column Break'},
			{'fieldname': 'danger_button_hover_background_color', 'fieldtype': 'Data', 'label': 'Danger Button Hover Background Color', 'options': 'color'},
			{'fieldname': 'sb7_cb2', 'fieldtype': 'Column Break'},
			{'fieldname': 'danger_button_text_color', 'fieldtype': 'Data', 'label': 'Danger Button Text Color', 'options': 'color'},
			{'fieldname': 'sb7_cb3', 'fieldtype': 'Column Break'},
			{'fieldname': 'danger_button_hover_text_color', 'fieldtype': 'Data', 'label': 'Danger Button Hover Text Color', 'options': 'color'},
			{'fieldname': 'sb8', 'fieldtype': 'Section Break', 'label': 'Default Button'},
			{'fieldname': 'default_button_background_color', 'fieldtype': 'Data', 'label': 'Default Button Background Color', 'options': 'color'},
			{'fieldname': 'sb8_cb1', 'fieldtype': 'Column Break'},
			{'fieldname': 'default_button_hover_background_color', 'fieldtype': 'Data', 'label': 'Default Button Hover Background Color', 'options': 'color'},
			{'fieldname': 'sb8_cb1', 'fieldtype': 'Column Break'},
			{'fieldname': 'default_button_text_color', 'fieldtype': 'Data', 'label': 'Default Button Text Color', 'options': 'color'},
			{'fieldname': 'sb8_cb3', 'fieldtype': 'Column Break'},
			{'fieldname': 'default_button_hover_text_color', 'fieldtype': 'Data', 'label': 'Default Button Hover Text Color', 'options': 'color'},
		]
	},
	{
		'name': 'footer',
		'title': 'Footer',
		'icon': 'fa fa-cube',
		'fields': [
			{'fieldname': 'footer_background_color', 'fieldtype': 'Data', 'label': 'Footer Background Color', 'options': 'color'},
			{'fieldname': 'footer_background_image', 'fieldtype': 'Attach Image', 'label': 'Footer Background Image'},
			{'fieldname': 'footer_text_color', 'fieldtype': 'Data', 'label': 'Footer Text Color', 'options': 'color'},
			{'fieldname': 'fcb1', 'fieldtype': 'Column Break'},
			{'fieldname': 'footer_link_color', 'fieldtype': 'Data', 'label': 'Footer Link Color', 'options': 'color'},
			{'fieldname': 'footer_link_hover_color', 'fieldtype': 'Data', 'label': 'Footer Link Hover Color', 'options': 'color'},
			{'fieldname': 'footer_heading_color', 'fieldtype': 'Data', 'label': 'Footer Heading Color', 'options': 'color'},
			{'fieldname': 'fcb2', 'fieldtype': 'Column Break'},
			{'fieldname': 'footer_address', 'fieldtype': 'Small Text', 'label': 'Footer Address'},
			{'fieldname': 'footer_email', 'fieldtype': 'Data', 'label': 'Footer Email'},
			{'fieldname': 'footer_phone', 'fieldtype': 'Data', 'label': 'Footer Phone'}
		]
	}
]