import frappe
from frappe import _


@frappe.whitelist()
def check_ss_jv(company, name, posting_date):
    ss_liabilities       = frappe.db.get_all("Company", {"name" : company} ,"social_security_liabilities")[0]['social_security_liabilities']
    ss_expenses          = frappe.db.get_all("Company", {"name" : company} , "custom_social_security_expenses")[0]['custom_social_security_expenses']
    cost_center          = frappe.db.get_all("Company", {"name" : company} ,"cost_center")[0]['cost_center']
    result = frappe.db.sql("""
        SELECT *
        FROM `tabJournal Entry Account` tjea 
        WHERE reference_type = 'Payroll Entry' AND reference_name = %s AND against_account IN (%s, %s)
    """, (name, ss_expenses, ss_liabilities), as_dict=True)
    if result:
        frappe.throw(_("The Social Security Journal Entry Has Been Created For The Same Period."))
    else:
        return ss_jv(company, name, posting_date, cost_center , ss_liabilities , ss_expenses)
          


@frappe.whitelist()
def ss_jv(company, name, posting_date, cost_center , ss_liabilities , ss_expenses):
    company_share_rate   = float((frappe.db.get_all("Company","custom_company_share_rate"))[0]['custom_company_share_rate'])
    employee_share_rate  = float((frappe.db.get_all("Company", "custom_employee_share_rate"))[0]['custom_employee_share_rate'])
    # amounts_of_employee  = (frappe.db.get_all("Employee" ,fields =["social_security_amount"]))
    amount_sql = frappe.db.sql("""
    select sum(tsd.default_amount) as `amount`
    from `tabSalary Slip` tss 
    inner join `tabSalary Detail` tsd on tss.name = tsd.parent 
    inner join `tabPayroll Entry` tpe on tpe.name = tss.payroll_entry 
    where tsd.salary_component = 'Company Social Security' and tpe.name = %s and tss.docstatus =1
    """, (name) , as_dict = True)
    ss_amount= amount_sql[0]['amount']
    ss_calculation = (ss_amount * (company_share_rate/100)) / (employee_share_rate/100)
    
    jv = frappe.new_doc("Journal Entry")
    jv.posting_date = posting_date
    jv.company =  company
    jv.cost_center = cost_center
    jv.cheque_no = name
    jv.cheque_date = posting_date
    jv.user_remark = f"Payroll Entry is:{name} in the Posting Date :{posting_date}"

    jv.append("accounts", {
        "account": ss_expenses,
        "debit_in_account_currency": ss_calculation,
        "cost_center": cost_center,
        "reference_type" : "Payroll Entry", 
        "reference_name" : name , 
        "reference_due_date" : posting_date,
        "user_remark": f"reference type is Payroll Entry , Reference Name is {name} and Reference Due Date is :{posting_date} "
    })

    jv.append("accounts", {
        "account": ss_liabilities,
        "credit_in_account_currency": ss_calculation,
        "cost_center": cost_center,
        "reference_type" : "Payroll Entry", 
        "reference_name" : name , 
        "reference_due_date" : posting_date,
         "user_remark": f"reference type is Payroll Entry , Reference Name is {name} and Reference Due Date is :{posting_date} "
    })

    jv.insert(ignore_permissions=True)
    jv.submit()
    return(f"Journal Entries created for{company} in Journal Entry")

   