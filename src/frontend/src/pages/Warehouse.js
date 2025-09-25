import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, Select, Space, message, Typography } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;
const { Option } = Select;

const Warehouse = () => {
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingWarehouse, setEditingWarehouse] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadWarehouses();
  }, []);

  const loadWarehouses = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/warehouses');
      setWarehouses(response.data);
    } catch (error) {
      message.error('창고 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingWarehouse(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingWarehouse(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      // 실제로는 DELETE API 호출
      message.success('창고 삭제 완료');
      loadWarehouses();
    } catch (error) {
      message.error('창고 삭제 실패');
    }
  };

  const handleSubmit = async (values) => {
    try {
      if (editingWarehouse) {
        // 수정 로직
        message.success('창고 수정 완료');
      } else {
        // 생성 로직
        await axios.post('/api/v1/warehouses', values);
        message.success('창고 생성 완료');
      }
      setModalVisible(false);
      loadWarehouses();
    } catch (error) {
      message.error('창고 저장 실패');
    }
  };

  const columns = [
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
      title: '용량 (m³)',
      dataIndex: 'capacity',
      key: 'capacity',
      render: (value) => value.toLocaleString(),
    },
    {
      title: '현재 사용량 (m³)',
      dataIndex: 'current_utilization',
      key: 'current_utilization',
      render: (value) => value.toLocaleString(),
    },
    {
      title: '온도 (°C)',
      dataIndex: 'temperature',
      key: 'temperature',
    },
    {
      title: '습도 (%)',
      dataIndex: 'humidity',
      key: 'humidity',
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
            onClick={() => handleDelete(record.warehouse_id)}
          >
            삭제
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card
        title={<Title level={3}>창고 관리</Title>}
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            새 창고 추가
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={warehouses}
          rowKey="warehouse_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editingWarehouse ? '창고 수정' : '새 창고 추가'}
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
            name="warehouse_id"
            label="창고 ID"
            rules={[{ required: true, message: '창고 ID를 입력하세요' }]}
          >
            <Input placeholder="예: WH001" />
          </Form.Item>

          <Form.Item
            name="zone"
            label="구역"
            rules={[{ required: true, message: '구역을 선택하세요' }]}
          >
            <Select placeholder="구역 선택">
              <Option value="A">A구역</Option>
              <Option value="B">B구역</Option>
              <Option value="C">C구역</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="capacity"
            label="용량 (m³)"
            rules={[{ required: true, message: '용량을 입력하세요' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="1000"
              min={0}
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value.replace(/\$\s?|(,*)/g, '')}
            />
          </Form.Item>

          <Form.Item
            name="current_utilization"
            label="현재 사용량 (m³)"
            rules={[{ required: true, message: '현재 사용량을 입력하세요' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="750"
              min={0}
              formatter={value => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
              parser={value => value.replace(/\$\s?|(,*)/g, '')}
            />
          </Form.Item>

          <Form.Item
            name="temperature"
            label="온도 (°C)"
            rules={[{ required: true, message: '온도를 입력하세요' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="22.5"
              min={-50}
              max={100}
              step={0.1}
            />
          </Form.Item>

          <Form.Item
            name="humidity"
            label="습도 (%)"
            rules={[{ required: true, message: '습도를 입력하세요' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="45"
              min={0}
              max={100}
              step={1}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingWarehouse ? '수정' : '생성'}
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

export default Warehouse;









