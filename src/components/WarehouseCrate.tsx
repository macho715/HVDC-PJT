import React from 'react';

interface WarehouseCrateProps {
  id: string;
  dimensions: {
    length: number;
    width: number;
    height: number;
  };
  material: 'plastic' | 'wood' | 'steel';
  weight: number;
  position: {
    x: number;
    y: number;
    z: number;
  };
  status: 'placed' | 'excluded' | 'pending';
  onClick?: () => void;
}

const WarehouseCrate: React.FC<WarehouseCrateProps> = ({
  id,
  dimensions,
  material,
  weight,
  position,
  status,
  onClick
}) => {
  const getMaterialColor = (material: string) => {
    switch (material) {
      case 'plastic': return '#2196f3';
      case 'wood': return '#8d6e63';
      case 'steel': return '#9e9e9e';
      default: return '#6c757d';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'placed': return '#28a745';
      case 'excluded': return '#dc3545';
      case 'pending': return '#ffc107';
      default: return '#6c757d';
    }
  };

  return (
    <div
      className="warehouse-crate"
      style={{
        position: 'absolute',
        left: position.x,
        top: position.y,
        width: dimensions.length * 10,
        height: dimensions.width * 10,
        backgroundColor: getMaterialColor(material),
        border: `2px solid ${getStatusColor(status)}`,
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s ease'
      }}
      onClick={onClick}
      title={`${id} - ${material} - ${weight}kg`}
    >
      <div className="crate-label" style={{ fontSize: '10px', color: 'white', textAlign: 'center' }}>
        {id}
      </div>
    </div>
  );
};

export default WarehouseCrate;
