app_name = "dbiz_ai_agent"
app_title = "dbiz_ai_agent"
app_publisher = "danls"
app_description = "AI Agent"
app_email = "danls@dbiz.com"
app_license = "gpl-3.0"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "dbiz_ai_agent",
# 		"logo": "/assets/dbiz_ai_agent/logo.png",
# 		"title": "dbiz_ai_agent",
# 		"route": "/dbiz_ai_agent",
# 		"has_permission": "dbiz_ai_agent.api.permission.has_app_permission"
# 	}
# ]
website_route_rules = [
	# Route any subpath under /ai-agent/* to the single SPA page 'dbiz_ai_agent'
	{"from_route": "/ai-agent/<path:app_path>", "to_route": "dbiz_ai_agent"},
	{"from_route": "/ai-agent", "to_route": "dbiz_ai_agent"},
]

fixtures = [
    "Custom Field",
    {"dt": "AI Agent Settings"}
]

after_install = [
    "dbiz_ai_agent.helpers.contact_sync.sync_ai_role_contacts",
]

after_migrate = [
    "dbiz_ai_agent.helpers.contact_sync.sync_ai_role_contacts",
]
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/dbiz_ai_agent/css/dbiz_ai_agent.css"
# app_include_js = "/assets/dbiz_ai_agent/js/dbiz_ai_agent.js"

app_include_js = [
    "/assets/dbiz_ai_agent/js/dbiz_ai_agent.bundle.js",
]

# include js, css files in header of web template
# web_include_css = "/assets/dbiz_ai_agent/css/dbiz_ai_agent.css"
# web_include_js = "/assets/dbiz_ai_agent/js/dbiz_ai_agent.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "dbiz_ai_agent/public/scss/website"

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

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "dbiz_ai_agent/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "dbiz_ai_agent.utils.jinja_methods",
# 	"filters": "dbiz_ai_agent.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "dbiz_ai_agent.install.before_install"
# after_install = "dbiz_ai_agent.install.after_install"

# After migrate - run patches

# Uninstallation
# ------------

# before_uninstall = "dbiz_ai_agent.uninstall.before_uninstall"
# after_uninstall = "dbiz_ai_agent.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "dbiz_ai_agent.utils.before_app_install"
# after_app_install = "dbiz_ai_agent.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "dbiz_ai_agent.utils.before_app_uninstall"
# after_app_uninstall = "dbiz_ai_agent.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "dbiz_ai_agent.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "AI Document": {
        "on_update": "dbiz_ai_agent.scripts.reindex_documents_permissions.on_document_update",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"dbiz_ai_agent.tasks.all"
# 	],
# 	"daily": [
# 		"dbiz_ai_agent.tasks.daily"
# 	],
# 	"hourly": [
# 		"dbiz_ai_agent.tasks.hourly"
# 	],
# 	"weekly": [
# 		"dbiz_ai_agent.tasks.weekly"
# 	],
# 	"monthly": [
# 		"dbiz_ai_agent.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "dbiz_ai_agent.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "dbiz_ai_agent.event.get_events"
# }

# Whitelist API methods
override_whitelisted_methods = {
	"dbiz_ai_agent.api.documents.get_documents": "dbiz_ai_agent.api.documents.get_documents",
	"dbiz_ai_agent.api.documents.get_folders": "dbiz_ai_agent.api.documents.get_folders",
	"dbiz_ai_agent.api.documents.create_folder": "dbiz_ai_agent.api.documents.create_folder",
	"dbiz_ai_agent.api.documents.delete_folder": "dbiz_ai_agent.api.documents.delete_folder",
	"dbiz_ai_agent.api.documents.upload_document": "dbiz_ai_agent.api.documents.upload_document",
	"dbiz_ai_agent.api.documents.delete_document": "dbiz_ai_agent.api.documents.delete_document",
	"dbiz_ai_agent.api.documents.move_document": "dbiz_ai_agent.api.documents.move_document",
	"dbiz_ai_agent.api.roles.get_roles": "dbiz_ai_agent.api.roles.get_roles",
	"dbiz_ai_agent.api.roles.create_role": "dbiz_ai_agent.api.roles.create_role",
	"dbiz_ai_agent.api.roles.update_role": "dbiz_ai_agent.api.roles.update_role",
	"dbiz_ai_agent.api.roles.delete_role": "dbiz_ai_agent.api.roles.delete_role",
	"dbiz_ai_agent.api.roles.get_role_details": "dbiz_ai_agent.api.roles.get_role_details",
	"dbiz_ai_agent.api.roles.toggle_role_status": "dbiz_ai_agent.api.roles.toggle_role_status",
	"dbiz_ai_agent.api.roles.get_role_statistics": "dbiz_ai_agent.api.roles.get_role_statistics"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "dbiz_ai_agent.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["dbiz_ai_agent.utils.cors.handle_cors"]
after_request = ["dbiz_ai_agent.helpers.cors.handle_cors"]

# Job Events
# ----------
# before_job = ["dbiz_ai_agent.utils.before_job"]
# after_job = ["dbiz_ai_agent.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"dbiz_ai_agent.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
