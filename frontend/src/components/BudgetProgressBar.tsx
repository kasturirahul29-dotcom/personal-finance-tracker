import React from 'react';

interface BudgetProgressBarProps {
  categoryName: string;
  percentUsed: number | null;
  warning: string | null;
}

const BudgetProgressBar: React.FC<BudgetProgressBarProps> = ({ categoryName, percentUsed, warning }) => {
  if (percentUsed === null) return null;

  const validPercent = Math.min(percentUsed, 100);
  
  let color = 'var(--success-color)';
  if (warning === 'over_budget') color = 'var(--danger-color)';
  else if (warning === 'approaching_limit') color = 'var(--warning-color)';

  return (
    <div style={{ marginBottom: '1rem' }}>
      <div className="flex justify-between" style={{ marginBottom: '0.25rem', fontSize: '0.875rem' }}>
        <span>{categoryName}</span>
        <span style={{ color }}>{percentUsed.toFixed(1)}%</span>
      </div>
      <div style={{ height: '8px', backgroundColor: 'var(--bg-primary)', borderRadius: '9999px', overflow: 'hidden' }}>
        <div
          style={{
            height: '100%',
            backgroundColor: color,
            width: `${validPercent}%`,
            transition: 'width 0.5s ease-in-out'
          }}
        />
      </div>
      {warning && (
        <div style={{ fontSize: '0.75rem', color, marginTop: '0.25rem', textAlign: 'right' }}>
          {warning === 'over_budget' ? 'Over budget!' : 'Approaching limit'}
        </div>
      )}
    </div>
  );
};

export default BudgetProgressBar;
