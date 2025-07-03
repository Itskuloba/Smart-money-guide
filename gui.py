import streamlit as st
import os
import sys
import pandas as pd
from io import BytesIO

script_dir = os.path.dirname(__file__)
if script_dir not in sys.path:
    sys.path.append(script_dir)

# Importing existing modules
try:
    # from data import save_user_data, load_user_data
    from tax import calculate_net_income
    from investment import suggest_investments, get_mmf_rates # get_mmf_rates is called by suggest_investments
except ImportError as e:
    st.error(f"Error importing a module. Please ensure all files are in the same directory as this app. Details: {e}")
    st.stop() # Stop the app if modules can't be imported

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="The Smart Money Guide",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Initialization (Consolidated and Safe) ---
# Initialize all necessary session state variables here
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        "name": "",
        "monthly_gross_salary": 0.0,
        "fixed_monthly_expenses": {},
        "savings_goals": {"target_amount": 0.0, "timeframe_months": 12},
    }
if 'expense_rows' not in st.session_state:
    st.session_state.expense_rows = [
        {"category": "Rent", "amount": 0.0},
        {"category": "Utilities", "amount": 0.0},
        {"category": "Food", "amount": 0.0}, 
        {"category": "Transport", "amount": 0.0},
        # {"category": "Other", "amount": 0.0}, # Re-added Other
    ]
if 'financial_breakdown' not in st.session_state:
    st.session_state.financial_breakdown = None
if 'investment_suggestions' not in st.session_state:
    st.session_state.investment_suggestions = []

USERNAME_INPUT_KEY = "user_name_input_sidebar" # Define the constant for the key

# Initialize the specific widget keys if they're not already set by a previous run/load
if USERNAME_INPUT_KEY not in st.session_state:
    st.session_state[USERNAME_INPUT_KEY] = st.session_state.user_data.get("name", "")

# if "user_data" not in st.session_state or not isinstance(st.session_state.user_data, dict):
#     st.session_state.user_data = {
#         "monthly_gross_salary": 0.0,
#         "fixed_monthly_expenses": {},
#         "savings_goals": {"target_amount": 0.0, "timeframe_months": 12},
#         "name": ""
#     }
if 'salary_input' not in st.session_state:
    st.session_state.salary_input = st.session_state.user_data.get("monthly_gross_salary", 0.0)
if 'savings_goal_amount_input' not in st.session_state:
    st.session_state.savings_goal_amount_input = st.session_state.user_data.get("savings_goals", {}).get("target_amount", 0.0)
if 'savings_goal_timeframe_input' not in st.session_state:
    st.session_state.savings_goal_timeframe_input = st.session_state.user_data.get("savings_goals", {}).get("timeframe_months", 12)

# import logging
# logging.basicConfig(filename='app.log', level=logging.DEBUG)
# with st.sidebar:
#     logging.debug("Rendering text_input with key=user_name_input_sidebar")
#     st.text_input(
#         "Your Name:",
#         value=st.session_state.user_data.get("name", ""),
#         key=USERNAME_INPUT_KEY
#     )
# --- Helper Functions for Streamlit UI ---

def get_inputs_from_ui():
    # user_name = st.session_state.user_name_input.strip()
    # user_name = st.session_state.get("user_name_input_main", "").strip()
    user_name = st.session_state.get(USERNAME_INPUT_KEY, "").strip()

    if not user_name:
        st.error("Please enter your name.")
        return None

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

    try:
        savings_goal_amount = float(st.session_state.savings_goal_amount_input)
        if savings_goal_amount < 0: raise ValueError("Savings goal cannot be negative.")
    except (ValueError, KeyError):
        st.error("Please enter a valid number for Target Investment Goal.") # Changed from Savings to Investment
        return None
    
    try:
        savings_goal_timeframe_months = int(st.session_state.savings_goal_timeframe_input)
        if savings_goal_timeframe_months < 1: raise ValueError("Timeframe must be at least 1 month.")
    except (ValueError, KeyError):
        st.error("Please enter a valid whole number (months) for Timeframe.")
        return None

    return {
        "name": user_name,
        "monthly_gross_salary": salary,
        "fixed_monthly_expenses": expenses,
        "savings_goals": {
            "target_amount": savings_goal_amount,
            "timeframe_months": savings_goal_timeframe_months
        },
    }

def set_inputs_to_ui(data):
    if not data or not isinstance(data, dict):
        return
    
    st.session_state.user_name_input = data.get("name", "")
    st.session_state.salary_input = data.get("monthly_gross_salary", 0.0)

    # Clear and re-populate expense rows in session state
    st.session_state.expense_rows = []
    fixed_expenses_loaded = data.get("fixed_monthly_expenses", {})
    for category, amount in fixed_expenses_loaded.items():
        st.session_state.expense_rows.append({"category": category, "amount": amount})
    
    # Ensure at least one blank row if no expenses are loaded
    if not st.session_state.expense_rows:
        st.session_state.expense_rows.append({"category": "", "amount": 0.0})

    savings_goals = data.get("savings_goals", {})
    st.session_state.savings_goal_amount_input = savings_goals.get("target_amount", 0.0)
    st.session_state.savings_goal_timeframe_input = savings_goals.get("timeframe_months", 12)
    st.session_state.risk_tolerance_radio = data.get("risk_tolerance", "low") # Populate risk tolerance

def add_expense_row_st():
    st.session_state.expense_rows.append({"category": "", "amount": 0.0})

def remove_expense_row_st(index):
    if len(st.session_state.expense_rows) > 1: # Always keep at least one row
        st.session_state.expense_rows.pop(index)
    else:
        st.warning("Cannot remove the last expense row.")

def calculate_and_suggest_st():
   
    st.session_state.user_data = get_inputs_from_ui()
    if not st.session_state.user_data: # If input validation failed
        return

    gross_salary = st.session_state.user_data["monthly_gross_salary"]
    fixed_expenses = st.session_state.user_data["fixed_monthly_expenses"]
    savings_goals = st.session_state.user_data["savings_goals"]

    try:
        financial_breakdown = calculate_net_income(gross_salary, fixed_expenses)
        st.session_state.financial_breakdown = financial_breakdown # Store in session state
    except Exception as e:
        st.error(f"An error occurred during financial calculation: {e}")
        st.session_state.financial_breakdown = None
        return

    try:
       
        investment_suggestions = suggest_investments(
        remaining_funds=financial_breakdown['remaining_for_savings_investment'],
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
        # "url": best.get("url", "#")
    }

def generate_excel_report(financial_breakdown, investment_suggestions, user_data):
    if not financial_breakdown:
        return None

    # Prepare data for financial breakdown
    breakdown_data = {
        "Category": [
            "Gross Salary",
            "PAYE Tax",
            "SHA Deduction", 
            "NSSF Deduction",
            "Total Statutory Deductions",
            "Net Salary (After Tax & Deductions)",
            "Total Fixed Expenses",
            "Remaining for Savings & Investment"
        ],
        "Amount (KES)": [
            financial_breakdown['gross_salary'],
            financial_breakdown['paye_tax'],
            financial_breakdown.get("sha_deduction", 0),
            financial_breakdown['nssf_deduction'],
            financial_breakdown['total_statutory_deductions'],
            financial_breakdown['net_salary_after_tax'],
            financial_breakdown['total_fixed_expenses'],
            financial_breakdown['remaining_for_savings_investment']
        ]
    }

    # Add detailed fixed expenses
    for category, amount in user_data.get("fixed_monthly_expenses", {}).items():
        breakdown_data["Category"].insert(6, f"  - {category} (Fixed Expense)")
        breakdown_data["Amount (KES)"].insert(6, amount)

    df_breakdown = pd.DataFrame(breakdown_data)

    # Prepare data for investment suggestions
    suggestion_texts = []

    for suggestion in investment_suggestions:
        if suggestion["type"] == "header":
            suggestion_texts.append(f"== {suggestion['message']} ==")
        elif suggestion["type"] == "info":
            suggestion_texts.append(f"[INFO] {suggestion['message']}")
        elif suggestion["type"] == "warning":
            suggestion_texts.append(f"[WARNING] {suggestion['message']}")
        elif suggestion["type"] == "error":
            suggestion_texts.append(f"[ERROR] {suggestion['message']}")
        elif suggestion["type"] == "mmf":
            suggestion_texts.append(
                f"{suggestion['name']} - Rate: {suggestion['rate']*100:.2f}%, "
                f"Projected Return: KES {suggestion['projected_return']:,.2f}"
            )
        elif suggestion["type"] == "highlight":
            suggestion_texts.append(f"💡 {suggestion['message']}")

    # ✅ Move this outside the loop to always define it
    df_suggestions = pd.DataFrame({"Investment Suggestions": suggestion_texts})

    # Create an in-memory Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        start_row_breakdown = 0
        if user_data.get("name"):
            df_name = pd.DataFrame([{"Report for": f"Report for: {user_data['name']}"}])
            df_name.to_excel(writer, sheet_name='Financial Breakdown', index=False, header=False, startrow=0)
            start_row_breakdown = 2

        df_breakdown.to_excel(writer, sheet_name='Financial Breakdown', index=False, startrow=start_row_breakdown)
        df_suggestions.to_excel(writer, sheet_name='Investment Suggestions', index=False)

    output.seek(0)
    return output


# Streamlit UI Layout 

st.title("💰 The Smart Money Guide")
st.markdown("A tool to help you understand your finances and explore investment options.")

# Input Section
with st.sidebar:
    st.header("Your Financial Inputs")

    st.text_input(
         "Your Name:",
         value=st.session_state.user_data.get("name", ""),
         key=USERNAME_INPUT_KEY
    )


    # Salary Input
    st.number_input(
        "Monthly Gross Salary (KES):", 
        min_value=0.0, 
        # value=st.session_state.user_data.get("monthly_gross_salary", 0.0),
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
        "Target Investment Goal (KES):", 
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


# Main Area
st.header("Your Financial Breakdown & Investment Suggestions")

if 'user_data' in st.session_state and st.session_state.user_data.get("name"):
    st.markdown(f" Hello, **{st.session_state.user_data['name']}**! Here's your financial overview:")

if 'financial_breakdown' in st.session_state and st.session_state.financial_breakdown:
    financial_breakdown = st.session_state.financial_breakdown
    st.subheader("Monthly Financial Breakdown")
    st.write(f"**Gross Salary:** KES {financial_breakdown['gross_salary']:,.2f}")
    st.write(f"**PAYE Tax:** KES {financial_breakdown['paye_tax']:,.2f}")
    st.write(f"**SHA Deduction:** KES {financial_breakdown.get('sha_deducti', 0):,.2f}") # Use .get for safety
    st.write(f"**NSSF Deduction:** KES {financial_breakdown['nssf_deduction']:,.2f}")
    st.write(f"**Total Statutory Deductions:** KES {financial_breakdown['total_statutory_deductions']:,.2f}")
    st.write(f"---")
    st.write(f"**Net Salary (After Tax & Deductions):** KES {financial_breakdown['net_salary_after_tax']:,.2f}")
    
    st.subheader("Fixed Expenses")
    fixed_expenses_display = ""

    for category, amount in st.session_state.user_data.get("fixed_monthly_expenses", {}).items():
        fixed_expenses_display += f"- {category}: KES {amount:,.2f}\n"
    st.markdown(fixed_expenses_display)
    st.write(f"**Total Fixed Expenses:** KES {financial_breakdown['total_fixed_expenses']:,.2f}")

    st.markdown("---")
    st.success(f"**Remaining for Savings & Investment:** KES {financial_breakdown['remaining_for_savings_investment']:,.2f}")

    #  Download Excel Report Button 
    excel_data = generate_excel_report(
        st.session_state.financial_breakdown,
        st.session_state.investment_suggestions,
        st.session_state.user_data
    )
    

    if excel_data:
        st.markdown("### 📥 Download Your Full Report as Excel")
        st.download_button(
            label="📊 Download Excel Report",
            data=excel_data,
            file_name="smart_money_guide_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel_report_main_unique" 
        )

if 'investment_suggestions' in st.session_state and st.session_state.investment_suggestions:
    st.subheader("Investment Suggestions")
    # Iterate through suggestions and display based on their 'type'
    for suggestion in st.session_state.investment_suggestions:
        if isinstance(suggestion, str): # Handle old string-based suggestions if any
            if suggestion.startswith("--- DISCLAIMER ---"):
                st.warning(suggestion)
            else:
                st.markdown(suggestion)
        elif isinstance(suggestion, dict): # Handle dictionary-based suggestions
            if suggestion.get("type") == "header":
                st.subheader(suggestion["message"])
            elif suggestion.get("type") == "info":
                st.info(suggestion["message"])
            elif suggestion.get("type") == "warning":
                st.warning(suggestion["message"])
            elif suggestion.get("type") == "error":
                st.error(suggestion["message"])
            elif suggestion.get("type") == "mmf":
                st.markdown(f"### 💼 {suggestion['name']}")
                st.write(f"**Annual Rate:** {suggestion['rate']:.2f}%")
                timeframe = st.session_state.user_data.get("savings_goals", {}).get("timeframe_months", 12)
                st.write(f"**Total Deposits (Over {timeframe} months):** KES {suggestion['total_deposits']:,.2f}")
                st.write(f"**Interest Earned:** KES {suggestion['interest_earned']:,.2f}")
                st.success(f"**Total Projected Return:** KES {suggestion['projected_return']:,.2f}")
                # if suggestion.get("url"):
                #     st.markdown(f"[👉 Visit Website]({suggestion['url']})", unsafe_allow_html=True)
            elif suggestion.get("type") == "highlight":
                st.success(suggestion["message"])

