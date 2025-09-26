import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const SystemContext = createContext();

export const useSystem = () => {
  const context = useContext(SystemContext);
  if (!context) {
    throw new Error('useSystem must be used within a SystemProvider');
  }
  return context;
};

export const SystemProvider = ({ children }) => {
  const [systemMode, setSystemMode] = useState('PRIME');
  const [systemStatus, setSystemStatus] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 시스템 상태 조회
  const fetchSystemStatus = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/system/status');
      setSystemStatus(response.data);
      setSystemMode(response.data.mode);
      setError(null);
    } catch (err) {
      setError('시스템 상태 조회 실패');
      console.error('시스템 상태 조회 오류:', err);
    } finally {
      setLoading(false);
    }
  };

  // 모드 전환
  const switchMode = async (newMode) => {
    try {
      setLoading(true);
      const response = await axios.post('/api/v1/system/switch-mode', {
        mode: newMode
      });
      setSystemMode(newMode);
      await fetchSystemStatus(); // 상태 새로고침
      setError(null);
      return response.data;
    } catch (err) {
      setError(`모드 전환 실패: ${err.response?.data?.detail || err.message}`);
      console.error('모드 전환 오류:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // 초기 로드
  useEffect(() => {
    fetchSystemStatus();
  }, []);

  const value = {
    systemMode,
    systemStatus,
    loading,
    error,
    fetchSystemStatus,
    switchMode
  };

  return (
    <SystemContext.Provider value={value}>
      {children}
    </SystemContext.Provider>
  );
};









