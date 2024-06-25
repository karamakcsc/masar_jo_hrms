from . import __version__ as app_version

app_name = "masar_jo_hrms"
app_title = "Masar Jo Hrms"
app_publisher = "KCSC"
app_description = "Masar JO HRMS"
app_email = "info@kcsc.com.jo"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/masar_jo_hrms/css/masar_jo_hrms.css"
# app_include_js = "/assets/masar_jo_hrms/js/masar_jo_hrms.js"

# include js, css files in header of web template
# web_include_css = "/assets/masar_jo_hrms/css/masar_jo_hrms.css"
# web_include_js = "/assets/masar_jo_hrms/js/masar_jo_hrms.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "masar_jo_hrms/public/scss/website"

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
# app_include_icons = "masar_jo_hrms/public/icons.svg"

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
# 	"methods": "masar_jo_hrms.utils.jinja_methods",
# 	"filters": "masar_jo_hrms.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "masar_jo_hrms.install.before_install"
# after_install = "masar_jo_hrms.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "masar_jo_hrms.uninstall.before_uninstall"
# after_uninstall = "masar_jo_hrms.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "masar_jo_hrms.utils.before_app_install"
# after_app_install = "masar_jo_hrms.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "masar_jo_hrms.utils.before_app_uninstall"
# after_app_uninstall = "masar_jo_hrms.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "masar_jo_hrms.notifications.get_notification_config"

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

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }
doctype_js = {
   "Employee" : "custom/employee/employee.js",
   "Salary Structure Assignment" : "custom/salary_structure_assignment/salary_structure_assignment.js",
   "Salary Slip" : "custom/salary_slip/salary_slip.js",
   ############## from mahmoud 
   "Payroll Entry" : "custom/payroll_entry/payroll_entry.js", 
 }


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"masar_jo_hrms.tasks.all"
# 	],
# 	"daily": [
# 		"masar_jo_hrms.tasks.daily"
# 	],
# 	"hourly": [
# 		"masar_jo_hrms.tasks.hourly"
# 	],
# 	"weekly": [
# 		"masar_jo_hrms.tasks.weekly"
# 	],
# 	"monthly": [
# 		"masar_jo_hrms.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "masar_jo_hrms.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "masar_jo_hrms.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "masar_jo_hrms.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["masar_jo_hrms.utils.before_request"]
# after_request = ["masar_jo_hrms.utils.after_request"]

# Job Events
# ----------
# before_job = ["masar_jo_hrms.utils.before_job"]
# after_job = ["masar_jo_hrms.utils.after_job"]

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
# 	"masar_jo_hrms.auth.validate"
# ]

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

###############
##############
##################
###########################    New Hooks 


fixtures = [
    {"dt": "Custom Field", "filters": [
        [
            "name", "in", [ 
            "Company-custom_social_security_liabilities",
            "Company-custom_employee_share_rate" , 
            "Company-custom_column_break_euvuw" , 
            "Company-custom_social_security_expenses" , 
            "Company-custom_company_share_rate" , 
            "Company-custom_social_security_info" ,
            "Company-custom_masar_hrms",
            "Salary Component-custom_is_social_security_applicable" , 
            "Salary Component-custom_is_overtime_applicable" ,  
            "Employee-custom_is_overtime_applicable" , 
            "Employee-custom_overtime_details" , 
            "Employee-custom_social_security_amount" , 
            "Employee-custom_social_security_salary" ,  
            "Employee-custom_social_security_date" , 
            "Employee-custom_tax_type" , 
            "Employee-custom_employee_share_rate" , 
            "Employee-custom_social_security_number" , 
            "Employee-custom_is_social_security_applicable" , 
            "Employee-custom_masar_hrms" , 
            "Employee-custom_tab_10",
            "Employee-custom_column_break_idzxg",
            "Employee-custom_national_no",
            "Employee-custom_nationality",
            "Employee-custom_personal_no"
            ]
        ]
    ]}
]

# from masar_jo_hrms.override import _salary_slip
# from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip



# SalarySlip.compute_taxable_earnings_for_year = _salary_slip.compute_taxable_earnings_for_year
# SalarySlip.calculate_variable_tax = _salary_slip.calculate_variable_tax
# SalarySlip.calculate_tax_by_tax_slab = _salary_slip.calculate_tax_by_tax_slab
# # SalarySlip.eval_tax_slab_condition = _salary_slip.eval_tax_slab_condition


# from masar_jo_hrms.override import _salary_slip
# from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
# # SalarySlip.get_working_days_details = _salary_slip.get_working_days_details





# from masar_jo_hrms.override import _salary_slip
# from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip

# SalarySlip.compute_taxable_earnings_for_year = _salary_slip.compute_taxable_earnings_for_year
# SalarySlip.calculate_variable_tax = _salary_slip.calculate_variable_tax
# SalarySlip.calculate_tax_by_tax_slab = _salary_slip.calculate_tax_by_tax_slab