import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { Category, PredictionResult } from '../types';

const Predictions: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
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

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCategory) return;
    
    setLoading(true);
    setError('');
    setPrediction(null);
    
    try {
      const res = await client.get(`/dashboard/predict/?category=${selectedCategory}`);
      setPrediction(res.data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to generate prediction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card animate-fade-in">
      <h2 style={{ marginBottom: '1.5rem' }}>Expense Predictions</h2>
      <p className="text-secondary mb-4">
        Select a category to predict your expenses for next month.
      </p>

      <form onSubmit={handlePredict} className="mb-4">
        <div className="flex gap-4 items-center">
          <div className="input-group" style={{ marginBottom: 0, flex: 1 }}>
            <select
              className="input-field"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              required
            >
              <option value="">Select Category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Predicting...' : 'Predict'}
          </button>
        </div>
      </form>

      {error && <div className="badge badge-danger mb-4">{error}</div>}

      {prediction && (
        <div style={{ marginTop: '2rem', padding: '1.5rem', backgroundColor: 'var(--bg-primary)', borderRadius: '0.5rem', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>
            Predicted amount: <span style={{ fontWeight: 700, color: 'var(--accent-color)' }}>₹{prediction.predicted_amount.toFixed(2)}</span>
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Prediction method: <strong>{prediction.method === 'linear_regression' ? 'Linear Regression' : 'Moving Average'}</strong> ({prediction.months_used} months of data)
          </div>
        </div>
      )}
    </div>
  );
};

export default Predictions;
