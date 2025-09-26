import React from 'react';

interface KPICardProps {
  title: string;
  value: number | string;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  color: 'success' | 'warning' | 'danger' | 'info';
}

const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  unit,
  trend,
  color
}) => {
  const getColorClass = (color: string) => {
    switch (color) {
      case 'success': return 'bg-success text-white';
      case 'warning': return 'bg-warning text-dark';
      case 'danger': return 'bg-danger text-white';
      case 'info': return 'bg-info text-white';
      default: return 'bg-secondary text-white';
    }
  };

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up': return '↗️';
      case 'down': return '↘️';
      case 'stable': return '→';
      default: return '';
    }
  };

  return (
    <div className={`kpi-card ${getColorClass(color)} p-3 rounded`}>
      <div className="kpi-title" style={{ fontSize: '14px', fontWeight: 'bold' }}>
        {title}
      </div>
      <div className="kpi-value" style={{ fontSize: '24px', fontWeight: 'bold' }}>
        {value}{unit && <span style={{ fontSize: '14px' }}> {unit}</span>}
        {trend && <span style={{ marginLeft: '8px' }}>{getTrendIcon(trend)}</span>}
      </div>
    </div>
  );
};

export default KPICard;
