import React, { useState } from 'react';
import { Layout as AntLayout, Menu, Button, Space, Typography } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  HomeOutlined,
  ContainerOutlined,
  FileTextOutlined,
  BarChartOutlined,
  SettingOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons';
import { useSystem } from '../contexts/SystemContext';

const { Header, Sider, Content } = AntLayout;
const { Title } = Typography;

const Layout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { systemMode, switchMode } = useSystem();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '대시보드',
    },
    {
      key: '/warehouse',
      icon: <HomeOutlined />,
      label: '창고 관리',
    },
    {
      key: '/containers',
      icon: <ContainerOutlined />,
      label: '컨테이너',
    },
    {
      key: '/invoices',
      icon: <FileTextOutlined />,
      label: '송장 관리',
    },
    {
      key: '/kpis',
      icon: <BarChartOutlined />,
      label: 'KPI 모니터링',
    },
    {
      key: '/system',
      icon: <SettingOutlined />,
      label: '시스템 상태',
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  const handleModeSwitch = async (mode) => {
    try {
      await switchMode(mode);
    } catch (error) {
      console.error('모드 전환 실패:', error);
    }
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div style={{ 
          height: 32, 
          margin: 16, 
          background: 'rgba(255, 255, 255, 0.2)',
          borderRadius: 6,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: 'bold'
        }}>
          HVDC
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <AntLayout>
        <Header style={{ 
          padding: '0 16px', 
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <Space>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ fontSize: '16px', width: 64, height: 64 }}
            />
            <Title level={4} style={{ margin: 0 }}>
              HVDC 물류 시스템
            </Title>
          </Space>
          <Space>
            <span>현재 모드: <strong>{systemMode}</strong></span>
            <Button 
              type="primary" 
              onClick={() => handleModeSwitch('LATTICE')}
              disabled={systemMode === 'LATTICE'}
            >
              LATTICE
            </Button>
            <Button 
              onClick={() => handleModeSwitch('RHYTHM')}
              disabled={systemMode === 'RHYTHM'}
            >
              RHYTHM
            </Button>
            <Button 
              danger 
              onClick={() => handleModeSwitch('ZERO')}
              disabled={systemMode === 'ZERO'}
            >
              ZERO
            </Button>
          </Space>
        </Header>
        <Content style={{ 
          margin: '24px 16px', 
          padding: 24, 
          background: '#fff',
          borderRadius: 6,
          minHeight: 280
        }}>
          {children}
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;









