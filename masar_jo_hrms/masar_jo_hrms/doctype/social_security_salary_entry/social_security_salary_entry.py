# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SocialSecuritySalaryEntry(Document):
	pass
# Copyright (c) 2023, KCSC and contributors
# For license information, please see license.txt

import json

from dateutil.relativedelta import relativedelta
import frappe
from frappe import _
from frappe.desk.reportview import get_filters_cond, get_match_cond
from frappe.model.document import Document
from frappe.query_builder.functions import Coalesce
from frappe.utils import (
	DATE_FORMAT,
	add_days,
	add_to_date,
	cint,
	comma_and,
	date_diff,
	flt,
	get_link_to_form,
	getdate,
)
import erpnext
from erpnext.accounts.utils import get_fiscal_year
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
import datetime
import masar_jo_hrms
from masar_jo_hrms.masar_jo_hrms.doctype.employee_social_security_salary.employee_social_security_salary import EmployeeSocialSecuritySalary
from frappe.model.document import Document


class SocialSecuritySalaryEntry(Document):
	def onload(self):
		if not self.docstatus == 1 or self.salary_slips_submitted:
			return
		
		# check if salary slips were manually submitted
		#Here
		# entries = frappe.db.count("Employee Social Security Salary", {"payroll_entry": self.name, "docstatus": 1}, ["name"])
		# if cint(entries) == len(self.employees):
		# 	self.set_onload("submitted_ss", True)		


	def validate(self):
		self.number_of_employees = len(self.employees)
		self.set_status()

	def on_submit(self):
		self.set_status(update=True, status="Submitted")
		#self.create_salary_slips()

	def set_status(self, status=None, update=False):
		if not status:
			status = {0: "Draft", 1: "Submitted", 2: "Cancelled"}[self.docstatus or 0]

		if update:
			self.db_set("status", status)
		else:
			self.status = status

			

	def get_emp_list(self):
		"""
		Returns list of active employees based on selected criteria
		and for which salary structure exists
		"""
		# self.check_mandatory()
		filters = self.make_filters()
		cond = get_filter_condition(filters)
		# cond += get_joining_relieving_condition(self.start_date, self.end_date)	

		condition = ""

		sal_struct = get_sal_struct(
			self.company, condition
		)
		if sal_struct:
			cond += "and t2.salary_structure IN %(sal_struct)s "
			# cond += "and %(from_date)s >= t2.from_date"
			emp_list = get_emp_list(sal_struct, cond)
			return emp_list

	def make_filters(self):
		filters = frappe._dict()
		filters["company"] = self.company
		filters["branch"] = self.branch
		filters["department"] = self.department
		filters["designation"] = self.designation

		return filters

	@frappe.whitelist()
	def fill_employee_details(self):
		self.set("employees", [])
		employees = self.get_emp_list()
		if not employees:
			error_msg = _(
				"No employees found for the mentioned criteria:<br>Company: {0}"
			).format(
				frappe.bold(self.company),
			)
			if self.branch:
				error_msg += "<br>" + _("Branch: {0}").format(frappe.bold(self.branch))
			if self.department:
				error_msg += "<br>" + _("Department: {0}").format(frappe.bold(self.department))
			if self.designation:
				error_msg += "<br>" + _("Designation: {0}").format(frappe.bold(self.designation))
			frappe.throw(error_msg, title=_("No employees found"))

		for d in employees:
			self.append("employees", d)

		self.number_of_employees = len(self.employees)

	# def check_mandatory(self):
	# 	for fieldname in ["company", "start_date", "end_date"]:
	# 		if not self.get(fieldname):
	# 			frappe.throw(_("Please set {0}").format(self.meta.get_label(fieldname)))



def get_sal_struct(
	company: str, condition: str
):
	return frappe.db.sql_list(
		"""
		select
			name from `tabSalary Structure`
		where
			docstatus = 1 and
			is_active = 'Yes'
			and company = %(company)s
			{condition}""".format(
			condition=condition
		),
		{
			"company": company,
		},
	)


def get_filter_condition(filters):
	cond = ""
	for f in ["company", "branch", "department", "designation"]:
		if filters.get(f):
			cond += " and t1." + f + " = " + frappe.db.escape(filters.get(f))

	return cond

# def get_joining_relieving_condition(start_date, end_date):
# 	cond = """
# 		and ifnull(t1.date_of_joining, '1900-01-01') <= '%(end_date)s'
# 		and ifnull(t1.relieving_date, '2199-12-31') >= '%(start_date)s'
# 	""" % {
# 		"start_date": start_date,
# 		"end_date": end_date,
# 	}
# 	return cond

def get_emp_list(sal_struct, cond):
	return frappe.db.sql(
		"""
			select
				distinct t1.name as employee, t1.employee_name, t1.department, t1.designation
			from
				`tabEmployee` t1, `tabSalary Structure Assignment` t2
			where
				t1.name = t2.employee
				and t2.docstatus = 1
				and t1.status != 'Inactive'
		%s order by t2.creation desc
		"""
		% cond,
		{
			"sal_struct": tuple(sal_struct),
			# "from_date": end_date,
		},
		as_dict=True,
	)

def get_employee_list(filters: frappe._dict) -> list[str]:
	condition = f"and payroll_frequency = '{filters.payroll_frequency}'"

	sal_struct = get_sal_struct(
		filters.company, condition
	)

	if not sal_struct:
		return []

	cond = (
		get_filter_condition(filters)
		# + get_joining_relieving_condition(filters.start_date, filters.end_date)
		+ (
			"and t2.salary_structure IN %(sal_struct)s "
			# "and t2.payroll_payable_account = %(payroll_payable_account)s "
			# "and %(from_date)s >= t2.from_date"
		)
	)
	emp_list = get_emp_list(sal_struct, cond)
	return emp_list


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def employee_query(doctype, txt, searchfield, start, page_len, filters):
	filters = frappe._dict(filters)
	conditions = []
	include_employees = []
	emp_cond = ""
	doctype = "Employee"

	if filters.start_date and filters.end_date:
		employee_list = get_employee_list(filters)
		emp = filters.get("employees") or []
		include_employees = [
			employee.employee for employee in employee_list if employee.employee not in emp
		]
		filters.pop("start_date")
		filters.pop("end_date")
		if filters.employees is not None:
			filters.pop("employees")

		if include_employees:
			emp_cond += "and employee in %(include_employees)s"

	return frappe.db.sql(
		"""select name, employee_name from `tabEmployee`
		where status = 'Active'
			and docstatus < 2
			and ({key} like %(txt)s
				or employee_name like %(txt)s)
			{emp_cond}
			{fcond} {mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, employee_name), locate(%(_txt)s, employee_name), 99999),
			idx desc,
			name, employee_name
		limit %(start)s, %(page_len)s""".format(
			**{
				"key": searchfield,
				"fcond": get_filters_cond(doctype, filters, conditions),
				"mcond": get_match_cond(doctype),
				"emp_cond": emp_cond,
			}
		),
		{
			"txt": "%%%s%%" % txt,
			"_txt": txt.replace("%", ""),
			"start": start,
			"page_len": page_len,
			"include_employees": include_employees,
		},
	)



############mahmoud start code 

@frappe.whitelist()
def create_employee_social_security_salary(name , posting_date):
	employee_sql = frappe.db.sql("""
		SELECT tssed.employee 
			FROM `tabSocial Security Salary Entry` tssse 
			INNER JOIN `tabSocial Security Employee Detail` tssed  ON tssse.name = tssed.parent 
			WHERE tssed.parent  = %s
	""" , (name))


	exist = frappe.db.sql("""
		SELECT employee , docstatus
			FROM `tabEmployee Social Security Salary` tesss 
		""")
	employee_name = [name[0] for name in  employee_sql]
	exist_employee = [name[0] for name in exist]
	status = [doc[1] for doc in exist]
	len_status = len(status)
	range_status = 0 
	for new_employee_ss in employee_name:
		if (new_employee_ss in exist_employee and status[range_status] == 1  ):
			if(range_status < len_status):
				range_status =+1 
		else:	
			doc = frappe.new_doc("Employee Social Security Salary")
			doc.employee = new_employee_ss
			doc.posting_date = posting_date
			doc.insert(ignore_permissions=True)
			doc.save()
			calcutale_all_share(new_employee_ss , doc)
			doc.save()
			doc.submit()

	return f'The Employee Social Security Salary is created For All Employee Except The Employees : {exist_employee} Becuase Alredy Created '
			
@frappe.whitelist()
def calcutale_all_share(employee  , doc ):
	sql = frappe.db.sql("""
		SELECT  tesss.company_share_rate , tesss.employee_share_rate ,tssa.base 
			FROM `tabEmployee Social Security Salary` tesss 
			INNER JOIN `tabSalary Structure Assignment` tssa ON tesss.employee  = tssa.employee 
			WHERE tesss.employee =  %s AND tssa.docstatus = 1 
	""" , (employee) , as_dict=True)
	
	result = sql

	company_share_rate = result[0]['company_share_rate']
	employee_share_rate = result[0]['employee_share_rate'] 
	base_salary = result[0]['base']


	company_share = base_salary * (company_share_rate/100)
	employee_share = base_salary * (employee_share_rate/100)
	doc.ss_company_share_amount = company_share
	doc.ss_emp_share_amount = employee_share
	doc.amount = base_salary
