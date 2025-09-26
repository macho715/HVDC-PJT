import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Progress, Table, Button, Space, Typography } from 'antd';
import { 
  HomeOutlined, 
  ContainerOutlined, 
  FileTextOutlined, 
  BarChartOutlined,
  ReloadOutlined 
} from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import { useSystem } from '../contexts/SystemContext';

const { Title, Text } = Typography;

const Dashboard = () => {
  const { systemMode, systemStatus } = useSystem();
  const [warehouseData, setWarehouseData] = useState([]);
  const [containerData, setContainerData] = useState([]);
  const [invoiceData, setInvoiceData] = useState([]);
  const [kpiData, setKpiData] = useState([]);
  const [loading, setLoading] = useState(false);

  // 데이터 로드
  const loadData = async () => {
    setLoading(true);
    try {
      const [warehouseRes, containerRes, invoiceRes, kpiRes] = await Promise.all([
        axios.get('/api/v1/warehouses'),
        axios.get('/api/v1/containers'),
        axios.get('/api/v1/invoices'),
        axios.get('/api/v1/kpis')
      ]);

      setWarehouseData(warehouseRes.data);
      setContainerData(containerRes.data);
      setInvoiceData(invoiceRes.data);
      setKpiData(kpiRes.data);
    } catch (error) {
      console.error('데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // KPI 차트 데이터
  const chartData = kpiData.map(kpi => ({
    name: kpi.metric_name,
    value: kpi.value,
    target: kpi.target,
    status: kpi.status
  }));

  // 창고 테이블 컬럼
  const warehouseColumns = [
    {
      title: '창고 ID',
      dataIndex: 'warehouse_id',
      key: 'warehouse_id',
    },
    {
      title: '구역',
      dataIndex: 'zone',
      key: 'zone',
    },
    {
      title: '용량',
      dataIndex: 'capacity',
      key: 'capacity',
      render: (value) => `${value.toLocaleString()} m³`,
    },
    {
      title: '사용률',
      dataIndex: 'current_utilization',
      key: 'current_utilization',
      render: (value, record) => (
        <Progress 
          percent={Math.round((value / record.capacity) * 100)} 
          size="small"
          status={value / record.capacity > 0.8 ? 'exception' : 'normal'}
        />
      ),
    },
    {
      title: '온도',
      dataIndex: 'temperature',
      key: 'temperature',
      render: (value) => `${value}°C`,
    },
  ];

  // 컨테이너 테이블 컬럼
  const containerColumns = [
    {
      title: '컨테이너 ID',
      dataIndex: 'container_id',
      key: 'container_id',
    },
    {
      title: '무게',
      dataIndex: 'weight',
      key: 'weight',
      render: (value) => `${value} kg`,
    },
    {
      title: '압력',
      dataIndex: 'pressure',
      key: 'pressure',
      render: (value) => (
        <Text type={value > 4.0 ? 'danger' : 'success'}>
          {value} t/m²
        </Text>
      ),
    },
    {
      title: '위치',
      dataIndex: 'location',
      key: 'location',
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      render: (value) => (
        <Text type={value === 'active' ? 'success' : 'warning'}>
          {value}
        </Text>
      ),
    },
  ];

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Title level={2}>
            HVDC 물류 시스템 대시보드
            <Text type="secondary" style={{ marginLeft: 16, fontSize: '16px' }}>
              현재 모드: {systemMode}
            </Text>
          </Title>
        </Col>
      </Row>

      {/* 통계 카드 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="창고 수"
              value={warehouseData.length}
              prefix={<HomeOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="컨테이너 수"
              value={containerData.length}
              prefix={<ContainerOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="송장 수"
              value={invoiceData.length}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="KPI 지표"
              value={kpiData.length}
              prefix={<BarChartOutlined />}
              valueStyle={{ color: '#eb2f96' }}
            />
          </Card>
        </Col>
      </Row>

      {/* KPI 차트 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="KPI 성과 추이" extra={
            <Button icon={<ReloadOutlined />} onClick={loadData} loading={loading}>
              새로고침
            </Button>
          }>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#1890ff" 
                  strokeWidth={2}
                  name="실제 값"
                />
                <Line 
                  type="monotone" 
                  dataKey="target" 
                  stroke="#52c41a" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="목표 값"
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* 데이터 테이블 */}
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="창고 현황" size="small">
            <Table
              columns={warehouseColumns}
              dataSource={warehouseData}
              rowKey="warehouse_id"
              pagination={false}
              size="small"
              scroll={{ y: 200 }}
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="컨테이너 현황" size="small">
            <Table
              columns={containerColumns}
              dataSource={containerData}
              rowKey="container_id"
              pagination={false}
              size="small"
              scroll={{ y: 200 }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;









