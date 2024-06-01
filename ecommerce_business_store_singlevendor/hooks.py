from . import __version__ as app_version

app_name = "ecommerce_business_store_singlevendor"
app_title = "Ecommerce Business Store SingleVendor"
app_publisher = "Tridotstech Private Ltd."
app_description = "Single vendor ecommerce app"
app_email = "info@valiantsystems.com"
app_license = "MIT"
 
app_logo_url = "/assets/ecommerce_business_store_singlevendor/images/gokommerce-logo.png"

# setup wizard
# setup_wizard_requires = "assets/ecommerce_business_store_singlevendor/js/setup_wizard.js"
# setup_wizard_stages = "ecommerce_business_store_singlevendor.utils.setup_wizard.get_setup_stages"
# setup_wizard_complete = "ecommerce_business_store_singlevendor.utils.setup_wizard.setup_complete"
#page Analytics 
leaderboard = "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.leaders.get_leaderboards"

boot_session = "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.boot_session"

custo="ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.cust.get_leaderboards"

leaderboardorder="ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.leaderboardtest.get_leaderboardorder"

custo = "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.cust.get_leaderboards"
leaderboardorder = "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.leaderboardtest.get_leaderboardorder"
# website permission
has_website_permission = {
	'Customers':'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.customer_web_permission'
}
after_install = "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.after_install.after_install"
# on login
on_session_creation = "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.login_customer"

app_include_css = [
	"/assets/ecommerce_business_store_singlevendor/css/console.css",
	"/assets/ecommerce_business_store_singlevendor/css/ui/uploader.css",
]
app_include_js = [
    "/assets/ecommerce_business_store_singlevendor/js/ui/dialog_popup.js",
     "/assets/ecommerce_business_store_singlevendor/js/default_methods.js",
     "/assets/ecommerce_business_store_singlevendor/js/option.js",
	"/assets/ecommerce_business_store_singlevendor/js/console.js",
	"/assets/ecommerce_business_store_singlevendor/js/getting_started.js",
	"assets/ecommerce_business_store_singlevendor/js/ui/product_func_class.js",
	"assets/ecommerce_business_store_singlevendor/js/quick_entry/return_quick_entry.js",
]
doctype_js = {
    "Web Form" : "public/js/ui/editor/web_form.js",
     "Web Page Builder" : "public/js/web_page_builder.js"
    }

page_js = {
	"products-bulk-update": [
		"public/plugins/datatable/sortable.min.js",
		"public/plugins/datatable/clusterize.min.js",
		"public/plugins/datatable/frappe-datatable.min.js",
		"public/js/uppy.min.js",
		"public/js/lightgallery.js"
	],
	"seo-tool": [
		"public/plugins/datatable/sortable.min.js",
		"public/plugins/datatable/clusterize.min.js",
		"public/plugins/datatable/frappe-datatable.min.js"
	]
}

has_permission = {
	# "Product Tax Template": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.product_tax_template.product_tax_template.has_permission",
	# "Return Policy": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.return_policy.return_policy.has_permission",
	# "Discounts": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.discounts.discounts.has_permission"
}
has_website_permission = {
	"Customers": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.customers.customers.has_website_permission"
}

override_doctype_class = {
	'File': 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.override.CustomFile',
	'PageSection': 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.override.PageSection'
}


doc_events = {
	"User": {
		"after_insert": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.customers.customers.generate_keys"
	},
	"Newsletter": {
		"autoname": "ecommerce_business_store_singlevendor.utils.setup.autoname_newsletter"
	},
	"Product": {
		"on_update": "ecommerce_business_store_singlevendor.utils.setup.website_generator_update",
		"on_trash": "ecommerce_business_store_singlevendor.utils.setup.website_generator_trash"
	},
	"Product Category": {
		"on_update": "ecommerce_business_store_singlevendor.utils.setup.website_generator_update",
		"on_trash": "ecommerce_business_store_singlevendor.utils.setup.website_generator_trash"
	},
	"Order": {
		"on_submit": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.whoosh.update_order_item"
	},
	"Google Settings": {
		"validate": "ecommerce_business_store_singlevendor.utils.setup.validate_google_settings"
	},
	"Help Article": {
		"validate": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.create_help_article_json"
	},
		"Order Settings": {
		"on_update": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.generate_all_website_settings_json_doc"
	},
	"Catalog Settings": {
		"on_update": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.generate_all_website_settings_json_doc"
	},
	"Market Place Settings": {
		"on_update": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.generate_all_website_settings_json_doc"
	},
	"Shopping Cart Settings": {
		"on_update": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.generate_all_website_settings_json_doc"
	},
	"Product Category": {
		"on_update": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.generate_all_website_settings_json_doc"
	},
	"Media Settings": {
		"on_update": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.generate_all_website_settings_json_doc"
	},
	"Header Component": {
		"on_update": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.generate_all_website_settings_json_doc"
	},
	"Footer Component": {
		"on_update": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.generate_all_website_settings_json_doc"
	},
	"Menu": {
		"on_update": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.common.generate_all_website_settings_json_doc"
	},
	"Version":{
		"after_insert":"ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.v2.orders.update_stoke"
	}
}

# Scheduled Tasks
# ---------------
scheduler_events = {
	"all": [
		"ecommerce_business_store_singlevendor.accounts.api.release_lockedin_amount",
		"ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.product.product.check_menu_available_time",
		"ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.order.order.auto_complete_orders",
	],
	"daily": [
		"ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.donations.donations.remove_guestuser",
	],
	
	"monthly": [
		"ecommerce_business_store_singlevendor.utils.setup.clear_logs"	
	],
	"cron": {
		"* * * * *": [
			"frappe.email.queue.flush",
		],
		"0 1 * * *": [
			"ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.customers.customers.delete_guest_customers",
			"ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.shopping_cart.shopping_cart.check_cart_discounts",
			"ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.pos_settings.pos_settings.clear_pos_orders",
			"ecommerce_business_store_singlevendor.membership.api.create_memberships"
		],
		"30 12 1 * *":[
			"ecommerce_business_store_singlevendor.utils.setup.clear_api_log"
		]
	}
}

fixtures = [
	{
		"doctype": "Custom Script",
		"filters": [
			["name", "in", (
				"Newsletter-Client"
			)]
		]
	},
	{
		"doctype": "Custom Field",
		"filters": [
			["name", "in", (
				"Country-enabled",
				"Country-phone_number_code",
				"Country-validate_zipcode",
				"Country-zipcode_validation_policy",
				"Country-min_zipcode_length",
				"Country-max_zipcode_length",
				"Notification-allow_user_modify",
				"Email Group Member-business",
				"Google Settings-restrict_to_countries",
				"Google Settings-countries",
				"Google Settings-default_address",
				"Google Settings-latitude",
				"Google Settings-longitude",
				"Google Settings-marker_icon",
				"Help Article-doctype_name",
				"Help Article-domain_name",
				"Email Group-business",
			)]
		]
	}
]

# Set default Role-updateby siva
# -------
default_roles = [
	{'role': 'Customer', 'doctype':'Customers'},
]
override_whitelisted_methods = {
    "frappe.client.validate_link": "ecommerce_business_store_singlevendor.utils.utils.validate_link",
    "frappe.desk.form.linked_with.cancel_all_linked_docs": "ecommerce_business_store_singlevendor.utils.utils.cancel_all_linked_docs"
    
}

auto_cancel_exempted_doctypes = ["Order"]
# before_tests = "ecommerce_business_store_singlevendor.install.before_tests"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ecommerce_business_store_singlevendor/css/ecommerce_business_store_singlevendor.css"
# app_include_js = "/assets/ecommerce_business_store_singlevendor/js/ecommerce_business_store_singlevendor.js"

# include js, css files in header of web template
# web_include_css = "/assets/ecommerce_business_store_singlevendor/css/ecommerce_business_store_singlevendor.css"
# web_include_js = "/assets/ecommerce_business_store_singlevendor/js/ecommerce_business_store_singlevendor.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ecommerce_business_store_singlevendor/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "ecommerce_business_store_singlevendor.utils.jinja_methods",
#	"filters": "ecommerce_business_store_singlevendor.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ecommerce_business_store_singlevendor.install.before_install"
# after_install = "ecommerce_business_store_singlevendor.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ecommerce_business_store_singlevendor.uninstall.before_uninstall"
# after_uninstall = "ecommerce_business_store_singlevendor.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ecommerce_business_store_singlevendor.utils.before_app_install"
# after_app_install = "ecommerce_business_store_singlevendor.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ecommerce_business_store_singlevendor.utils.before_app_uninstall"
# after_app_uninstall = "ecommerce_business_store_singlevendor.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ecommerce_business_store_singlevendor.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"ecommerce_business_store_singlevendor.tasks.all"
#	],
#	"daily": [
#		"ecommerce_business_store_singlevendor.tasks.daily"
#	],
#	"hourly": [
#		"ecommerce_business_store_singlevendor.tasks.hourly"
#	],
#	"weekly": [
#		"ecommerce_business_store_singlevendor.tasks.weekly"
#	],
#	"monthly": [
#		"ecommerce_business_store_singlevendor.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "ecommerce_business_store_singlevendor.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "ecommerce_business_store_singlevendor.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "ecommerce_business_store_singlevendor.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ecommerce_business_store_singlevendor.utils.before_request"]
# after_request = ["ecommerce_business_store_singlevendor.utils.after_request"]

# Job Events
# ----------
# before_job = ["ecommerce_business_store_singlevendor.utils.before_job"]
# after_job = ["ecommerce_business_store_singlevendor.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"ecommerce_business_store_singlevendor.auth.validate"
# ]
