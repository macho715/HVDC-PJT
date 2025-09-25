import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, InputNumber, Space, message, Typography, Tag } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title } = Typography;

const Invoices = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingInvoice, setEditingInvoice] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/invoices');
      setInvoices(response.data);
    } catch (error) {
      message.error('송장 데이터 로드 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingInvoice(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingInvoice(record);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      message.success('송장 삭제 완료');
      loadInvoices();
    } catch (error) {
      message.error('송장 삭제 실패');
    }
  };

  const handleSubmit = async (values) => {
    try {
      if (editingInvoice) {
        message.success('송장 수정 완료');
      } else {
        await axios.post('/api/v1/invoices', values);
        message.success('송장 생성 완료');
      }
      setModalVisible(false);
      loadInvoices();
    } catch (error) {
      message.error('송장 저장 실패');
    }
  };

  const columns = [
    {
      title: '송장 ID',
      dataIndex: 'invoice_id',
      key: 'invoice_id',
    },
    {
      title: 'HS 코드',
      dataIndex: 'hs_code',
      key: 'hs_code',
    },
    {
      title: '설명',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '수량',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (value) => value.toLocaleString(),
    },
    {
      title: '단가',
      dataIndex: 'unit_price',
      key: 'unit_price',
      render: (value) => `$${value.toLocaleString()}`,
    },
    {
      title: '총액',
      dataIndex: 'total_amount',
      key: 'total_amount',
      render: (value) => `$${value.toLocaleString()}`,
    },
    {
      title: 'OCR 신뢰도',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (value) => (
        <Tag color={value >= 0.90 ? 'green' : 'red'}>
          {(value * 100).toFixed(1)}%
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
            onClick={() => handleDelete(record.invoice_id)}
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
        title={<Title level={3}>송장 관리</Title>}
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            새 송장 추가
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={invoices}
          rowKey="invoice_id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title={editingInvoice ? '송장 수정' : '새 송장 추가'}
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
            name="invoice_id"
            label="송장 ID"
            rules={[{ required: true, message: '송장 ID를 입력하세요' }]}
          >
            <Input placeholder="예: INV001" />
          </Form.Item>

          <Form.Item
            name="hs_code"
            label="HS 코드"
            rules={[{ required: true, message: 'HS 코드를 입력하세요' }]}
          >
            <Input placeholder="예: 8471.30.00" />
          </Form.Item>

          <Form.Item
            name="description"
            label="설명"
            rules={[{ required: true, message: '설명을 입력하세요' }]}
          >
            <Input placeholder="상품 설명" />
          </Form.Item>

          <Form.Item
            name="quantity"
            label="수량"
            rules={[{ required: true, message: '수량을 입력하세요' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="100"
              min={1}
              step={1}
            />
          </Form.Item>

          <Form.Item
            name="unit_price"
            label="단가 ($)"
            rules={[{ required: true, message: '단가를 입력하세요' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="1200"
              min={0}
              step={0.01}
              precision={2}
            />
          </Form.Item>

          <Form.Item
            name="total_amount"
            label="총액 ($)"
            rules={[{ required: true, message: '총액을 입력하세요' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="120000"
              min={0}
              step={0.01}
              precision={2}
            />
          </Form.Item>

          <Form.Item
            name="confidence"
            label="OCR 신뢰도"
            rules={[
              { required: true, message: 'OCR 신뢰도를 입력하세요' },
              { type: 'number', min: 0.90, max: 1.0, message: 'OCR 신뢰도는 0.90 이상이어야 합니다' }
            ]}
          >
            <InputNumber
              style={{ width: '100%' }}
              placeholder="0.95"
              min={0.90}
              max={1.0}
              step={0.01}
              precision={2}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                {editingInvoice ? '수정' : '생성'}
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

export default Invoices;









