import sys
from data import collect_user_data
from tax import calculate_net_income
from investment import suggest_investments
from investment import get_mmf_rates
from investment import calculate_mmf_return


def main():
    
    print("Welcome to The Smart Money Guide!")

    # User Input and Data Collection
    user_financial_data = collect_user_data()
    if not user_financial_data:
        print("Failed to collect user data. Exiting.")
        return

    gross_salary = user_financial_data.get("monthly_gross_salary", 0)
    fixed_expenses = user_financial_data.get("fixed_monthly_expenses", {})
    savings_goals = user_financial_data.get("savings_goals", {})
    #risk_tolerance = user_financial_data.get("risk_tolerance", "low")

    # Financial Calculations and Deductions
    financial_breakdown = calculate_net_income(gross_salary, fixed_expenses)

    print("\n--- Your Monthly Financial Breakdown ---")
    print(f"Gross Salary: KES {financial_breakdown['gross_salary']:,.2f}")
    print(f"PAYE Tax: KES {financial_breakdown['paye_tax']:,.2f}")
    print(f"Sha Deduction: KES {financial_breakdown['sha_deduction']:,.2f}")
    print(f"NSSF Deduction: KES {financial_breakdown['nssf_deduction']:,.2f}")
    print(f"Total Statutory Deductions: KES {financial_breakdown['total_statutory_deductions']:,.2f}")
    print(f"Net Salary (After Tax & Deductions): KES {financial_breakdown['net_salary_after_tax']:,.2f}")
    
    print("\nFixed Expenses:")
    for category, amount in fixed_expenses.items():
        print(f"  {category}: KES {amount:,.2f}")
    print(f"Total Fixed Expenses: KES {financial_breakdown['total_fixed_expenses']:,.2f}")

    remaining_funds = financial_breakdown['remaining_for_savings_investment']
    print(f"\nRemaining for Savings & Investment: KES {remaining_funds:,.2f}")

    # Part 3: Investment Recommendations
    investment_suggestions = suggest_investments(
        remaining_funds = remaining_funds, 
        savings_goal_amount=savings_goals.get("target_amount", 0),
        savings_goal_timeframe_months=savings_goals.get("timeframe_months", 1)
    )

    rates = get_mmf_rates()
    for fund in rates:
        print(f"{fund['name']}: {fund['rate']}")

    for suggestion in investment_suggestions:
        print(suggestion)

    print("\nThank you for using The Smart Money Guide!")

if __name__ == "__main__":
    main()