let financeChart = null;

async function runAnalysis() {
    // 1. UI Updates
    document.getElementById('input-section').classList.add('hidden');
    document.getElementById('loader').classList.remove('hidden');
    
    // 2. Gather Data (API Key is NO LONGER collected here)
    const payload = {
        income: document.getElementById('income').value,
        fixed: document.getElementById('fixed').value,
        food_hist: document.getElementById('foodHist').value,
        misc_hist: document.getElementById('miscHist').value,
        transport_pred: document.getElementById('transPred').value,
        debt: document.getElementById('debt').value,
        rate: document.getElementById('rate').value,
        savings: document.getElementById('savings').value,
        household: document.getElementById('household').value,
        goal: document.getElementById('goal').value
    };

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert("Error: " + data.error);
            // Reload to reset state
            location.reload();
            return;
        }

        // Render Results
        document.getElementById('loader').classList.add('hidden');
        document.getElementById('results-section').classList.remove('hidden');
        
        // Vitals Logic
        const cashClass = data.cash_flow > 0 ? '#00ff9d' : '#ff4b4b';
        document.getElementById('cashFlowVal').innerText = `$${data.cash_flow.toFixed(2)}`;
        document.getElementById('cashFlowVal').style.color = cashClass;
        
        document.getElementById('stratVal').innerText = data.strategy;
        document.getElementById('runwayVal').innerText = `${data.runway.toFixed(1)} Months`;

        // AI Text
        document.getElementById('aiContent').innerHTML = marked.parse(data.ai_advice);

        // Tool
        document.getElementById('toolName').innerText = data.tool.name;
        document.getElementById('toolLink').href = data.tool.link;
        document.getElementById('toolIcon').innerText = data.tool.icon;

        renderChart(data.chart_data);

    } catch (e) {
        alert("System Failure: " + e);
        location.reload();
    }
}

function renderChart(dataValues) {
    const ctx = document.getElementById('financeChart').getContext('2d');
    if (financeChart) financeChart.destroy();

    financeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Fixed', 'Food', 'Transport', 'Misc', 'Debt Scale'],
            datasets: [{
                data: dataValues,
                backgroundColor: ['#3a7bd5', '#ff4b4b', '#f1c40f', '#9b59b6', '#34495e'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom', labels: { color: 'white' } } }
        }
    });
          }
          
