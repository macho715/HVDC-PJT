import { useEffect, useState } from 'react';
import { forecastCapacity } from '../utils/wh_predict_ml5.js';
export default function WarehouseForecast() {
  const [series, setSeries] = useState([]);
  useEffect(() => {
    (async () => setSeries(await forecastCapacity()))();
  }, []);
  return (
    <section>
      <h1 className="text-2xl font-bold mb-4">Warehouse Forecast</h1>
      <div className="flex space-x-2">
        {series.map((v, i) => (
          <div key={i} className="h-24 w-6 bg-blue-500/50" style={{ height: `${v / 10}px` }} title={`M+${i}: ${v.toFixed(2)}`}/>
        ))}
      </div>
    </section>
  );
} 