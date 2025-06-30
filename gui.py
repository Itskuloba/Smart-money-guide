import streamlit as st
import os
import sys
import pandas as pd
from io import BytesIO
import streamlit as st

script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Import your existing modules
try:
    from data import save_user_data, load_user_data
    from tax import calculate_net_income
    from investment import suggest_investments, get_mmf_rates # get_mmf_rates is called by suggest_investments
except ImportError as e:
    st.error(f"Error importing a module. Please ensure all backend files (data_manager.py, tax_calculation_module.py, investment_module.py) are in the same directory as this app. Details: {e}")
    st.stop() # Stop the app if modules can't be imported

# Streamlit Page Configuration 
def main():
 st.set_page_config(
    page_title="The Smart Money Guide",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
 )

#  Session State Initialization 
# Initialize session state variables if they don't exist
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        "monthly_gross_salary": 0.0,
        "fixed_monthly_expenses": {},
        "savings_goals": {"target_amount": 0.0, "timeframe_months": 12},
        # "risk_tolerance": "low"
    }
if 'expense_rows' not in st.session_state:
    # Start with a few default expense rows
    st.session_state.expense_rows = [
        {"category": "Rent", "amount": 0.0},
        {"category": "Utilities", "amount": 0.0},
        # {"category": "Food", "amount": 0.0},
        {"category": "Transport", "amount": 0.0},
        # {"category": "Other", "amount": 0.0},
    ]
# Initialize session state variables safely
if 'investment_suggestions' not in st.session_state:
    st.session_state.investment_suggestions = []

# --- Helper Functions for Streamlit UI ---
def get_inputs_from_ui():

    try:
        salary = float(st.session_state.salary_input)
        if salary < 0: raise ValueError("Salary cannot be negative.")
    except (ValueError, KeyError):
        st.error("Please enter a valid number for Monthly Gross Salary.")
        return None

    expenses = {}
    for i, row in enumerate(st.session_state.expense_rows):
        category_key = f"expense_category_{i}"
        amount_key = f"expense_amount_{i}"
        category = st.session_state[category_key].strip()
        
        if not category:
            st.error(f"Expense category for row {i+1} cannot be empty.")
            return None
        try:
            amount = float(st.session_state[amount_key])
            if amount < 0: raise ValueError("Expense amount cannot be negative.")
            expenses[category] = amount
        except (ValueError, KeyError):
            st.error(f"Please enter a valid number for expense '{category}' (row {i+1}).")
            return None
    
    name = st.session_state.get("name_input", "").strip()
    if not name:
        st.error("Please enter your name.")
        return None

    try:
        savings_goal_amount = float(st.session_state.savings_goal_amount_input)
        if savings_goal_amount < 0: raise ValueError("Savings goal cannot be negative.")
    except (ValueError, KeyError):
        st.error("Please enter a valid number for Target Savings Goal.")
        return None
    
    try:
        savings_goal_timeframe_months = int(st.session_state.savings_goal_timeframe_input)
        if savings_goal_timeframe_months < 1: raise ValueError("Timeframe must be at least 1 month.")
    except (ValueError, KeyError):
        st.error("Please enter a valid whole number (months) for Timeframe.")
        return None

    return {
        "name": name,
        "monthly_gross_salary": salary,
        "fixed_monthly_expenses": expenses,
        "savings_goals": {
            "target_amount": savings_goal_amount,
            "timeframe_months": savings_goal_timeframe_months
        }
    }

def set_inputs_to_ui(data):

    if not data:
        return
    
    st.session_state.name_input = data.get("name", "")
    st.session_state.salary_input = data.get("monthly_gross_salary", 0.0)

    # Clear and re-populate expense rows
    st.session_state.expense_rows = []
    fixed_expenses_loaded = data.get("fixed_monthly_expenses", {})
    for category, amount in fixed_expenses_loaded.items():
        st.session_state.expense_rows.append({"category": category, "amount": amount})
    
    # If no expenses loaded, ensure at least one blank row is available
    if not st.session_state.expense_rows:
        st.session_state.expense_rows.append({"category": "", "amount": 0.0})

    savings_goals = data.get("savings_goals", {})
    st.session_state.savings_goal_amount_input = savings_goals.get("target_amount", 0.0)
    st.session_state.savings_goal_timeframe_input = savings_goals.get("timeframe_months", 12)
    # st.session_state.risk_tolerance_radio = data.get("risk_tolerance", "low")

def add_expense_row_st():

    st.session_state.expense_rows.append({"category": "", "amount": 0.0})

def remove_expense_row_st(index):

    if len(st.session_state.expense_rows) > 1: # Always keep at least one row
        st.session_state.expense_rows.pop(index)
    else:
        st.warning("Cannot remove the last expense row.")

# def save_data_st():

#     data_to_save = get_inputs_from_ui()
#     if data_to_save:
#         save_user_data(data_to_save)
#         st.success("Your financial data has been saved successfully!")
#         st.session_state.user_data = data_to_save # Update session state

# def load_data_st():
#     # loaded_data = load_user_data()
#     # if loaded_data:
#     #     set_inputs_to_ui(loaded_data)
#     #     st.session_state.user_data = loaded_data # Update session state
#     #     st.success("Your financial data has been loaded successfully!")
#     #     # Rerun to apply loaded values to inputs
#     #     st.rerun() 
#     # else:
#     #     st.info("No existing data found to load. Please enter new data.")
#     loaded_data = load_user_data()
#     if loaded_data:
#         set_inputs_to_ui(loaded_data)
#         st.session_state.user_data = loaded_data
#         st.session_state.needs_rerun = True  # Set the flag
#         st.success("Your financial data has been loaded successfully!")
#     else:
#         st.info("No existing data found to load.")

def calculate_and_suggest_st():
    
    st.session_state.user_data = get_inputs_from_ui()
    if not st.session_state.user_data: # If input validation failed
        return

    gross_salary = st.session_state.user_data["monthly_gross_salary"]
    fixed_expenses = st.session_state.user_data["fixed_monthly_expenses"]
    savings_goals = st.session_state.user_data["savings_goals"]

    # Part 2: Financial Calculations and Deductions
    try:
        financial_breakdown = calculate_net_income(gross_salary, fixed_expenses)
        st.session_state.financial_breakdown = financial_breakdown # Store in session state
    except Exception as e:
        st.error(f"An error occurred during financial calculation: {e}")
        st.session_state.financial_breakdown = None
        return

    # Part 3: Investment Recommendations
    try:
        investment_suggestions = suggest_investments(
            financial_breakdown['remaining_for_savings_investment'],
            # risk_tolerance,
            savings_goal_amount=savings_goals.get("target_amount", 0),
            savings_goal_timeframe_months=savings_goals.get("timeframe_months", 1)
        )
        st.session_state.investment_suggestions = investment_suggestions # Store in session state
    except Exception as e:
        st.error(f"An error occurred while getting investment suggestions: {e}")
        st.session_state.investment_suggestions = []
        return
    
    st.success("Calculations complete! See your breakdown below.")

def suggest_best_mmf(top_mmfs):
    
    if not top_mmfs:
        return {"type": "error", "message": "No MMF data available to make a recommendation."}

    best = top_mmfs[0]

    return {
        "type": "highlight",
        "message": (
            f"✅ **Top Recommendation:** {best['name']} "
            f"with an annual rate of **{best['rate'] * 100:.2f}%**.\n\n"
            f"You'll earn approximately **KES {best['interest_earned']:,.2f}** "
            f"in interest over your savings period, bringing your total to "
            f"**KES {best['projected_return']:,.2f}**."
        ),
        "url": best.get("url", "#")
    }

def generate_excel(user_data: dict, investment_data: list) -> bytes:
    # Financial Summary
    salary_data = {
        "Description": [
            "Gross Salary",
            "PAYE",
            "NSSF",
            "SHA",
            "Net Salary"
        ],
        "Amount (KES)": [
            user_data.get("monthly_gross_salary", 0),
            st.session_state.get("financial_breakdown", {}).get("paye_tax", 0),
            st.session_state.get("financial_breakdown", {}).get("nssf_deduction", 0),
            st.session_state.get("financial_breakdown", {}).get("sha_deduction", 0),
            st.session_state.get("financial_breakdown", {}).get("net_salary_after_tax", 0),
        ]
    }
    salary_df = pd.DataFrame(salary_data)

    # Expenses
    expenses_df = pd.DataFrame(
        list(user_data.get("fixed_monthly_expenses", {}).items()),
        columns=["Category", "Amount (KES)"]
    )

    # Savings Goals
    goals = user_data.get("savings_goals", {})
    goals_df = pd.DataFrame.from_dict({
        "Target Savings Goal (KES)": [goals.get("target_amount", 0)],
        "Timeframe (Months)": [goals.get("timeframe_months", 0)]
    })

    # Investment Suggestions
    mmfs = []
    for entry in investment_data:
        if entry.get("type") == "mmf":
            mmfs.append({
                "Fund Name": entry["name"],
                "Rate (%)": entry["rate"],
                "Projected Return (KES)": round(entry["projected_return"], 2),
                # "Website": entry["url"]
            })

    mmf_df = pd.DataFrame(mmfs)

    # Write to Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        salary_df.to_excel(writer, index=False, sheet_name="Salary Summary")
        expenses_df.to_excel(writer, index=False, sheet_name="Expenses")
        goals_df.to_excel(writer, index=False, sheet_name="Savings Goal")
        if not mmf_df.empty:
            mmf_df.to_excel(writer, index=False, sheet_name="MMF Suggestions")

    return output.getvalue()

#  Streamlit Button to Download Excel 
if 'user_data' in st.session_state and 'investment_suggestions' in st.session_state:
    st.markdown("### Download Your Full Report as Excel")
    excel_bytes = generate_excel(st.session_state.user_data, st.session_state.investment_suggestions)
    st.download_button(
        label="📊 Download Excel Report",
        data=excel_bytes,
        file_name="smart_money_guide_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_excel_report"
    )

# Streamlit UI Layout 

st.title("💰 The Smart Money Guide")
st.markdown("A tool to help you understand your finances and explore investment options.")

#  Input Section 
with st.sidebar:
    st.header("Your Financial Inputs")

    st.text_input(
        "Your Name:",
        value=st.session_state.user_data.get("name", ""),
        key="name_input"
    )

    # Salary Input
    st.number_input(
        "Monthly Gross Salary (KES):", 
        min_value=0.0, 
        value=st.session_state.user_data.get("monthly_gross_salary", 0.0),
        key="salary_input",
        format="%.2f"
    )

    st.subheader("Fixed Monthly Expenses:")
    # Dynamic expense entries
    for i, row in enumerate(st.session_state.expense_rows):
        cols = st.columns([0.6, 0.3, 0.1])
        with cols[0]:
            st.text_input(f"Category {i+1}:", value=row["category"], key=f"expense_category_{i}", label_visibility="collapsed")
        with cols[1]:
            st.number_input(f"Amount {i+1}:", min_value=0.0, value=row["amount"], key=f"expense_amount_{i}", format="%.2f", label_visibility="collapsed")
        with cols[2]:
            st.button("❌", key=f"remove_btn_{i}", on_click=remove_expense_row_st, args=(i,))

    st.button("➕ Add Another Expense", on_click=add_expense_row_st)

    st.subheader("Savings Goals:")
    st.number_input(
        "Target Savings Goal (KES):", 
        min_value=0.0, 
        value=st.session_state.user_data.get("savings_goals", {}).get("target_amount", 0.0),
        key="savings_goal_amount_input",
        format="%.2f"
    )
    st.number_input(
        "Timeframe (Months):", 
        min_value=1, 
        value=st.session_state.user_data.get("savings_goals", {}).get("timeframe_months", 12),
        key="savings_goal_timeframe_input",
        format="%d"
    )

    st.markdown("---")
    st.button("Calculate & Get Suggestions", on_click=calculate_and_suggest_st, type="primary")
    # st.button("Save Data", on_click=save_data_st)
    # st.button("Load Data", on_click=load_data_st)

# Output Section
st.header("Your Financial Breakdown & Investment Suggestions")

if 'user_data' in st.session_state and st.session_state.user_data.get("name"):
    st.markdown(f"👋 Hello, **{st.session_state.user_data['name']}**! Here's your financial overview:")

if 'financial_breakdown' in st.session_state and st.session_state.financial_breakdown:
    financial_breakdown = st.session_state.financial_breakdown
    st.subheader("Monthly Financial Breakdown")
    st.write(f"**Gross Salary:** KES {financial_breakdown['gross_salary']:,.2f}")
    st.write(f"**PAYE Tax:** KES {financial_breakdown['paye_tax']:,.2f}")
    st.write(f"**SHA Deduction:** KES {financial_breakdown['sha_deduction']:,.2f}")
    st.write(f"**NSSF Deduction:** KES {financial_breakdown['nssf_deduction']:,.2f}")
    st.write(f"**Total Statutory Deductions:** KES {financial_breakdown['total_statutory_deductions']:,.2f}")
    st.write(f"---")
    st.write(f"**Net Salary (After Tax & Deductions):** KES {financial_breakdown['net_salary_after_tax']:,.2f}")
    
    st.subheader("Fixed Expenses")
    fixed_expenses_display = ""
    # st.session_state.user_data for expenses to show what user actually entered
    for category, amount in st.session_state.user_data.get("fixed_monthly_expenses", {}).items():
        fixed_expenses_display += f"- {category}: KES {amount:,.2f}\n"
    st.markdown(fixed_expenses_display)
    st.write(f"**Total Fixed Expenses:** KES {financial_breakdown['total_fixed_expenses']:,.2f}")

    st.markdown("---")
    st.success(f"**Remaining for Savings & Investment:** KES {financial_breakdown['remaining_for_savings_investment']:,.2f}")

if 'investment_suggestions' in st.session_state:
    for suggestion in st.session_state.investment_suggestions:
        if suggestion["type"] == "header":
            st.subheader(suggestion["message"])

        elif suggestion["type"] == "info":
            st.info(suggestion["message"])

        elif suggestion["type"] == "warning":
            st.warning(suggestion["message"])

        elif suggestion["type"] == "error":
            st.error(suggestion["message"])

        elif suggestion["type"] == "mmf":
            st.markdown(f"### 💼 {suggestion['name']}")
            st.write(f"**Annual Rate:** {suggestion['rate']:.2f}%")
            timeframe = st.session_state.user_data.get("savings_goals", {}).get("timeframe_months", 12)
            st.write(f"**Total Deposits (Over {timeframe} months):** KES {suggestion['total_deposits']:,.2f}")
            st.write(f"**Interest Earned:** KES {suggestion['interest_earned']:,.2f}")
            st.success(f"**Total Projected Return:** KES {suggestion['projected_return']:,.2f}")
            # st.markdown(f"[👉 Visit Website]({suggestion['url']})", unsafe_allow_html=True)

for suggestion in st.session_state.investment_suggestions:
    if suggestion["type"] == "highlight":
        st.success(suggestion["message"])

if st.session_state.get("needs_rerun", False):
    st.session_state.needs_rerun = False  # Reset the flag
    st.rerun()

if __name__ == "__main__":
    main()