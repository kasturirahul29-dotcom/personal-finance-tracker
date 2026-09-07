import React, { useEffect, useState } from 'react';
import client from '../api/client';
import { DashboardSummary } from '../types';
import CategoryPieChart from '../components/CategoryPieChart';
import BudgetProgressBar from '../components/BudgetProgressBar';

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Use current month YYYY-MM-01
  const currentMonth = new Date().toISOString().substring(0, 7) + '-01';

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await client.get(`/dashboard/summary/?month=${currentMonth}`);
        
        // Enhance budgets with suggestions endpoint to get percent_used and warning
        const budgetsWithUsage = await Promise.all(res.data.budgets.map(async (b: any) => {
          try {
            const sugRes = await client.get(`/budgets/suggestions/?category=${b.category}`);
            const categoryRes = await client.get(`/categories/${b.category}/`);
            return {
              ...b,
              categoryName: categoryRes.data.name,
              percent_used: sugRes.data.percent_used,
              warning: sugRes.data.warning
            };
          } catch (e) {
            return b;
          }
        }));

        setSummary({
          ...res.data,
          budgets: budgetsWithUsage
        });
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, [currentMonth]);

  if (loading) return <div className="text-center mt-4">Loading dashboard...</div>;
  if (!summary) return <div className="text-center mt-4 text-danger">Failed to load dashboard.</div>;

  return (
    <div className="animate-fade-in">
      <h2 style={{ marginBottom: '1.5rem' }}>Dashboard Overview</h2>
      
      <div className="grid-2" style={{ marginBottom: '2rem' }}>
        <div className="card text-center">
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', textTransform: 'uppercase' }}>Total Income</div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--success-color)' }}>
            ₹{summary.total_income.toFixed(2)}
          </div>
        </div>
        <div className="card text-center">
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', textTransform: 'uppercase' }}>Total Expense</div>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--danger-color)' }}>
            ₹{summary.total_expense.toFixed(2)}
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Expenses by Category</h3>
          <CategoryPieChart data={summary.by_category} />
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Budget Tracking</h3>
          {summary.budgets.length === 0 ? (
            <p className="text-secondary">No budgets set for this month.</p>
          ) : (
            summary.budgets.map((b: any) => (
              <BudgetProgressBar 
                key={b.id} 
                categoryName={b.categoryName || `Category ${b.category}`} 
                percentUsed={b.percent_used} 
                warning={b.warning} 
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
