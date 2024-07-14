import frappe
from frappe import _
from frappe.utils import (add_days,cint,cstr,flt,getdate,ceil)
from hrms.payroll.doctype.salary_slip.salary_slip import eval_tax_slab_condition
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip as SS
get_amount_based_on_payment_days = SS.get_amount_based_on_payment_days
get_future_recurring_additional_amount = SS.get_future_recurring_additional_amount

def get_taxable_earnings(self, allow_tax_exemption=False, based_on_payment_days=0):
	taxable_earnings = 0
	additional_income = 0
	additional_income_with_full_tax = 0
	flexi_benefits = 0
	amount_exempted_from_income_tax = 0
	for earning in self.earnings:
		if based_on_payment_days:
			amount, additional_amount = self.get_amount_based_on_payment_days(earning)
		else:
			if earning.additional_amount:
				amount, additional_amount = earning.amount, earning.additional_amount
			else:
				amount, additional_amount = earning.default_amount, earning.additional_amount

		if earning.is_tax_applicable:
			if earning.is_flexible_benefit:
				flexi_benefits += amount
			else:
				taxable_earnings += amount - additional_amount
				additional_income += additional_amount
				if earning.deduct_full_tax_on_selected_payroll_date:
					additional_income_with_full_tax += additional_amount
	if allow_tax_exemption:
		for ded in self.deductions:
			if ded.exempted_from_income_tax:
				amount, additional_amount = ded.amount, ded.additional_amount
				if based_on_payment_days:
					amount, additional_amount = self.get_amount_based_on_payment_days(ded)

				taxable_earnings -= flt(amount - additional_amount)
				additional_income -= additional_amount
				amount_exempted_from_income_tax = flt(amount - additional_amount)

				if additional_amount and ded.is_recurring_additional_salary:
					additional_income -= self.get_future_recurring_additional_amount(
						ded.additional_salary, ded.additional_amount
					)  # Used ded.additional_amount to consider the amount for the full month
	return frappe._dict(
		{
			"taxable_earnings": taxable_earnings,
			"additional_income": additional_income,
			"amount_exempted_from_income_tax": amount_exempted_from_income_tax,
			"additional_income_with_full_tax": additional_income_with_full_tax,
			"flexi_benefits": flexi_benefits,
		}
	)


def compute_current_and_future_taxable_earnings(self):
	# #get taxable_earnings for current period (all days)
	self.current_taxable_earnings = self.get_taxable_earnings(self.tax_slab.allow_tax_exemption)
	self.future_structured_taxable_earnings = self.current_taxable_earnings.taxable_earnings * (
		ceil(self.remaining_sub_periods) - 1
	)

	current_taxable_earnings_before_exemption = (
		self.current_taxable_earnings.taxable_earnings
		+ self.current_taxable_earnings.amount_exempted_from_income_tax
	)
	self.future_structured_taxable_earnings_before_exemption = (
		current_taxable_earnings_before_exemption * (ceil(self.remaining_sub_periods) - 1)
	)

	# get taxable_earnings, addition_earnings for current actual payment days
	self.current_taxable_earnings_for_payment_days = self.get_taxable_earnings(
		self.tax_slab.allow_tax_exemption, based_on_payment_days=1
	)

	self.current_structured_taxable_earnings = (
		self.current_taxable_earnings_for_payment_days.taxable_earnings
	)
	self.current_structured_taxable_earnings_before_exemption = (
		self.current_structured_taxable_earnings
		+ self.current_taxable_earnings_for_payment_days.amount_exempted_from_income_tax
	)

	self.current_additional_earnings = self.current_taxable_earnings_for_payment_days.additional_income
	self.current_additional_earnings_with_full_tax = (
		self.current_taxable_earnings_for_payment_days.additional_income_with_full_tax
	)
def calculate_variable_tax(self, tax_component):
		self.previous_total_paid_taxes = self.get_tax_paid_in_period(
			self.payroll_period.start_date, self.start_date, tax_component
		)

		# Structured tax amount
		eval_locals, default_data = self.get_data_for_eval()
		self.total_structured_tax_amount = calculate_tax_by_tax_slab(
			self.total_taxable_earnings_without_full_tax_addl_components,
			self.tax_slab,
			self.whitelisted_globals,
			eval_locals,
		)
		self.current_structured_tax_amount = (
			self.total_structured_tax_amount 
			# - self.previous_total_paid_taxes
		# ) / self.remaining_sub_periods
		)/12 #### Mahmoud
		# Total taxable earnings with additional earnings with full tax
		self.full_tax_on_additional_earnings = 0.0
		if self.current_additional_earnings_with_full_tax:
			self.total_tax_amount = calculate_tax_by_tax_slab(
				self.total_taxable_earnings, self.tax_slab, self.whitelisted_globals, eval_locals
			)
			self.full_tax_on_additional_earnings = self.total_tax_amount - self.total_structured_tax_amount

		current_tax_amount = self.current_structured_tax_amount + self.full_tax_on_additional_earnings
		
		if flt(current_tax_amount) < 0:
			current_tax_amount = 0

		self._component_based_variable_tax[tax_component].update(
			{
				"previous_total_paid_taxes": self.previous_total_paid_taxes,
				"total_structured_tax_amount": self.total_structured_tax_amount,
				"current_structured_tax_amount": self.current_structured_tax_amount,
				"full_tax_on_additional_earnings": self.full_tax_on_additional_earnings,
				"current_tax_amount": current_tax_amount,
			}
		)

		return current_tax_amount

def compute_taxable_earnings_for_year(self):
		# get taxable_earnings, opening_taxable_earning, paid_taxes for previous period
		self.previous_taxable_earnings, exempted_amount = self.get_taxable_earnings_for_prev_period(
			self.payroll_period.start_date, self.start_date, self.tax_slab.allow_tax_exemption
		)
		self.previous_taxable_earnings_before_exemption = self.previous_taxable_earnings + exempted_amount

		self.compute_current_and_future_taxable_earnings()
		# Deduct taxes forcefully for unsubmitted tax exemption proof and unclaimed benefits in the last period
		if self.payroll_period.end_date <= getdate(self.end_date):
			self.deduct_tax_for_unsubmitted_tax_exemption_proof = 1
			self.deduct_tax_for_unclaimed_employee_benefits = 1

		# Get taxable unclaimed benefits
		self.unclaimed_taxable_benefits = 0
		if self.deduct_tax_for_unclaimed_employee_benefits:
			self.unclaimed_taxable_benefits = self.calculate_unclaimed_taxable_benefits()

		# Total exemption amount based on tax exemption declaration
		self.total_exemption_amount = self.get_total_exemption_amount()

		# Employee Other Incomes
		self.other_incomes = self.get_income_form_other_sources() or 0.0

		# Total taxable earnings including additional and other incomes
		self.total_taxable_earnings = (
			# self.previous_taxable_earnings
			+ self.current_structured_taxable_earnings * 12 ### Mahmoud
			# + self.future_structured_taxable_earnings
			+ self.current_additional_earnings   *  12 ### Mahmoud
			+ self.other_incomes
			+ self.unclaimed_taxable_benefits
			- self.total_exemption_amount
		)

		# Total taxable earnings without additional earnings with full tax
		self.total_taxable_earnings_without_full_tax_addl_components = (
			self.total_taxable_earnings
                    # - self.current_additional_earnings_with_full_tax
		)
	
## Calculate 30 Days ###### Start

def get_working_days_details(self, lwp=None, for_preview=0):
    payroll_settings = frappe.get_cached_value(
        "Payroll Settings",
        None,
        (
            "payroll_based_on",
            "include_holidays_in_total_working_days",
            "consider_marked_attendance_on_holidays",
            "daily_wages_fraction_for_half_day",
            "consider_unmarked_attendance_as",
        ),
        as_dict=1,
    )

    consider_marked_attendance_on_holidays = (
        payroll_settings.include_holidays_in_total_working_days
        and payroll_settings.consider_marked_attendance_on_holidays
    )

    daily_wages_fraction_for_half_day = (
        flt(payroll_settings.daily_wages_fraction_for_half_day) or 0.5
    )

    working_days = 30
    if for_preview:
        self.total_working_days = working_days
        self.payment_days = working_days
        return

    holidays = self.get_holidays_for_employee(self.start_date, self.end_date)
    working_days_list = [
        add_days(getdate(self.start_date), days=day) for day in range(0, working_days)
    ]

    if not cint(payroll_settings.include_holidays_in_total_working_days):
        working_days_list = [i for i in working_days_list if i not in holidays]

        working_days -= len(holidays)
        if working_days < 0:
            frappe.throw(_("There are more holidays than working days this month."))

    if not payroll_settings.payroll_based_on:
        frappe.throw(_("Please set Payroll based on in Payroll settings"))

    if payroll_settings.payroll_based_on == "Attendance":
        actual_lwp, absent = self.calculate_lwp_ppl_and_absent_days_based_on_attendance(
            holidays, daily_wages_fraction_for_half_day, consider_marked_attendance_on_holidays
        )
        self.absent_days = absent
    else:
        actual_lwp = self.calculate_lwp_or_ppl_based_on_leave_application(
            holidays, working_days_list, daily_wages_fraction_for_half_day
        )

    if not lwp:
        lwp = actual_lwp
    elif lwp != actual_lwp:
        frappe.msgprint(
            _("Leave Without Pay does not match with approved {} records").format(
                payroll_settings.payroll_based_on
            )
        )

    self.leave_without_pay = lwp
    self.total_working_days = working_days

    payment_days = 30

    if flt(payment_days) > flt(lwp):
        self.payment_days = flt(payment_days) - flt(lwp)

        if payroll_settings.payroll_based_on == "Attendance":
            self.payment_days -= flt(absent)

        consider_unmarked_attendance_as = payroll_settings.consider_unmarked_attendance_as or "Present"

        if (
            payroll_settings.payroll_based_on == "Attendance"
            and consider_unmarked_attendance_as == "Absent"
        ):
            unmarked_days = self.get_unmarked_days(payroll_settings.include_holidays_in_total_working_days)
            self.absent_days += unmarked_days  # will be treated as absent
            self.payment_days -= unmarked_days
    else:
        self.payment_days = 0
        
### Calculate 30 Days ###### END



def calculate_tax_by_tax_slab(annual_taxable_earning, tax_slab, eval_globals=None, eval_locals=None):
	eval_locals.update({"annual_taxable_earning": annual_taxable_earning})
	tax_amount = 0
	for slab in tax_slab.slabs:
		cond = cstr(slab.condition).strip()
		if cond and not eval_tax_slab_condition(cond, eval_globals, eval_locals):
			continue
		if not slab.to_amount and annual_taxable_earning >= slab.from_amount:
			tax_amount += (annual_taxable_earning - slab.from_amount + 0.01) * slab.percent_deduction * 0.01     #### Mahmoud
			continue

		if annual_taxable_earning >= slab.from_amount and annual_taxable_earning < slab.to_amount:
			tax_amount += (annual_taxable_earning - slab.from_amount + 0.01) * slab.percent_deduction * 0.01   #### Mahmoud
		elif annual_taxable_earning >= slab.from_amount and annual_taxable_earning >= slab.to_amount:
			tax_amount += (slab.to_amount - slab.from_amount + 0.01) * slab.percent_deduction * 0.01   #### Mahmoud
	# other taxes and charges on income tax 
	for d in tax_slab.other_taxes_and_charges:
		if flt(d.min_taxable_income) and flt(d.min_taxable_income) > annual_taxable_earning:
			continue

		if flt(d.max_taxable_income) and flt(d.max_taxable_income) < annual_taxable_earning:
			continue

		tax_amount += tax_amount * flt(d.percent) / 100
	
	return tax_amount