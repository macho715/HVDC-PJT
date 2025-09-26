import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, Select, Space, message, Typography, Tag, Progress } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, BarChartOutlined } from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const { Title } = Typography;
const { Option } = Select;

const KPIs = () => {
  const [kpis, setKpis] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingKPI, setEditingKPI] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadKPIs();
  }, []);

  const loadKPIs = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/kpis');
      setKpis(response.data);
    } catch (error) {
      message.error('KPI 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingKPI(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingKPI(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      message.success('KPI 삭제 완료');
      loadKPIs();
    } catch (error) {
      message.error('KPI 삭제 실패');
    }
  };

  const handleSubmit = async (values) => {
    try {
      if (editingKPI) {
        message.success('KPI 수정 완료');
      } else {
        await axios.post('/api/v1/kpis', values);
        message.success('KPI 생성 완료');
      }
      setModalVisible(false);
      loadKPIs();
    } catch (error) {
      message.error('KPI 저장 실패');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'SUCCESS': return 'green';
      case 'WARNING': return 'orange';
      case 'CRITICAL': return 'red';
      default: return 'default';
    }
  };

  const getProgressStatus = (value, target) => {
    const ratio = value / target;
    if (ratio >= 1.0) return 'success';
    if (ratio >= 0.8) return 'normal';
    if (ratio >= 0.6) return 'exception';
    return 'exception';
  };

  const columns = [
    {
      title: '메트릭명',
      dataIndex: 'metric_name',
      key: 'metric_name',
    },
    {
      title: '실제 값',
      dataIndex: 'value',
      key: 'value',
      render: (value, record) => (
        <span>{value} {record.unit}</span>
      ),
    },
    {
      title: '목표 값',
      dataIndex: 'target',
      key: 'target',
      render: (value, record) => (
        <span>{value} {record.unit}</span>
      ),
    },
    {
      title: '달성률',
      key: 'achievement',
      render: (_, record) => {
        const percent = Math.round((record.value / record.target) * 100);
        return (
          <Progress
            percent={percent}
            size="small"
            status={getProgressStatus(record.value, record.target)}
            format={(percent) => `${percent}%`}
          />
        );
      },
    },
    {
      title: '상태',
      dataIndex: 'status',
      key: 'status',
      render: (value) => (
        <Tag color={getStatusColor(value)}>
          {value}
        </Tag>
      ),
    },
    {
      title: '작업',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button 
            type="primary" 
            icon={<EditOutlined />} 
            size="small"
            onClick={() => handleEdit(record)}
          >
            수정
          </Button>
          <Button 
            danger 
            icon={<DeleteOutlined />} 
            size="small"
            onClick={() => handleDelete(record.metric_name)}
          >
            삭제
          </Button>
        </Space>
      ),
    },
  ];

  // 차트 데이터
  const chartData = kpis.map(kpi => ({
    name: kpi.metric_name,
    value: kpi.value,
    target: kpi.target,
    unit: kpi.unit
  }));

  return (
    <div>
      <Card
        title={<Title level={3}>KPI 모니터링</Title>}
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            새 KPI 추가
          </Button>
        }
      >
        {/* KPI 차트 */}
        <Card title="KPI 성과 추이" style={{ marginBottom: 24 }}>
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

        {/* KPI 테이블 */}
        <Table
          columns={columns}
          dataSource={kpis}
          rowKey="metric_name"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editingKPI ? 'KPI 수정' : '새 KPI 추가'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="metric_name"
            label="메트릭명"
            rules={[{ required: true, message: '메트릭명을 입력하세요' }]}
          >
            <Input placeholder="예: warehouse_utilization" />
          </Form.Item>

          <Form.Item
            name="value"
            label="실제 값"
            rules={[{ required: true, message: '실제 값을 입력하세요' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="75"
              min={0}
              step={0.01}
              precision={2}
            />
          </Form.Item>

          <Form.Item
            name="target"
            label="목표 값"
            rules={[{ required: true, message: '목표 값을 입력하세요' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="80"
              min={0}
              step={0.01}
              precision={2}
            />
          </Form.Item>

          <Form.Item
            name="unit"
            label="단위"
            rules={[{ required: true, message: '단위를 입력하세요' }]}
          >
            <Input placeholder="예: %, kg, m³" />
          </Form.Item>

          <Form.Item
            name="status"
            label="상태"
            rules={[{ required: true, message: '상태를 선택하세요' }]}
          >
            <Select placeholder="상태 선택">
              <Option value="SUCCESS">성공</Option>
              <Option value="WARNING">경고</Option>
              <Option value="CRITICAL">위험</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingKPI ? '수정' : '생성'}
              </Button>
              <Button onClick={() => setModalVisible(false)}>
                취소
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default KPIs;









