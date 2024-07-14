import frappe
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry ,get_existing_salary_slips , log_payroll_failure
create_salary_slips = PayrollEntry.create_salary_slips
from frappe import _
@frappe.whitelist()
def create_salary_slips(self):
    """
    Creates salary slip for selected employees if already not created
    """
    self.check_permission("write")
    employees = [emp.employee for emp in self.employees]

    if employees:
        args = frappe._dict(
            {
                "salary_slip_based_on_timesheet": self.salary_slip_based_on_timesheet,
                "payroll_frequency": self.payroll_frequency,
                "start_date": self.start_date,
                "end_date": self.end_date,
                "company": self.company,
                "posting_date": self.posting_date,
                "deduct_tax_for_unclaimed_employee_benefits": self.deduct_tax_for_unclaimed_employee_benefits,
                "deduct_tax_for_unsubmitted_tax_exemption_proof": self.deduct_tax_for_unsubmitted_tax_exemption_proof,
                "payroll_entry": self.name,
                "exchange_rate": self.exchange_rate,
                "currency": self.currency,
            })
        if len(employees) > 30 or frappe.flags.enqueue_payroll_entry:
            self.db_set("status", "Queued")
            frappe.enqueue(
                create_salary_slips_for_employees,
                timeout=3000,
                employees=employees,
                args=args,
                publish_progress=False,
            )
            frappe.msgprint(("Salary Slip creation is queued. It may take a few minutes"),alert=True,
                indicator="blue",
            )
        else:
            create_salary_slips_for_employees(employees, args, publish_progress=False)
            # since this method is called via frm.call this doc needs to be updated manually
            self.reload()

def create_salary_slips_for_employees(employees, args, publish_progress=True):
	payroll_entry = frappe.get_cached_doc("Payroll Entry", args.payroll_entry)

	try:
		salary_slips_exist_for = get_existing_salary_slips(employees, args)
		count = 0

		employees = list(set(employees) - set(salary_slips_exist_for))
		for emp in employees:
			args.update({"doctype": "Salary Slip", "employee": emp})
			doc = frappe.get_doc(args).insert()
			doc.deduct_tax_for_unsubmitted_tax_exemption_proof = not(doc.deduct_tax_for_unsubmitted_tax_exemption_proof)
			doc.run_method('save')
			doc.deduct_tax_for_unsubmitted_tax_exemption_proof = not(doc.deduct_tax_for_unsubmitted_tax_exemption_proof)
			doc.run_method('validate')
			doc.run_method('save')
			count += 1
			if publish_progress:
				frappe.publish_progress(
					count * 100 / len(employees),
					title=_("Creating Salary Slips..."),
				)

		payroll_entry.db_set({"status": "Submitted", "salary_slips_created": 1, "error_message": ""})

		if salary_slips_exist_for:
			frappe.msgprint(
				_(
					"Salary Slips already exist for employees {}, and will not be processed by this payroll."
				).format(frappe.bold(", ".join(emp for emp in salary_slips_exist_for))),
				title=_("Message"),
				indicator="orange",
			)

	except Exception as e:
		frappe.db.rollback()
		log_payroll_failure("creation", payroll_entry, e)

	finally:
		frappe.db.commit()  # nosemgrep
		frappe.publish_realtime("completed_salary_slip_creation", user=frappe.session.user)

###3