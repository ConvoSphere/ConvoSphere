import React, { useState } from 'react';
import { Alert, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import { useThemeStore } from '../store/themeStore';
import ModernCard from '../components/ModernCard';
import ModernButton from '../components/ModernButton';
import ModernInput from '../components/ModernInput';
import ModernForm, { ModernFormItem } from '../components/ModernForm';

const { Title, Text } = Typography;

const Register: React.FC = () => {
  const { t } = useTranslation();
  const register = useAuthStore((s) => s.register);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const navigate = useNavigate();
  const { getCurrentColors } = useThemeStore();
  const colors = getCurrentColors();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const onFinish = async (values: { username: string; password: string; email: string; confirmEmail: string }) => {
    setLoading(true);
    setError(null);
    try {
      await register(values.username, values.password, values.email);
      setSuccess(true);
    } catch {
      setError(t('auth.register.failed'));
    } finally {
      setLoading(false);
    }
  };

  if (isAuthenticated) {
    navigate('/');
    return null;
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      background: colors.colorGradientSecondary,
      padding: '24px'
    }}>
      <ModernCard 
        variant="elevated" 
        size="xl"
        style={{ 
          maxWidth: 480, 
          width: '100%',
          backdropFilter: 'blur(10px)',
          backgroundColor: 'rgba(255, 255, 255, 0.95)'
        }}
        className="stagger-children"
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={2} style={{ 
            color: colors.colorTextBase, 
            marginBottom: 8,
            fontSize: '2.5rem',
            fontWeight: 700
          }}>
            {t('auth.register.title')}
          </Title>
          <Text type="secondary" style={{ fontSize: '16px' }}>
            {t('auth.register.subtitle')}
          </Text>
        </div>

        {success ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Alert
              type="success"
              message={t('auth.register.success')}
              showIcon
              style={{ 
                marginBottom: 24, 
                borderRadius: '12px',
                border: 'none'
              }}
            />
            <ModernButton
              variant="primary"
              size="lg"
              onClick={() => navigate('/login')}
              style={{ marginTop: 16 }}
            >
              {t('auth.login.button')}
            </ModernButton>
          </div>
        ) : (
          <>
            {error && (
              <Alert 
                type="error" 
                message={error} 
                showIcon 
                style={{ 
                  marginBottom: 24, 
                  borderRadius: '12px',
                  border: 'none'
                }} 
              />
            )}
            
            <ModernForm 
              variant="minimal" 
              size="lg"
              onFinish={onFinish}
              aria-label={t('auth.register.title')}
            >
              <ModernFormItem 
                label={t('auth.login.username')} 
                required
              >
                <ModernInput
                  name="username"
                  variant="filled"
                  size="lg"
                  autoFocus
                  aria-label={t('auth.login.username')}
                  placeholder={t('auth.login.username_placeholder')}
                />
              </ModernFormItem>
              
              <ModernFormItem 
                label={t('auth.register.email')} 
                required
              >
                <ModernInput
                  name="email"
                  type="email"
                  variant="filled"
                  size="lg"
                  aria-label={t('auth.register.email')}
                  placeholder={t('auth.register.email_placeholder')}
                />
              </ModernFormItem>
              
              <ModernFormItem 
                label={t('auth.register.confirm_email')} 
                required
              >
                <ModernInput
                  name="confirmEmail"
                  type="email"
                  variant="filled"
                  size="lg"
                  aria-label={t('auth.register.confirm_email')}
                  placeholder={t('auth.register.confirm_email_placeholder')}
                />
              </ModernFormItem>
              
              <ModernFormItem 
                label={t('auth.login.password')} 
                required
              >
                <ModernInput
                  name="password"
                  type="password"
                  variant="filled"
                  size="lg"
                  showPasswordToggle
                  aria-label={t('auth.login.password')}
                  placeholder={t('auth.login.password_placeholder')}
                />
              </ModernFormItem>
              
              <ModernFormItem>
                <ModernButton 
                  variant="gradient" 
                  size="lg" 
                  htmlType="submit" 
                  loading={loading} 
                  style={{ 
                    width: '100%',
                    height: '56px',
                    fontSize: '18px',
                    fontWeight: 600
                  }}
                  aria-label={t('auth.register.button')}
                >
                  {t('auth.register.button')}
                </ModernButton>
              </ModernFormItem>
            </ModernForm>
            
            <div style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              marginTop: 24,
              paddingTop: 24,
              borderTop: '1px solid var(--colorBorder)'
            }}>
              <ModernButton
                variant="ghost"
                size="sm"
                onClick={() => navigate('/login')}
                aria-label={t('auth.login.link')}
              >
                {t('auth.login.link')}
              </ModernButton>
            </div>
          </>
        )}
      </ModernCard>
    </div>
  );
};

export default Register; 