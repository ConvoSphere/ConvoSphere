import React, { useState, useEffect } from "react";
import { Button, Card, Alert, Spinner, Badge } from "./ui";
import { ssoLink, getSSOProviders } from "../services/auth";


interface SSOProvider {
  id: string;
  name: string;
  type: string;
  icon: string;
  login_url: string;
  linked?: boolean;
}

interface SSOAccountLinkingProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export const SSOAccountLinking: React.FC<SSOAccountLinkingProps> = ({
  onSuccess,
  onError,
}) => {
  const [providers, setProviders] = useState<SSOProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [linking, setLinking] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);



  useEffect(() => {
    loadSSOProviders();
  }, []);

  const loadSSOProviders = async () => {
    try {
      setLoading(true);
      const response = await getSSOProviders();
      setProviders(response);
    } catch (_err) {
      setError("Failed to load SSO providers");
      onError?.("Failed to load SSO providers");
    } finally {
      setLoading(false);
    }
  };

  const handleLinkAccount = async (providerId: string) => {
    try {
      setLinking(providerId);
      setError(null);
      setSuccess(null);

      await ssoLink(providerId);

      setSuccess(`Successfully linked account with ${providerId}`);
      onSuccess?.();

      // Reload providers to update linked status
      await loadSSOProviders();
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || "Failed to link account";
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setLinking(null);
    }
  };

  const getProviderIcon = (provider: SSOProvider) => {
    const iconMap: Record<string, string> = {
      google: "🔍",
      microsoft: "🪟",
      github: "🐙",
      saml: "🔐",
      oidc: "🔑",
    };
    return iconMap[provider.id] || "🔗";
  };

  const getProviderColor = (provider: SSOProvider) => {
    const colorMap: Record<string, string> = {
      google: "bg-red-100 text-red-800",
      microsoft: "bg-blue-100 text-blue-800",
      github: "bg-gray-100 text-gray-800",
      saml: "bg-purple-100 text-purple-800",
      oidc: "bg-green-100 text-green-800",
    };
    return colorMap[provider.id] || "bg-gray-100 text-gray-800";
  };

  if (loading) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center">
          <Spinner size="lg" />
          <span className="ml-2">Loading SSO providers...</span>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Link SSO Accounts
        </h2>
        <p className="text-gray-600">
          Connect your local account with external SSO providers for easier
          login.
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
              {provider.linked && (
                <Badge className={getProviderColor(provider)}>Linked</Badge>
              )}
            </div>

            <div className="space-y-3">
              {provider.linked ? (
                <div className="text-center">
                  <p className="text-sm text-green-600 mb-2">
                    ✓ Account linked successfully
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleLinkAccount(provider.id)}
                    disabled={linking === provider.id}
                  >
                    {linking === provider.id ? (
                      <>
                        <Spinner size="sm" className="mr-2" />
                        Relinking...
                      </>
                    ) : (
                      "Relink Account"
                    )}
                  </Button>
                </div>
              ) : (
                <Button
                  onClick={() => handleLinkAccount(provider.id)}
                  disabled={linking === provider.id}
                  className="w-full"
                >
                  {linking === provider.id ? (
                    <>
                      <Spinner size="sm" className="mr-2" />
                      Linking...
                    </>
                  ) : (
                    `Link with ${provider.name}`
                  )}
                </Button>
              )}
            </div>
          </Card>
        ))}
      </div>

      {providers.length === 0 && (
        <Card className="p-6 text-center">
          <p className="text-gray-500">
            No SSO providers are currently configured.
          </p>
        </Card>
      )}

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-semibold text-blue-900 mb-2">
          How Account Linking Works
        </h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Link your local account with SSO providers for easier login</li>
          <li>• You can still use your local password to login</li>
          <li>• SSO login will automatically use your linked account</li>
          <li>• You can unlink accounts at any time</li>
        </ul>
      </div>
    </div>
  );
};
