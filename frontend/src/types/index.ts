export interface Category {
  id: number;
  name: string;
}

export interface Transaction {
  id: number;
  category: number;
  amount: number;
  type: 'income' | 'expense';
  date: string; // ISO date
  description: string;
  is_anomaly: boolean;
  anomaly_reason: string | null;
}

export interface Budget {
  id: number;
  category: number;
  monthly_limit: number;
  month: string;
}

export interface DashboardSummary {
  total_income: number;
  total_expense: number;
  by_category: { category: string; total: number }[];
  budgets: Budget[];
}

export interface PredictionResult {
  predicted_amount: number;
  method: 'linear_regression' | 'moving_average';
  months_used: number;
}
