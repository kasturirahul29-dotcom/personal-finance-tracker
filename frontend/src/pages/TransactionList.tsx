import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { Transaction, Category } from '../types';
import AnomalyBadge from '../components/AnomalyBadge';

const TransactionList: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [filterCategory, setFilterCategory] = useState('');
  const [filterMonth, setFilterMonth] = useState('');
  const [filterType, setFilterType] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const res = await client.get('/categories/');
        setCategories(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchCategories();
  }, []);

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      let query = '';
      if (filterCategory) query += `category=${filterCategory}&`;
      if (filterMonth) query += `month=${filterMonth}&`;
      if (filterType) query += `type=${filterType}&`;
      
      const res = await client.get(`/transactions/?${query}`);
      setTransactions(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, [filterCategory, filterMonth, filterType]);

  const getCategoryName = (id: number) => {
    return categories.find(c => c.id === id)?.name || 'Unknown';
  };

  return (
    <div className="card animate-fade-in">
      <h2 style={{ marginBottom: '1.5rem' }}>Transactions</h2>
      
      <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
        <div className="input-group">
          <label>Category</label>
          <select className="input-field" value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)}>
            <option value="">All Categories</option>
            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div className="input-group">
          <label>Month (YYYY-MM)</label>
          <input type="month" className="input-field" value={filterMonth} onChange={(e) => setFilterMonth(e.target.value)} />
        </div>
        <div className="input-group">
          <label>Type</label>
          <select className="input-field" value={filterType} onChange={(e) => setFilterType(e.target.value)}>
            <option value="">All</option>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center mt-4">Loading...</div>
      ) : transactions.length === 0 ? (
        <div className="text-center mt-4 text-secondary">No transactions found.</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Type</th>
                <th>Category</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(t => (
                <tr key={t.id}>
                  <td>{t.date}</td>
                  <td>
                    <span className={`badge ${t.type === 'income' ? 'badge-success' : 'badge-warning'}`}>
                      {t.type}
                    </span>
                  </td>
                  <td>{getCategoryName(t.category)}</td>
                  <td>{t.description || '-'}</td>
                  <td style={{ fontWeight: 600 }}>₹{t.amount.toFixed(2)}</td>
                  <td>
                    {t.is_anomaly && t.anomaly_reason ? (
                      <AnomalyBadge reason={t.anomaly_reason} />
                    ) : (
                      <span className="text-secondary" style={{ fontSize: '0.875rem' }}>Normal</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default TransactionList;
