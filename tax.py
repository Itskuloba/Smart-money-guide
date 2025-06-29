def calculate_kra_paye(gross_salary):
    
    tax_payable = 0.0
    personal_relief = 2400 # monthly personal relief

    # Simplified KRA PAYE Brackets
    # Tier 1: First KES 24,000 @ 10%
    # Tier 2: Next KES 16,667 (24001-32333) @ 25%
    # Tier 3: Next KES 16,666 (32334-500000) @ 30%
    # Tier 4: Next KES 16,666 (500001-800000) @ 32.5%
    # Tier 5: Above KES 800,000 @ 35%

    if gross_salary <= 24000:
        tax_payable = gross_salary * 0.10
    elif gross_salary <= 32333:
        tax_payable = (24000 * 0.10) + ((gross_salary - 24000) * 0.25)
    elif gross_salary <= 500000:
        tax_payable = (24000 * 0.10) + (8333 * 0.25) + ((gross_salary - 32333) * 0.30)
    elif gross_salary <= 800000:
        tax_payable = (24000 * 0.10) + (8333 * 0.25) + (467667 * 0.30) + ((gross_salary - 500000) * 0.325)
    else:
        tax_payable = (24000 * 0.10) + (8333 * 0.25) + (467667 * 0.30) + (300000 * 0.325) + ((gross_salary - 800000) * 0.35)


    # Deduct personal relief
    net_tax_after_relief = max(0, tax_payable - personal_relief) # Ensure tax doesn't go negative

    # SHA (Social Health Authority) 
    sha = 0
    if gross_salary <= 5999: sha = 150
    elif gross_salary <= 7999: sha = 300
    elif gross_salary <= 11999: sha = 400
    elif gross_salary <= 14999: sha = 500
    elif gross_salary <= 19999: sha = 600
    elif gross_salary <= 24999: sha = 750
    elif gross_salary <= 29999: sha = 850
    elif gross_salary <= 34999: sha = 900
    elif gross_salary <= 39999: sha = 950
    elif gross_salary <= 44999: sha = 1000
    elif gross_salary <= 49999: sha = 1100
    elif gross_salary <= 59999: sha = 1200
    elif gross_salary <= 69999: sha = 1300
    elif gross_salary <= 79999: sha = 1400
    elif gross_salary <= 89999: sha = 1500
    elif gross_salary <= 99999: sha = 1600
    else: sha = 1700 

    # Tiered NSSF rates.
    nssf_upper_limit_tier1 = 7000 # Max for Tier I
    nssf_upper_limit_tier2 = 36000 # Max for Tier II 
    nssf_rate = 0.06 # 6% for both employee and employer

    nssf_employee_contribution = min(gross_salary * nssf_rate, nssf_upper_limit_tier1 * nssf_rate) # Simplified Tier I
    nssf_employee_contribution = min(gross_salary * nssf_rate, nssf_upper_limit_tier2 * nssf_rate) #Tier II
    
    total_deductions = net_tax_after_relief + sha + nssf_employee_contribution
    
    return {
        "paye_tax": net_tax_after_relief,
        "sha": sha,
        "nssf": nssf_employee_contribution,
        "total_statutory_deductions": total_deductions
    }

def calculate_net_income(gross_salary, fixed_expenses_dict):
   
    statutory_deductions = calculate_kra_paye(gross_salary)
    total_tax_and_deductions = statutory_deductions["total_statutory_deductions"]

    total_fixed_expenses = sum(fixed_expenses_dict.values())

    net_income_after_tax = gross_salary - total_tax_and_deductions
    remaining_for_savings_investment = net_income_after_tax - total_fixed_expenses

    return {
        "gross_salary": gross_salary,
        "paye_tax": statutory_deductions["paye_tax"],
        "sha_deduction": statutory_deductions["sha"],
        "nssf_deduction": statutory_deductions["nssf"],
        "total_statutory_deductions": total_tax_and_deductions,
        "net_salary_after_tax": net_income_after_tax,
        "total_fixed_expenses": total_fixed_expenses,
        "remaining_for_savings_investment": remaining_for_savings_investment
    }