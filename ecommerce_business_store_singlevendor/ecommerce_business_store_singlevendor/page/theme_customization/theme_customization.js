frappe.pages['theme-customization'].on_page_load = function(wrapper) {
	frappe.theme_edit = new ThemeEdit(wrapper);
}
frappe.pages['theme-customization'].refresh = function (wrapper) {
	let routes = frappe.get_route();
	if(routes.length == 1)
		frappe.set_route('theme-customization', 'edit', 'index');
	frappe.theme_edit.page_name = routes[2];
	if(routes.length == 4)
		frappe.theme_edit._page_name = routes[3];
	frappe.theme_edit.refresh();
}
var ThemeEdit = Class.extend({
	init: function(parent) {
		this.parent = parent;
		this.device_type = 'Desktop';
		this.dd_type = 'desktop';
		this.page_title = '';
		this.page_name = '';
		this._page_name = '';
		this.__unsaved = false;
		this.make();
	},
	make: function() {
		this.page = frappe.ui.make_app_page({
			parent: this.parent,
			title: 'Theme Customization',
			single_column: true
		});
		this.render_page_template();
		this.get_pages_list();
	},
	render_page_template: function() {
		this.page.main.append(template);
		this.page_renderer = template.find('.page-renderer');
		this.mobile_device = template.find('#mobileDevice');
		this.tab_device = template.find('#tabletDevice');
		this.desktop_device = template.find('#desktopDevice');
		this.pagelist = template.find('#pageTitle');
		this.primary_action = template.find('.btn-primary');
		this.setup_device_change();
		this.setup_side_bar();
		this.setup_primary_action();
	},
	refresh: function() {
		if(this.page_name == 'index') {
			this.page_title = 'Home';
			this._page_name = 'index';
		} else {
			this.page_title = this.page_name;
		}
		template.find('#menuList .page-title').html(this.page_title);
		this.route = window.location.origin + (this._page_name == 'index' ? '' : '/' + this._page_name);
		this.set_iframe();
	},
	setup_device_change: function() {
		let me = this;
		this.mobile_device.on('click', function() {
			if(me.iFrame) {
				me.page_renderer.html('');
			}
			me.page_renderer.removeClass('tab-width');
			me.page_renderer.addClass('mobile-width');
			me.device_type = 'Mobile';
			this.dd_type = 'mobile';
			me.set_iframe();
		});
		this.tab_device.on('click', function() {
			if(me.iFrame) {
				me.page_renderer.html('');
			}
			me.page_renderer.removeClass('mobile-width');
			me.page_renderer.addClass('tab-width');
			me.device_type = 'Desktop';
			this.dd_type = 'tablet';
			me.set_iframe();
		});
		this.desktop_device.on('click', function() {
			if(me.iFrame) {
				me.page_renderer.html('');
			}
			me.page_renderer.removeClass('mobile-width');
			me.page_renderer.removeClass('tab-width');
			me.device_type = 'Desktop';
			this.dd_type = 'desktop';
			me.set_iframe();
		});
	},
	set_iframe: function() {
		let route = this.route + '?sid=' + getCookie('sid') + '&device_type=' + this.device_type;
		template.find('.loader-div').hide();
		this.iFrame = $(`<iframe seamless src="${route}"></iframe>`).appendTo(this.page_renderer);
	},
	get_pages_list: function() {
		let me = this;
		this.pages_list = [];
		this.catalog_settings = {};
		this.web_theme = {};
		frappe.call({
			method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.theme_customization.theme_customization.get_page_details',
			args: {
				website: window.location.host
			},
			callback: function(r) {
				if(r.message) {
					me.pages_list = r.message.pages;
					me.catalog_settings = r.message.catalog_settings;
					me.web_theme = r.message.theme_settings;
					me.update_pages();
				}
			}
		})
	},
	update_pages: function() {
		let me = this;
		if(this.pages_list.length > 0) {
			$(this.pages_list).each((k, v) => {
				let row = $(`<li>
						<a href="#" onclick="return false;">${v.page_title}</a>
					</li>`);
				this.pagelist.find('.dropdown-menu').append(row);
				row.on('click', function() {
					template.find('.loader-div').show();
					me.page_renderer.html('');
					if(v.name != 'index')
						frappe.set_route('theme-customization', 'edit', v.page_title, v.route);
					else
						frappe.set_route('theme-customization', 'edit', 'index');
				});
			});
		}
	},
	setup_side_bar: function() {
		let me = this;
		this.sidebar = template.find('#editOpts');
		let theme = $(`<li class="pad-0">
				<a href="#" onclick="return false;">
					<i class="fa fa-paint-brush"></i>
					<span>Theme</span>
				</a>
			</li>`);
		this.sidebar.append(theme);
		theme.on('click', function() {
			me.edit_type = 'theme';
			me.show_modal();
		});
		let header = $(`<li class="pad-0">
				<a href="#" onclick="return false;">
					<i class="fa fa-file-o"></i>
					<span>Header</span>
				</a>
			</li>`);
		this.sidebar.append(header);
		header.on('click', function() {
			me.edit_type = 'header';
			me.show_modal();
		})
		let footer = $(`<li class="pad-0">
				<a href="#" onclick="return false;">
					<i class="fa fa-file-o"></i>
					<span>Footer</span>
				</a>
			</li>`);
		this.sidebar.append(footer);
		footer.on('click', function() {
			me.edit_type = 'footer';
			me.show_modal();
		})
	},
	show_modal: function() {
		let me = this;
		this.modal = new frappe.ui.Dialog({
			title: `${me.edit_type.toUpperCase()} SETTINGS`,
			fields: me.get_fields_list()
		});
		this.modal.show();
		this.modal.$wrapper.find('.modal-dialog').css({
			'width': '400px', 'margin': '40px 8.33%'
		});
		this.modal.$wrapper.find('.modal-content').css({'border-radius': 0});
		this.modal.$wrapper.find('.modal-header .modal-title').css({
			'font-weight': 500, 'font-size': '14px'
		});
		this.modal.$wrapper.find('.btn-modal-close').find('span').text('');
		this.modal.$wrapper.find('.btn-modal-close').find('span').addClass('fa fa-times');
		this.modal.$wrapper.find('.btn-modal-close').addClass('btn-link');
		this.modal.$wrapper.find('.modal-backdrop').css('display', 'none');
		this.update_modal_values();
	},
	get_fields_list: function() {
		return fields_list.find(obj => obj.type == this.edit_type).fields;
	},
	update_modal_values: function() {
		let me = this;
		let fields = this.get_fields_list();
		$(fields).each((k, v) => {
			if(v._dt){
				let setting = this[variable_map[v._dt]];
				if(setting[v.fieldname])
					this.modal.set_value(v.fieldname, setting[v.fieldname]);
				this.modal.fields_dict[v.fieldname].$input.on('change', function() {
					me.__unsaved = true;
					setting[v.fieldname] = me.modal.get_value(v.fieldname);
					me.update_preview();
				});
			}
		});
	},
	update_preview: function() {
		let me = this;
		frappe.call({
			method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.theme_customization.theme_customization.update_cache_value',
			args: {
				catalog: JSON.stringify(me.catalog_settings),
				theme: JSON.stringify(me.web_theme)
			},
			async: false,
			freeze_message: __('Updating'),
			callback: function(r) {
				me.set_iframe();
			}
		})
	},
	setup_primary_action: function() {
		this.primary_action.click(() => {
			if(this.__unsaved) {
				this.__unsaved = false;
				this.update_value(this.catalog_settings, 'catalog_settings');
				this.update_value(this.web_theme, 'web_theme');
			}				
		});
	},
	update_value: function(data, field) {
		let me = this;
		frappe.call({
			method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.mobileapi.update_doc',
			args: {
				doc: JSON.stringify(data)
			},
			callback: function(r) {
				if(r.message) {
					me[field] = r.message;
				}
			}
		})
	}
});
var template = $(`<header>
	<div class="navbar navbar-default navbar-fixed-top">
		<div class="container-fluid">
			<div class="row">
				<div class="col-md-2">
					
				</div>
				<div class="col-md-4">
					<ul id="menuList" class="nav navbar-nav">
						<li id="pageTitle" class="dropdown">
							<a class="dropdown-toggle" data-toggle="dropdown" href="#" onclick="return false;">
								<span class="page-title"></span> 
								<span class="caret"></span>
							</a>
							<ul class="dropdown-menu"></ul>
						</li>
						<li id="desktopDevice" class="devicetypes">
							<a href="#" onclick="return false;">
								<span class="fa fa-desktop"></span>
							</a>
						</li>
						<li id="tabletDevice" class="devicetypes">
							<a href="#" onclick="return false;">
								<span class="fa fa-tablet"></span>
							</a>
						</li>
						<li id="mobileDevice" class="devicetypes">
							<a href="#" onclick="return false;">
								<span class="fa fa-mobile"></span>
							</a>
						</li>
					</ul>
				</div>
				<div class="col-md-6">
					<div class="floatRight pad-5">
						<button class="btn btn-primary">Save</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</header>
<div class="content-div">
	<div class="container-fluid">
		<div class="row">
			<div class="col-md-1 pad-0">
				<ul id="editOpts"></ul>
			</div>
			<div class="col-md-11 pad-0">
				<div class="loader-div">Loading...</div>
				<div class="page-renderer"></div>
			</div>
		</div>
	</div>
</div>
<style>
	body[data-route*="theme-customization"] .main-section .main-header,
	body[data-route*="theme-customization"] .main-section .main-sidebar,
	body[data-route*="theme-customization"] .main-section .page-head {
	    display: none;
	}
	body[data-route*="theme-customization"] .main-section .layout-main-section {
	    border: 0;
	}
	body[data-route*="theme-customization"] .main-section .page-content {
	    margin-top: 0;
	    padding-left: 0 !important;
	}
	#page-theme-customization #pageTitle a {
		min-width: 150px;
		padding: 10px;
	}
	#page-theme-customization .navbar .nav > li > a {
		border-right: 1px solid #ddd;
	}
	#page-theme-customization #pageTitle .caret {
		float: right;
		margin-top: 9px;
	}
	#page-theme-customization .devicetypes a {
		padding: 10px 15px;
		font-size: 18px;
	}
	#page-theme-customization .layout-main-section-wrapper {
		padding: 0;
		margin: 0;
	}
	.pad-0 {
		padding: 0;
	}
	.pad-5 {
		padding: 5px;
	}
	#page-theme-customization .content-div {
		margin-top: 40px;
	}
	#page-theme-customization .page-renderer {
		position: relative;
		width: 100%;
		padding-top: 49.25%;
		height: calc(100% - 40px);
		overflow: hidden;
	}
	#page-theme-customization .page-renderer iframe {
		position: absolute;
		top: 0;
		left: 0;
		bottom: 0;
		right: 0;
		width: 100%;
		height: 100%;
		border: 0;
	}
	#page-theme-customization .page-renderer.mobile-width {
		width: 320px;
		margin: auto;
	}
	#page-theme-customization .page-renderer.tab-width {
		width: 768px;
		margin: auto;
	}
	#page-theme-customization .loader-div {
		width: 100%;
		height: 100%;
		position: fixed;
		text-align: center;
		padding: 20%;
		background: #f5f5f5;
	}
	#page-theme-customization #editOpts {
		list-style: none;
		padding-inline-start: 0px;
		background: #efefef;
		position: fixed;
		height: 100%;
		width: 8.33%;
		border-right: 1px solid #ddd;
	}
	#page-theme-customization #editOpts li a {
		padding: 13px 10px;
		display: block;
		text-align: center;
		font-size: 13px;
		border-bottom: 1px solid #ddd;
	}
	#page-theme-customization #editOpts li a i {
		font-size: 25px;
	}
	#page-theme-customization #editOpts li a span {
		display: block;
		margin-top: 5px;
	}
	#page-theme-customization #editOpts li a:hover {
		text-decoration: none;
	}
	#page-theme-customization .floatRight {
		float: right;
	}
</style>`);
let fields_list = [
	{
		'type': 'theme',
		'fields': []
	},
	{
		'type': 'header',
		'fields': [
			{
				'fieldtype': 'Attach Image',
				'fieldname': 'website_logo',
				'label': 'Website Logo',
				'_dt': 'Catalog Settings'
			},
			{
				'fieldtype': 'Data',
				'fieldname': 'site_name',
				'label': __('Site Name'),
				'_dt': 'Catalog Settings',
			},
			{
				'fieldtype': 'Attach Image',
				'fieldname': 'favicon',
				'label': __('FavIcon'),
				'_dt': 'Web Theme'
			},
			{ 'fieldtype': 'Section Break', 'fieldname': 'header_sec_01' },
			{
				'fieldtype': 'Check',
				'fieldname': 'include_all_categories',
				'label': __('Include All Categories In Menu?'),
				'_dt': 'Catalog Settings'
			}
		]
	},
	{
		'type': 'footer',
		'fields': []
	},
]
let variable_map = {
	'Catalog Settings': 'catalog_settings',
	'Web Theme': 'web_theme'
}