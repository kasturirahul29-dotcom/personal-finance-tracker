from datetime import timedelta
import numpy as np
import pandas as pd
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from sklearn.linear_model import LinearRegression
from .models import Transaction, Budget

def check_anomaly(transaction):
    if transaction.type != "expense":
        return False, None
    
    six_months_ago = transaction.date - timedelta(days=6*30)
    
    # 1. Fetch past transactions
    past_transactions = Transaction.objects.filter(
        user=transaction.user,
        category=transaction.category,
        type="expense",
        date__gte=six_months_ago
    ).exclude(id=transaction.id)

    if past_transactions.count() < 3:
        # 2. Cold start rule
        if transaction.amount > 5000:
            return True, "First-time high-value transaction in this category (cold start rule)"
        return False, None
    
    # 3. 3 or more past transactions
    amounts = [float(t.amount) for t in past_transactions]
    mean = np.mean(amounts)
    std_dev = np.std(amounts)
    # std_dev could be 0 if all transactions have same amount, handle it gracefully
    
    if float(transaction.amount) > mean + 2 * std_dev:
        return True, f"Amount ₹{transaction.amount} exceeds 2 std deviations above category average (₹{mean:.2f} ± {std_dev:.2f})"
        
    return False, None

def predict_next_month(user, category):
    six_months_ago = timezone.now().date().replace(day=1) - relativedelta(months=6)
    
    # 1. Fetch monthly totals for expense transactions, grouped by month, last 6 months
    transactions = Transaction.objects.filter(
        user=user,
        category=category,
        type="expense",
        date__gte=six_months_ago
    )
    
    if not transactions.exists():
        return {"predicted_amount": 0.0, "method": "moving_average", "months_used": 0}
        
    # Group by month
    df = pd.DataFrame(list(transactions.values('date', 'amount')))
    df['amount'] = df['amount'].astype(float)
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
    monthly_totals = df.groupby('month')['amount'].sum().reset_index()
    monthly_totals = monthly_totals.sort_values('month')
    
    months_used = len(monthly_totals)
    
    if months_used >= 3:
        # 2. Linear regression
        X = np.arange(months_used).reshape(-1, 1)
        y = monthly_totals['amount'].values
        model = LinearRegression()
        model.fit(X, y)
        predicted_amount = model.predict([[months_used]])[0]
        method = "linear_regression"
    else:
        # 3. Moving average fallback
        predicted_amount = monthly_totals['amount'].mean()
        method = "moving_average"
        
    return {
        "predicted_amount": float(max(0, predicted_amount)), # Ensure no negative predictions
        "method": method,
        "months_used": months_used
    }

def suggest_budget(user, category):
    # 1. Fetch last 3 months of expense totals
    three_months_ago = timezone.now().date().replace(day=1) - relativedelta(months=3)
    transactions = Transaction.objects.filter(
        user=user,
        category=category,
        type="expense",
        date__gte=three_months_ago
    )
    
    if transactions.exists():
        df = pd.DataFrame(list(transactions.values('date', 'amount')))
        df['amount'] = df['amount'].astype(float)
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        monthly_totals = df.groupby('month')['amount'].sum()
        avg_last_3_months = monthly_totals.mean()
    else:
        avg_last_3_months = 0.0
        
    # 2. suggested_limit = average * 1.1
    suggested_limit = float(avg_last_3_months) * 1.1
    
    # 3. Check existing budget for current month
    current_month_first_day = timezone.now().date().replace(day=1)
    budget = Budget.objects.filter(
        user=user,
        category=category,
        month=current_month_first_day
    ).first()
    
    current_limit = None
    percent_used = None
    warning = None
    
    if budget:
        current_limit = float(budget.monthly_limit)
        
        # Calculate current month spend
        current_month_transactions = Transaction.objects.filter(
            user=user,
            category=category,
            type="expense",
            date__gte=current_month_first_day
        )
        current_month_spend = sum(t.amount for t in current_month_transactions)
        
        percent_used = (float(current_month_spend) / current_limit) * 100 if current_limit > 0 else 0
        
        if percent_used > 100:
            warning = "over_budget"
        elif percent_used > 80:
            warning = "approaching_limit"
            
    return {
        "suggested_limit": float(suggested_limit),
        "current_limit": current_limit,
        "percent_used": percent_used,
        "warning": warning
    }
