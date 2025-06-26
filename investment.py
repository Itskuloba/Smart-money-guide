
import requests
from bs4 import BeautifulSoup

def get_mmf_rates():
    
    mmf_rates = []
    url = "https://money.ke/mmf-rates/" 

    try:
        response = requests.get(url) 
        response.raise_for_status() 
        soup = BeautifulSoup(response.content, "html.parser")

        rows = soup.find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            if len(columns) >= 3:
                name = columns[0].text.strip()  # class="column-1" — Fund Name
                rate = columns[2].text.strip()  # likely class="column-2" — Rate
                mmf_rates.append({"name": name, "rate": rate})

      
        print(f"Attempting to scrape MMF rates from {url}...")
        

    except requests.exceptions.RequestException as e:
        print(f"Network or request error retrieving MMF rates: {e}")
        mmf_rates = [{"name": "Error", "rate": f"Could not fetch MMF rates: {e}"}]
    except Exception as e:
        print(f"An unexpected error occurred during MMF scraping: {e}")
        mmf_rates = [{"name": "Error", "rate": f"Could not fetch MMF rates: {e}"}]
    
    return mmf_rates


def suggest_investments(remaining_funds, savings_goal_amount=0, savings_goal_timeframe_months=1):
    
    suggestions = []
    

    if remaining_funds <= 0:
        suggestions.append("\nNo funds available for investment after expenses.")
        return suggestions

    suggestions.append(f"\nYou have KES {remaining_funds:,.2f} remaining for savings and investment this month.")
    
    if savings_goal_amount > 0 and savings_goal_timeframe_months > 0:
        monthly_saving_needed = savings_goal_amount / savings_goal_timeframe_months
        if remaining_funds >= monthly_saving_needed:
            suggestions.append(f"To reach your goal of KES {savings_goal_amount:,.2f} in {savings_goal_timeframe_months} months, you need to save KES {monthly_saving_needed:,.2f} per month.")
            suggestions.append(f"You are currently on track! Consider allocating at least KES {monthly_saving_needed:,.2f} towards your goal.")
        else:
            suggestions.append(f"To reach your goal of KES {savings_goal_amount:,.2f} in {savings_goal_timeframe_months} months, you need to save KES {monthly_saving_needed:,.2f} per month.")
            suggestions.append(f"You need to increase your monthly savings by KES {monthly_saving_needed - remaining_funds:,.2f} to meet your goal.")


    suggestions.append("\n--- Investment Suggestions ---")

    mmfs = get_mmf_rates()
    if mmfs and isinstance(mmfs[0], dict) and "numeric_rate" in mmfs[0]:
        top_mmfs = sorted(mmfs, key=lambda x: x["numeric_rate"], reverse=True)[:5]
        suggestions.append("\nTop 5 Money Market Funds (MMFs):")
        for mmf in top_mmfs:
            suggestions.append(f"  - {mmf['name']}: {mmf['rate']} per annum")
    else:
        suggestions.append("  - Could not fetch reliable MMF data.")

    suggestions.append("  - Fixed Deposit Accounts: Predictable, locked savings.")
    suggestions.append("  - Government T-Bills: Safe short-term investment.")

    # if mmfs:
    #      suggestions.append("\nMoney Market Funds (MMFs) - generally low risk, good for short-term savings:")
    # for mmf in mmfs:
    #     if isinstance(mmf, dict) and "name" in mmf and "rate" in mmf:
    #         suggestions.append(f"  - {mmf['name']}: {mmf['rate']} (current rates)")
    #     else: # Fallback for simple string rates from old example
    #                  suggestions.append(f"  - {mmf} (current rates)")
    # else:
    #      suggestions.append("  - Could not fetch MMF rates at this time.")
    # suggestions.append("  - Fixed Deposit Accounts: Offer predictable returns, but funds are locked for a period.")

    return suggestions
