import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Card, Alert, Spinner, Badge, Switch, Modal } from './ui';
import { getSSOProviders } from '../services/auth';
import { useAuthStore } from '../stores/authStore';

interface SSOProvider {
  id: string;
  name: string;
  type: string;
  icon: string;
  login_url: string;
  enabled?: boolean;
  configured?: boolean;
  metadata_url?: string;
}

interface SSOProviderManagementProps {
  onProviderUpdate?: () => void;
}

export const SSOProviderManagement: React.FC<SSOProviderManagementProps> = ({
  onProviderUpdate
}) => {
  const { t } = useTranslation();
  const [providers, setProviders] = useState<SSOProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showConfigModal, setShowConfigModal] = useState<string | null>(null);
  const [configData, setConfigData] = useState<any>(null);
  
  const { user } = useAuthStore();

  useEffect(() => {
    loadSSOProviders();
  }, []);

  const loadSSOProviders = async () => {
    try {
      setLoading(true);
      const response = await getSSOProviders();
      setProviders(response);
    } catch (err) {
      setError(t('sso.load_failed'));
    } finally {
      setLoading(false);
    }
  };

  const handleToggleProvider = async (providerId: string, enabled: boolean) => {
    try {
      setUpdating(providerId);
      setError(null);
      setSuccess(null);

      // This would call the backend API to toggle provider status
      // await toggleSSOProvider(providerId, enabled);
      
      setSuccess(`${providerId} ${enabled ? t('sso.enabled') : t('sso.disabled')} ${t('sso.successfully')}`);
      onProviderUpdate?.();
      
      // Reload providers to update status
      await loadSSOProviders();
      
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || t('sso.update_failed');
      setError(errorMessage);
    } finally {
      setUpdating(null);
    }
  };

  const handleViewConfig = async (providerId: string) => {
    try {
      // This would fetch provider configuration from backend
      // const config = await getSSOProviderConfig(providerId);
      const mockConfig = {
        client_id: '***hidden***',
        redirect_uri: 'https://example.com/callback',
        scopes: ['openid', 'email', 'profile'],
        metadata_url: 'https://example.com/metadata'
      };
      
      setConfigData(mockConfig);
      setShowConfigModal(providerId);
    } catch (err) {
      setError(t('sso.config_load_failed'));
    }
  };

  const getProviderIcon = (provider: SSOProvider) => {
    const iconMap: Record<string, string> = {
      google: '🔍',
      microsoft: '🪟',
      github: '🐙',
      saml: '🔐',
      oidc: '🔑'
    };
    return iconMap[provider.id] || '🔗';
  };

  const getStatusBadge = (provider: SSOProvider) => {
    if (!provider.configured) {
      return <Badge className="bg-red-100 text-red-800">{t('sso.status.not_configured')}</Badge>;
    }
    if (provider.enabled) {
      return <Badge className="bg-green-100 text-green-800">{t('sso.status.active')}</Badge>;
    }
    return <Badge className="bg-yellow-100 text-yellow-800">{t('sso.status.disabled')}</Badge>;
  };

  const getProviderDescription = (provider: SSOProvider) => {
    const descriptions: Record<string, string> = {
      google: 'Google OAuth2 for Gmail and Google Workspace users',
      microsoft: 'Microsoft Azure AD for enterprise users',
      github: 'GitHub OAuth for developers',
      saml: 'SAML 2.0 for enterprise SSO integration',
      oidc: 'OpenID Connect for modern identity providers'
    };
    return descriptions[provider.id] || 'External authentication provider';
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center">
          <Spinner size="lg" />
          <span className="ml-2">{t('sso.loading_providers')}</span>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          {t('sso.title')}
        </h2>
        <p className="text-gray-600">
          {t('sso.description')}
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <span>{error}</span>
        </Alert>
      )}

      {success && (
        <Alert variant="default" className="border-green-200 bg-green-50">
          <span className="text-green-800">{success}</span>
        </Alert>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {providers.map((provider) => (
          <Card key={provider.id} className="p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{getProviderIcon(provider)}</span>
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {provider.name}
                  </h3>
                  <p className="text-sm text-gray-500 capitalize">
                    {provider.type}
                  </p>
                </div>
              </div>
              {getStatusBadge(provider)}
            </div>

            <p className="text-sm text-gray-600 mb-4">
              {getProviderDescription(provider)}
            </p>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">
                  {t('sso.status.label')}
                </span>
                <Switch
                  checked={provider.enabled || false}
                  onCheckedChange={(enabled) => handleToggleProvider(provider.id, enabled)}
                  disabled={!provider.configured || updating === provider.id}
                />
              </div>

              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleViewConfig(provider.id)}
                  className="flex-1"
                >
                  {t('sso.actions.view_config')}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.open(provider.login_url, '_blank')}
                  className="flex-1"
                >
                  {t('sso.actions.test_login')}
                </Button>
              </div>

              {updating === provider.id && (
                <div className="flex items-center justify-center text-sm text-gray-500">
                  <Spinner size="sm" className="mr-2" />
                  {t('sso.updating')}
                </div>
              )}
            </div>
          </Card>
        ))}
      </div>

      {providers.length === 0 && (
        <Card className="p-6 text-center">
          <p className="text-gray-500">
            {t('sso.no_providers')}
          </p>
        </Card>
      )}

      {/* Configuration Modal */}
      <Modal
        isOpen={showConfigModal !== null}
        onClose={() => setShowConfigModal(null)}
        title={`${showConfigModal?.toUpperCase()} ${t('sso.configuration')}`}
      >
        {configData && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium text-gray-700">{t('sso.configuration.client_id')}</span>
                <p className="text-gray-600 font-mono">{configData.client_id}</p>
              </div>
              <div>
                <span className="font-medium text-gray-700">{t('sso.configuration.redirect_uri')}</span>
                <p className="text-gray-600 font-mono">{configData.redirect_uri}</p>
              </div>
              <div>
                <span className="font-medium text-gray-700">{t('sso.configuration.scopes')}</span>
                <p className="text-gray-600">{configData.scopes.join(', ')}</p>
              </div>
              {configData.metadata_url && (
                <div>
                  <span className="font-medium text-gray-700">{t('sso.configuration.metadata_url')}</span>
                  <p className="text-gray-600 font-mono">{configData.metadata_url}</p>
                </div>
              )}
            </div>
            
            <div className="flex justify-end space-x-2">
              <Button
                variant="outline"
                onClick={() => setShowConfigModal(null)}
              >
                {t('common.close')}
              </Button>
              <Button
                onClick={() => {
                  // Handle edit configuration
                  setShowConfigModal(null);
                }}
              >
                {t('sso.actions.edit_config')}
              </Button>
            </div>
          </div>
        )}
      </Modal>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-2">
          {t('sso.guide.title')}
        </h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• {t('sso.guide.enable_disable')}</li>
          <li>• {t('sso.guide.view_config')}</li>
          <li>• {t('sso.guide.test_login')}</li>
          <li>• {t('sso.guide.configure_env')}</li>
        </ul>
      </div>
    </div>
  );
};