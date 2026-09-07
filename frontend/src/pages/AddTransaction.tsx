import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { Category } from '../types';
import AnomalyBadge from '../components/AnomalyBadge';

const AddTransaction: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [amount, setAmount] = useState('');
  const [type, setType] = useState<'income' | 'expense'>('expense');
  const [date, setDate] = useState(new Date().toISOString().substring(0, 10));
  const [categoryId, setCategoryId] = useState('');
  const [description, setDescription] = useState('');
  const [anomaly, setAnomaly] = useState<{ is_anomaly: boolean; reason: string | null } | null>(null);
  const [error, setError] = useState('');

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAnomaly(null);
    setError('');
    
    try {
      const res = await client.post('/transactions/', {
        amount,
        type,
        date,
        category: categoryId,
        description
      });
      
      if (res.data.is_anomaly) {
        setAnomaly({ is_anomaly: true, reason: res.data.anomaly_reason });
      } else {
        alert('Transaction added successfully!');
        setAmount('');
        setDescription('');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add transaction');
    }
  };

  return (
    <div className="card animate-fade-in" style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '1.5rem' }}>Add Transaction</h2>
      
      {anomaly && anomaly.is_anomaly && (
        <div style={{ marginBottom: '1rem', padding: '1rem', border: '1px solid var(--danger-color)', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '0.5rem' }}>
          <div className="flex items-center gap-2 mb-2">
            <AnomalyBadge reason={anomaly.reason || ''} />
            <strong className="text-danger">Anomaly Detected!</strong>
          </div>
          <p style={{ fontSize: '0.875rem' }}>{anomaly.reason}</p>
        </div>
      )}
      
      {error && <div className="badge badge-danger mb-4">{error}</div>}
      
      <form onSubmit={handleSubmit}>
        <div className="grid-2">
          <div className="input-group">
            <label htmlFor="type">Type</label>
            <select 
              id="type" 
              className="input-field" 
              value={type} 
              onChange={(e) => setType(e.target.value as 'income' | 'expense')}
            >
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </select>
          </div>
          <div className="input-group">
            <label htmlFor="amount">Amount</label>
            <input 
              type="number" 
              id="amount" 
              className="input-field" 
              value={amount} 
              onChange={(e) => setAmount(e.target.value)} 
              required 
              min="0.01" 
              step="0.01" 
            />
          </div>
        </div>
        
        <div className="grid-2">
          <div className="input-group">
            <label htmlFor="category">Category</label>
            <select 
              id="category" 
              className="input-field" 
              value={categoryId} 
              onChange={(e) => setCategoryId(e.target.value)} 
              required
            >
              <option value="">Select Category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div className="input-group">
            <label htmlFor="date">Date</label>
            <input 
              type="date" 
              id="date" 
              className="input-field" 
              value={date} 
              onChange={(e) => setDate(e.target.value)} 
              required 
            />
          </div>
        </div>
        
        <div className="input-group">
          <label htmlFor="description">Description (Optional)</label>
          <input 
            type="text" 
            id="description" 
            className="input-field" 
            value={description} 
            onChange={(e) => setDescription(e.target.value)} 
          />
        </div>
        
        <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1rem' }}>
          Save Transaction
        </button>
      </form>
    </div>
  );
};

export default AddTransaction;
