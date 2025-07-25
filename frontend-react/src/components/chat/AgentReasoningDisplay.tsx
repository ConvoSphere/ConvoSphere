import React, { useState } from 'react';
import { Collapse, Card, Tag, Progress, Space, Typography, Divider } from 'antd';
import { 
  BulbOutlined, 
  CheckCircleOutlined, 
  ClockCircleOutlined,
  EyeOutlined,
  EyeInvisibleOutlined
} from '@ant-design/icons';
import { useTranslation } from 'react-i18next';

const { Panel } = Collapse;
const { Text, Paragraph } = Typography;

interface ReasoningStep {
  step: number;
  thought: string;
  confidence: number;
  evidence: string[];
  conclusion?: string;
  created_at: string;
}

interface AgentReasoningDisplayProps {
  reasoningProcess: ReasoningStep[];
  modeDecision?: {
    current_mode: string;
    recommended_mode: string;
    reason: string;
    confidence: number;
    complexity_score: number;
    context_relevance: number;
  };
  visible?: boolean;
  onToggleVisibility?: (visible: boolean) => void;
  className?: string;
}

const AgentReasoningDisplay: React.FC<AgentReasoningDisplayProps> = ({
  reasoningProcess,
  modeDecision,
  visible = true,
  onToggleVisibility,
  className = '',
}) => {
  const { t } = useTranslation();
  const [expandedSteps, setExpandedSteps] = useState<number[]>([]);

  if (!reasoningProcess || reasoningProcess.length === 0) {
    return null;
  }

  const toggleStepExpansion = (stepNumber: number) => {
    setExpandedSteps(prev => 
      prev.includes(stepNumber) 
        ? prev.filter(s => s !== stepNumber)
        : [...prev, stepNumber]
    );
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const getConfidenceText = (confidence: number) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  return (
    <div className={`agent-reasoning-display ${className}`}>
      {/* Header with visibility toggle */}
      <div className="reasoning-header">
        <Space>
          <BulbOutlined />
          <Text strong>{t('chat.agentReasoning.title')}</Text>
          {onToggleVisibility && (
            <button
              type="button"
              className="visibility-toggle"
              onClick={() => onToggleVisibility(!visible)}
            >
              {visible ? <EyeInvisibleOutlined /> : <EyeOutlined />}
            </button>
          )}
        </Space>
      </div>

      {visible && (
        <>
          {/* Mode Decision Summary */}
          {modeDecision && (
            <Card size="small" className="mode-decision-card">
              <div className="mode-decision-summary">
                <Space direction="vertical" size="small" style={{ width: '100%' }}>
                  <div className="decision-header">
                    <Text strong>{t('chat.agentReasoning.modeDecision')}</Text>
                    <Tag color={modeDecision.current_mode === modeDecision.recommended_mode ? 'green' : 'orange'}>
                      {modeDecision.current_mode} → {modeDecision.recommended_mode}
                    </Tag>
                  </div>
                  
                  <div className="decision-metrics">
                    <Space wrap>
                      <div className="metric">
                        <Text type="secondary">{t('chat.agentReasoning.confidence')}</Text>
                        <Progress 
                          percent={Math.round(modeDecision.confidence * 100)} 
                          size="small" 
                          status={getConfidenceColor(modeDecision.confidence) as any}
                        />
                      </div>
                      
                      <div className="metric">
                        <Text type="secondary">{t('chat.agentReasoning.complexity')}</Text>
                        <Progress 
                          percent={Math.round(modeDecision.complexity_score * 100)} 
                          size="small" 
                          strokeColor="#722ed1"
                        />
                      </div>
                      
                      <div className="metric">
                        <Text type="secondary">{t('chat.agentReasoning.contextRelevance')}</Text>
                        <Progress 
                          percent={Math.round(modeDecision.context_relevance * 100)} 
                          size="small" 
                          strokeColor="#13c2c2"
                        />
                      </div>
                    </Space>
                  </div>
                  
                  <div className="decision-reason">
                    <Text type="secondary">{t('chat.agentReasoning.reason')}: </Text>
                    <Text>{modeDecision.reason}</Text>
                  </div>
                </Space>
              </div>
            </Card>
          )}

          <Divider style={{ margin: '12px 0' }} />

          {/* Reasoning Steps */}
          <Collapse 
            ghost 
            size="small"
            activeKey={expandedSteps}
            onChange={(keys) => setExpandedSteps(keys.map(k => Number(k)))}
          >
            {reasoningProcess.map((step, index) => (
              <Panel
                key={step.step}
                header={
                  <div className="reasoning-step-header">
                    <Space>
                      <Text strong>Step {step.step}</Text>
                      <Tag color={getConfidenceColor(step.confidence)}>
                        {getConfidenceText(step.confidence)} Confidence
                      </Tag>
                      <ClockCircleOutlined />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {formatTimestamp(step.created_at)}
                      </Text>
                    </Space>
                  </div>
                }
                className="reasoning-step-panel"
              >
                <div className="reasoning-step-content">
                  <div className="thought-section">
                    <Text strong>{t('chat.agentReasoning.thought')}:</Text>
                    <Paragraph style={{ marginTop: 8 }}>
                      {step.thought}
                    </Paragraph>
                  </div>

                  {step.evidence && step.evidence.length > 0 && (
                    <div className="evidence-section">
                      <Text strong>{t('chat.agentReasoning.evidence')}:</Text>
                      <ul style={{ marginTop: 8, marginBottom: 8 }}>
                        {step.evidence.map((evidence, idx) => (
                          <li key={idx}>
                            <Text>{evidence}</Text>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {step.conclusion && (
                    <div className="conclusion-section">
                      <Text strong>{t('chat.agentReasoning.conclusion')}:</Text>
                      <Paragraph style={{ marginTop: 8 }}>
                        {step.conclusion}
                      </Paragraph>
                    </div>
                  )}

                  <div className="step-metrics">
                    <Space>
                      <div className="metric">
                        <Text type="secondary">{t('chat.agentReasoning.confidence')}</Text>
                        <Progress 
                          percent={Math.round(step.confidence * 100)} 
                          size="small" 
                          status={getConfidenceColor(step.confidence) as any}
                        />
                      </div>
                    </Space>
                  </div>
                </div>
              </Panel>
            ))}
          </Collapse>

          {/* Summary */}
          <div className="reasoning-summary">
            <Space>
              <CheckCircleOutlined style={{ color: '#52c41a' }} />
              <Text type="secondary">
                {t('chat.agentReasoning.completed', { steps: reasoningProcess.length })}
              </Text>
            </Space>
          </div>
        </>
      )}
    </div>
  );
};

export default AgentReasoningDisplay; 