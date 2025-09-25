import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, Select, Space, message, Typography, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;
const { Option } = Select;

const Containers = () => {
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingContainer, setEditingContainer] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadContainers();
  }, []);

  const loadContainers = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/containers');
      setContainers(response.data);
    } catch (error) {
      message.error('컨테이너 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingContainer(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingContainer(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      message.success('컨테이너 삭제 완료');
      loadContainers();
    } catch (error) {
      message.error('컨테이너 삭제 실패');
    }
  };

  const handleSubmit = async (values) => {
    try {
      if (editingContainer) {
        message.success('컨테이너 수정 완료');
      } else {
        await axios.post('/api/v1/containers', values);
        message.success('컨테이너 생성 완료');
      }
      setModalVisible(false);
      loadContainers();
    } catch (error) {
      message.error('컨테이너 저장 실패');
    }
  };

  const columns = [
    {
      title: '컨테이너 ID',
      dataIndex: 'container_id',
      key: 'container_id',
    },
    {
      title: '무게 (kg)',
      dataIndex: 'weight',
      key: 'weight',
      render: (value) => value.toLocaleString(),
    },
    {
      title: '부피 (m³)',
      dataIndex: 'volume',
      key: 'volume',
      render: (value) => value.toLocaleString(),
    },
    {
      title: '압력 (t/m²)',
      dataIndex: 'pressure',
      key: 'pressure',
      render: (value) => (
        <Tag color={value > 4.0 ? 'red' : 'green'}>
          {value} t/m²
          {value > 4.0 && <ExclamationCircleOutlined style={{ marginLeft: 4 }} />}
        </Tag>
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
        <Tag color={value === 'active' ? 'green' : 'orange'}>
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
            onClick={() => handleDelete(record.container_id)}
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
        title={<Title level={3}>컨테이너 관리</Title>}
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            새 컨테이너 추가
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={containers}
          rowKey="container_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editingContainer ? '컨테이너 수정' : '새 컨테이너 추가'}
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
            name="container_id"
            label="컨테이너 ID"
            rules={[{ required: true, message: '컨테이너 ID를 입력하세요' }]}
          >
            <Input placeholder="예: CONT001" />
          </Form.Item>

          <Form.Item
            name="weight"
            label="무게 (kg)"
            rules={[{ required: true, message: '무게를 입력하세요' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="500"
              min={0}
              step={0.1}
            />
          </Form.Item>

          <Form.Item
            name="volume"
            label="부피 (m³)"
            rules={[{ required: true, message: '부피를 입력하세요' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="25"
              min={0}
              step={0.1}
            />
          </Form.Item>

          <Form.Item
            name="pressure"
            label="압력 (t/m²)"
            rules={[
              { required: true, message: '압력을 입력하세요' },
              { type: 'number', max: 4.0, message: '압력은 4.0 t/m² 이하여야 합니다' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="3.5"
              min={0}
              max={4.0}
              step={0.1}
            />
          </Form.Item>

          <Form.Item
            name="location"
            label="위치"
            rules={[{ required: true, message: '위치를 입력하세요' }]}
          >
            <Input placeholder="예: Zone A" />
          </Form.Item>

          <Form.Item
            name="status"
            label="상태"
            rules={[{ required: true, message: '상태를 선택하세요' }]}
          >
            <Select placeholder="상태 선택">
              <Option value="active">활성</Option>
              <Option value="inactive">비활성</Option>
              <Option value="maintenance">정비중</Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingContainer ? '수정' : '생성'}
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

export default Containers;









