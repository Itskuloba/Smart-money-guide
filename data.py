import json
import os

def collect_user_data():
    
    user_data = load_user_data()

    if user_data:
        print("\nExisting data found. Would you like to use it or start fresh?")
        choice = input("Enter 'load' to use existing data or 'new' to enter new data: ").lower().strip()
        if choice == 'load':
            return user_data
        
    print("Smart Money Guide")

    name = input("Enter your name: ").strip()
    salary = get_numeric_input("Enter your monthly gross salary (KES): ")

    expenses = {}
    print("Enter your total fixed monthly expenses (enter 'done' when finished):")
    while True:
        category = input("Expense category (e.g., Rent, Utilities, Transport, 'done'): ").strip()
        if category.lower() == 'done':
            break
        if not category:
            print("Expense category cannot be empty.")
            continue
        amount = get_numeric_input(f"Amount for {category}: ", min_value=0)
        expenses[category] = amount

    print(" Savings Goals")
    savings_goal_amount = get_numeric_input("Enter your target savings goal amount (e.g., 500000 KES): ", min_value=0)
    savings_goal_timeframe_months = get_numeric_input("Enter the timeframe for your savings goal in months: ", min_value=1)


    # Consolidate all collected data
    new_data = {
        "name": name,
        "monthly_gross_salary": salary,
        "fixed_monthly_expenses": expenses,
        "savings_goals": {
            "target_amount": savings_goal_amount,
            "timeframe_months": savings_goal_timeframe_months
        }
    }
    
    save_user_data(new_data) # Saves the newly entered data
    return new_data

def load_user_data(filename="user_data.json"):
    
    if not os.path.exists(filename):
        print(f"No existing user data found at {filename}.")
        return None
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        print(f"User data loaded successfully from {filename}")
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filename}: {e}. File might be corrupted.")
        return None
    except IOError as e:
        print(f"Error loading data: {e}")
        return None

def get_numeric_input(prompt, min_value=0):
   
    while True:
        try:
            value = float(input(prompt))
            if value < min_value:
                print(f"Please enter a value greater than or equal to {min_value}.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def save_user_data(data, filename="user_data.json"):
    
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"User data saved successfully to {filename}")
    except IOError as e:
        print(f"Error saving data: {e}")

# def get_risk_tolerance():
   
#     while True:
#         risk = input("Enter your risk tolerance (low, medium, high): ").lower().strip()
#         if risk in ['low', 'medium', 'high']:
#             return risk
#         else:
#             print("Invalid input. Please choose 'low', 'medium', or 'high'.")

if __name__ == "__main__":
    user_profile = collect_user_data()

    print("\n--- Summary of Collected Data ---")
    print(json.dumps(user_profile, indent=4))