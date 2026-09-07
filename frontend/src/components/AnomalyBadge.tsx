import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface AnomalyBadgeProps {
  reason: string;
}

const AnomalyBadge: React.FC<AnomalyBadgeProps> = ({ reason }) => {
  return (
    <div className="badge badge-danger" title={reason} style={{ cursor: 'help' }}>
      <AlertTriangle size={14} />
      <span>Anomaly</span>
    </div>
  );
};

export default AnomalyBadge;
