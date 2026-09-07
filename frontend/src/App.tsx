import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import { Wallet, LogOut, LayoutDashboard, List, PlusCircle, TrendingUp } from 'lucide-react';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import TransactionList from './pages/TransactionList';
import AddTransaction from './pages/AddTransaction';
import Predictions from './pages/Predictions';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem('access_token');

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  if (!token) return null;

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Wallet color="var(--accent-color)" />
        <span>Finance Tracker</span>
      </div>
      <div className="navbar-links">
        <Link to="/" className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}>
          <div className="flex items-center gap-2"><LayoutDashboard size={18}/> Dashboard</div>
        </Link>
        <Link to="/transactions" className={`nav-link ${location.pathname === '/transactions' ? 'active' : ''}`}>
          <div className="flex items-center gap-2"><List size={18}/> Transactions</div>
        </Link>
        <Link to="/add" className={`nav-link ${location.pathname === '/add' ? 'active' : ''}`}>
          <div className="flex items-center gap-2"><PlusCircle size={18}/> Add</div>
        </Link>
        <Link to="/predictions" className={`nav-link ${location.pathname === '/predictions' ? 'active' : ''}`}>
          <div className="flex items-center gap-2"><TrendingUp size={18}/> Predict</div>
        </Link>
        <button onClick={handleLogout} className="btn" style={{ backgroundColor: 'transparent', color: 'var(--text-secondary)', padding: '0.5rem' }}>
          <LogOut size={20} />
        </button>
      </div>
    </nav>
  );
};

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/login';
    return null;
  }
  return <>{children}</>;
};

function App() {
  return (
    <Router>
      <Navigation />
      <div className="app-container" style={{ paddingTop: localStorage.getItem('access_token') ? '0' : '2rem' }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route 
            path="/" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/transactions" 
            element={
              <ProtectedRoute>
                <TransactionList />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/add" 
            element={
              <ProtectedRoute>
                <AddTransaction />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/predictions" 
            element={
              <ProtectedRoute>
                <Predictions />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
