import os
from flask import Flask, render_template, request, jsonify
from groq import Groq
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

# --- CONFIGURATION ---
DEFAULT_MODEL = "llama-3.3-70b-versatile"

# --- SECURE API KEY LOADING ---
# The app will look for the key in the environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# --- AFFILIATE VAULT ---
AFFILIATE_OFFERS = {
    "debt": {"name": "0% APR Balance Transfer", "link": "https://www.nerdwallet.com/best/credit-cards/balance-transfer", "icon": "💳"},
    "savings": {"name": "High-Yield Savings (5.0%)", "link": "https://www.bankrate.com/banking/savings/rates/", "icon": "💰"},
    "invest": {"name": "Robo-Advisor Wealthfront", "link": "https://www.betterment.com/", "icon": "📈"},
    "insurance": {"name": "Term Life Insurance", "link": "https://www.policygenius.com/", "icon": "🛡️"},
    "budget": {"name": "YNAB (You Need A Budget)", "link": "https://www.ynab.com/", "icon": "📱"}
}

def analyze_trend(history_str):
    """Calculates slope and next month prediction."""
    try:
        data = [float(x.strip()) for x in history_str.split(',') if x.strip()]
        if len(data) < 2: return 0, 0, "Stable"
        
        X = np.array(range(len(data))).reshape(-1, 1)
        y = np.array(data)
        model = LinearRegression().fit(X, y)
        
        prediction = model.predict(np.array([[len(data)]]))[0]
        trend = model.coef_[0]
        
        status = "rising" if trend > 15 else "falling" if trend < -15 else "stable"
        return max(0, prediction), trend, status
    except:
        return 0, 0, "error"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # 1. Security Check
    if not GROQ_API_KEY:
        return jsonify({"error": "Server Configuration Error: API Key missing. Please set GROQ_API_KEY in environment variables."}), 500

    data = request.json
    
    # 2. Parse Data
    try:
        income = float(data['income'])
        fixed = float(data['fixed'])
        debt = float(data['debt'])
        rate = float(data['rate'])
        savings = float(data['savings'])
        
        pred_food, t_food, s_food = analyze_trend(data['food_hist'])
        pred_misc, t_misc, s_misc = analyze_trend(data['misc_hist'])
        
        total_variable = pred_food + float(data['transport_pred']) + pred_misc
        total_spend = fixed + total_variable
        cash_flow = income - total_spend
        
        # 3. Logic Gates
        savings_rate = (cash_flow / income * 100) if income > 0 else 0
        runway = savings / total_spend if total_spend > 0 else 0
        
        # Monetization Logic
        if debt > 2000 and rate > 15:
            tool = AFFILIATE_OFFERS['debt']
            strategy = "DEBT AVALANCHE"
        elif runway < 3:
            tool = AFFILIATE_OFFERS['insurance'] if float(data['household']) > 1 else AFFILIATE_OFFERS['budget']
            strategy = "SECURITY FIRST"
        elif savings_rate > 20:
            tool = AFFILIATE_OFFERS['invest']
            strategy = "WEALTH ACCELERATION"
        else:
            tool = AFFILIATE_OFFERS['savings']
            strategy = "OPTIMIZATION"

        # 4. AI Generation
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"""
        Act as a Supreme Financial Architect.
        User: Income ${income}, Spend ${total_spend}, Debt ${debt} ({rate}%), Goal: "{data['goal']}".
        Trends: Food is {s_food}, Misc is {s_misc}.
        Cash Flow: ${cash_flow}/mo.
        
        Create a Battle Plan (Markdown):
        1. **Reality Check:** Can they afford the goal?
        2. **The Cuts:** Specific dollar amounts to cut from Food/Misc.
        3. **The Strategy:** How to attack the debt or build savings.
        4. **Tone:** Ruthless but encouraging.
        """
        
        completion = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=500
        )
        ai_advice = completion.choices[0].message.content

        return jsonify({
            "cash_flow": cash_flow,
            "savings_rate": savings_rate,
            "runway": runway,
            "strategy": strategy,
            "tool": tool,
            "ai_advice": ai_advice,
            "trends": {
                "food": {"val": pred_food, "status": s_food},
                "misc": {"val": pred_misc, "status": s_misc}
            },
            "chart_data": [fixed, pred_food, float(data['transport_pred']), pred_misc, (debt/10)]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
 
