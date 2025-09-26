import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import koKR from 'antd/locale/ko_KR';
import 'antd/dist/reset.css';

// 컴포넌트 임포트
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Warehouse from './pages/Warehouse';
import Containers from './pages/Containers';
import Invoices from './pages/Invoices';
import KPIs from './pages/KPIs';
import SystemStatus from './pages/SystemStatus';

// API 서비스
import { SystemProvider } from './contexts/SystemContext';

function App() {
  return (
    <ConfigProvider locale={koKR}>
      <SystemProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/warehouse" element={<Warehouse />} />
              <Route path="/containers" element={<Containers />} />
              <Route path="/invoices" element={<Invoices />} />
              <Route path="/kpis" element={<KPIs />} />
              <Route path="/system" element={<SystemStatus />} />
            </Routes>
          </Layout>
        </Router>
      </SystemProvider>
    </ConfigProvider>
  );
}

export default App;









