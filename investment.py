
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
                name = columns[0].text.strip()  
                rate = columns[2].text.strip()  
                mmf_rates.append({"name": name, "rate": rate})

      
        print(f"Attempting to scrape MMF rates from {url}...")
        

    except requests.exceptions.RequestException as e:
        print(f"Network or request error retrieving MMF rates: {e}")
        mmf_rates = [{"name": "Error", "rate": f"Could not fetch MMF rates: {e}"}]
    except Exception as e:
        print(f"An unexpected error occurred during MMF scraping: {e}")
        mmf_rates = [{"name": "Error", "rate": f"Could not fetch MMF rates: {e}"}]
    
    return mmf_rates


def calculate_mmf_return(monthly_deposit, annual_rate, months):
    r = annual_rate / 12  # Monthly rate
    total_deposits = monthly_deposit * months

    if r == 0:
        return {
            "total_deposits": total_deposits,
            "interest_earned": 0.0,
            "future_value": total_deposits
        }

    future_value = monthly_deposit * (((1 + r) ** months - 1) / r)
    interest_earned = future_value - total_deposits

    return {
        "total_deposits": total_deposits,
        "interest_earned": interest_earned,
        "future_value": future_value
    }


def suggest_investments(remaining_funds, savings_goal_amount=0, savings_goal_timeframe_months=1):
    results = []

    if remaining_funds <= 0:
        return [{"type": "warning", "message": "No funds available for investment after expenses."}]

    # Calculate user's monthly deposit capacity
    monthly_deposit = savings_goal_amount / savings_goal_timeframe_months if savings_goal_timeframe_months > 0 else 0

    # Progress on savings goal
    if savings_goal_amount > 0 and savings_goal_timeframe_months > 0:
        if remaining_funds >= monthly_deposit:
            results.append({
                "type": "info",
                "message": f"To reach your goal of KES {savings_goal_amount:,.2f} in {savings_goal_timeframe_months} months, you're on track by saving KES {monthly_deposit:,.2f} per month."
            })
        else:
            gap = monthly_deposit - remaining_funds
            results.append({
                "type": "warning",
                "message": f"You need to save KES {monthly_deposit:,.2f} per month, but you're short by KES {gap:,.2f}."
            })

    # MMF Investment Suggestions
    mmfs = get_mmf_rates()
    top_mmfs = []

    for mmf in mmfs:
        try:
            # Convert rate string like "12.25%" to float
            rate_value = float(mmf['rate'].replace('%', '').strip()) / 100
            returns = calculate_mmf_return(
                monthly_deposit=monthly_deposit,
                annual_rate=rate_value,
                months=savings_goal_timeframe_months
            )
            top_mmfs.append({
                "name": mmf['name'],
                "rate": rate_value,
                "total_deposits": returns["total_deposits"],
                "interest_earned": returns["interest_earned"],
                "projected_return": returns["future_value"],
                # "url": mmf.get("url", "#")
            })
        except Exception:
            continue

    top_mmfs = sorted(top_mmfs, key=lambda x: x["rate"], reverse=True)[:5]
    # Recommend the best MMF
    from gui import suggest_best_mmf
    best_mmf_suggestion = suggest_best_mmf(top_mmfs)
    results.append(best_mmf_suggestion)


    if top_mmfs:
        results.append({"type": "header", "message": "Top 5 MMFs based on current rates:"})
        for mmf in top_mmfs:
            results.append({
                "type": "mmf",
                "name": mmf["name"],
                "rate": mmf["rate"] * 100,  # Convert back to percentage
                "total_deposits": mmf["total_deposits"],
                "interest_earned": mmf["interest_earned"],
                "projected_return": mmf["projected_return"],
                # "url": mmf["url"]
            })
    else:
        results.append({"type": "error", "message": "Could not fetch reliable MMF rates at this time."})

    return results










