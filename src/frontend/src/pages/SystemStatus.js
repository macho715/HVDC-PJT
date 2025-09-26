import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, Space, Typography, Alert, Descriptions, Tag, Progress } from 'antd';
import { 
  SettingOutlined, 
  ReloadOutlined, 
  CheckCircleOutlined, 
  ExclamationCircleOutlined,
  CloseCircleOutlined 
} from '@ant-design/icons';
import { useSystem } from '../contexts/SystemContext';

const { Title, Text } = Typography;

const SystemStatus = () => {
  const { systemMode, systemStatus, loading, error, fetchSystemStatus, switchMode } = useSystem();
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      fetchSystemStatus();
      setLastUpdate(new Date());
    }, 30000); // 30초마다 자동 새로고침

    return () => clearInterval(interval);
  }, [fetchSystemStatus]);

  const handleModeSwitch = async (mode) => {
    try {
      await switchMode(mode);
      message.success(`모드가 ${mode}로 전환되었습니다`);
    } catch (error) {
      message.error('모드 전환 실패');
    }
  };

  const getModeColor = (mode) => {
    switch (mode) {
      case 'PRIME': return 'blue';
      case 'ORACLE': return 'green';
      case 'LATTICE': return 'purple';
      case 'RHYTHM': return 'orange';
      case 'COST-GUARD': return 'red';
      case 'ZERO': return 'default';
      default: return 'default';
    }
  };

  const getModeDescription = (mode) => {
    switch (mode) {
      case 'PRIME': return '기본 운영 모드 - 모든 기능 활성화';
      case 'ORACLE': return '데이터 분석 모드 - AI 기반 의사결정 지원';
      case 'LATTICE': return '창고 최적화 모드 - 적재 및 공간 효율성 극대화';
      case 'RHYTHM': return '실시간 모니터링 모드 - KPI 및 알림 집중';
      case 'COST-GUARD': return '비용 관리 모드 - 예산 및 비용 최적화';
      case 'ZERO': return '안전 모드 - 최소 기능만 활성화';
      default: return '알 수 없는 모드';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.95) return 'green';
    if (confidence >= 0.90) return 'orange';
    return 'red';
  };

  const getConfidenceStatus = (confidence) => {
    if (confidence >= 0.95) return 'success';
    if (confidence >= 0.90) return 'exception';
    return 'exception';
  };

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Title level={2}>
            시스템 상태 모니터링
            <Text type="secondary" style={{ marginLeft: 16, fontSize: '16px' }}>
              마지막 업데이트: {lastUpdate.toLocaleTimeString()}
            </Text>
          </Title>
        </Col>
      </Row>

      {/* 오류 알림 */}
      {error && (
        <Alert
          message="시스템 오류"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      {/* 현재 모드 정보 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="현재 시스템 모드">
            <Row gutter={[16, 16]} align="middle">
              <Col span={8}>
                <Statistic
                  title="현재 모드"
                  value={systemMode}
                  valueStyle={{ color: getModeColor(systemMode) }}
                  prefix={<SettingOutlined />}
                />
              </Col>
              <Col span={16}>
                <Text>{getModeDescription(systemMode)}</Text>
                <br />
                <Text type="secondary">
                  모드 전환을 위해 아래 버튼을 사용하세요
                </Text>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 모드 전환 버튼 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="모드 전환">
            <Space wrap>
              <Button 
                type="primary" 
                onClick={() => handleModeSwitch('PRIME')}
                disabled={systemMode === 'PRIME'}
              >
                PRIME
              </Button>
              <Button 
                type="primary" 
                onClick={() => handleModeSwitch('ORACLE')}
                disabled={systemMode === 'ORACLE'}
              >
                ORACLE
              </Button>
              <Button 
                type="primary" 
                onClick={() => handleModeSwitch('LATTICE')}
                disabled={systemMode === 'LATTICE'}
              >
                LATTICE
              </Button>
              <Button 
                type="primary" 
                onClick={() => handleModeSwitch('RHYTHM')}
                disabled={systemMode === 'RHYTHM'}
              >
                RHYTHM
              </Button>
              <Button 
                type="primary" 
                onClick={() => handleModeSwitch('COST-GUARD')}
                disabled={systemMode === 'COST-GUARD'}
              >
                COST-GUARD
              </Button>
              <Button 
                danger 
                onClick={() => handleModeSwitch('ZERO')}
                disabled={systemMode === 'ZERO'}
              >
                ZERO
              </Button>
            </Space>
          </Card>
        </Col>
      </Row>

      {/* 시스템 통계 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="시스템 신뢰도"
              value={(systemStatus.confidence * 100).toFixed(1)}
              suffix="%"
              valueStyle={{ color: getConfidenceColor(systemStatus.confidence) }}
              prefix={<CheckCircleOutlined />}
            />
            <Progress
              percent={systemStatus.confidence * 100}
              status={getConfidenceStatus(systemStatus.confidence)}
              size="small"
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="창고 수"
              value={systemStatus.warehouse_count || 0}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="컨테이너 수"
              value={systemStatus.container_count || 0}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="송장 수"
              value={systemStatus.invoice_count || 0}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 상세 시스템 정보 */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card 
            title="상세 시스템 정보"
            extra={
              <Button 
                icon={<ReloadOutlined />} 
                onClick={fetchSystemStatus}
                loading={loading}
              >
                새로고침
              </Button>
            }
          >
            <Descriptions bordered column={2}>
              <Descriptions.Item label="시스템 버전">
                {systemStatus.version || '3.4.0'}
              </Descriptions.Item>
              <Descriptions.Item label="현재 모드">
                <Tag color={getModeColor(systemMode)}>{systemMode}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="시스템 신뢰도">
                <Tag color={getConfidenceColor(systemStatus.confidence)}>
                  {(systemStatus.confidence * 100).toFixed(1)}%
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="마지막 업데이트">
                {systemStatus.timestamp ? new Date(systemStatus.timestamp).toLocaleString() : 'N/A'}
              </Descriptions.Item>
              <Descriptions.Item label="데이터베이스 상태">
                <Tag color="green">연결됨</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="API 상태">
                <Tag color="green">정상</Tag>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SystemStatus;









