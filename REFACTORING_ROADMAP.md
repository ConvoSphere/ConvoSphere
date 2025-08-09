# Refactoring Roadmap - Praktische Umsetzung

## Phase 1: Sofortige Maßnahmen (Woche 1-2)

### Woche 1: Backend CLI Refactoring

#### Tag 1-2: Vorbereitung und Setup
```bash
# Neue Verzeichnisstruktur erstellen
mkdir -p backend/cli/{commands,utils}
mkdir -p backend/cli/commands/{database,user,backup,monitoring,assistant,dev}
mkdir -p backend/cli/utils/{output,validation,helpers}
```

#### Tag 3-4: CLI Commands auslagern
**Datei: `backend/cli/commands/database.py`**
```python
from backend.cli.utils.output import print_success, print_error, print_info
from backend.cli.utils.validation import validate_revision

class DatabaseCommands:
    def migrate(self) -> None:
        """Run Alembic migrations."""
        # Ausgelagerte Logik aus admin.py
        
    def status(self) -> None:
        """Show migration status."""
        # Ausgelagerte Logik aus admin.py
        
    def downgrade(self, revision: str) -> None:
        """Downgrade to specific revision."""
        # Ausgelagerte Logik aus admin.py
```

**Datei: `backend/cli/commands/user.py`**
```python
from backend.cli.utils.output import print_success, print_error
from backend.cli.utils.validation import validate_email, validate_username

class UserCommands:
    def create_admin(self) -> None:
        """Create admin user."""
        # Ausgelagerte Logik aus admin.py
        
    def create_secure(self) -> None:
        """Create secure user."""
        # Ausgelagerte Logik aus admin.py
        
    def list(self) -> None:
        """List all users."""
        # Ausgelagerte Logik aus admin.py
```

#### Tag 5: CLI Main Refactoring
**Datei: `backend/cli/main.py`**
```python
import argparse
from backend.cli.commands.database import DatabaseCommands
from backend.cli.commands.user import UserCommands
from backend.cli.commands.backup import BackupCommands

class AdminCLI:
    def __init__(self):
        self.commands = {
            'db': DatabaseCommands(),
            'user': UserCommands(),
            'backup': BackupCommands(),
        }
    
    def run(self, args):
        command = args.command
        subcommand = args.subcommand
        
        if command in self.commands:
            handler = getattr(self.commands[command], subcommand, None)
            if handler:
                handler(**vars(args))
            else:
                print_error(f"Unknown subcommand: {subcommand}")
        else:
            print_error(f"Unknown command: {command}")

def main():
    parser = argparse.ArgumentParser(description="ChatAssistant Admin CLI")
    # Argument-Parsing-Logik
    args = parser.parse_args()
    
    cli = AdminCLI()
    cli.run(args)
```

### Woche 2: AI Service Refactoring

#### Tag 1-2: Service-Struktur erstellen
```bash
mkdir -p backend/app/services/ai/{core,providers,rag,tools}
```

#### Tag 3-4: Core-Komponenten auslagern
**Datei: `backend/app/services/ai/core/cost_tracker.py`**
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class CostInfo:
    model: str
    tokens_used: int
    cost_usd: float
    timestamp: datetime
    user_id: str | None = None
    conversation_id: str | None = None

class CostTracker:
    def __init__(self):
        self.costs: List[CostInfo] = []
        self.total_cost = 0.0
        self.total_tokens = 0
    
    def add_cost(self, cost_info: CostInfo):
        # Ausgelagerte Logik aus ai_service.py
```

**Datei: `backend/app/services/ai/core/response.py`**
```python
from dataclasses import dataclass
from typing import Any, List, Optional

@dataclass
class AIResponse:
    content: str
    message_type: str = "text"
    metadata: Optional[dict[str, Any]] = None
    tool_calls: Optional[List[dict[str, Any]]] = None
    context_used: Optional[List[dict[str, Any]]] = None
```

#### Tag 5: Provider-Pattern implementieren
**Datei: `backend/app/services/ai/providers/base.py`**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseProvider(ABC):
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def get_embeddings(
        self,
        text: str,
        model: str
    ) -> List[float]:
        pass
```

**Datei: `backend/app/services/ai/providers/litellm_provider.py`**
```python
from backend.app.services.ai.providers.base import BaseProvider
import litellm

class LiteLLMProvider(BaseProvider):
    def __init__(self):
        self._setup_litellm()
    
    async def chat_completion(self, messages, **kwargs):
        # Ausgelagerte LiteLLM-Logik
```

## Phase 2: Frontend Refactoring (Woche 3-4)

### Woche 3: Admin Page Refactoring

#### Tag 1-2: Custom Hooks erstellen
**Datei: `frontend-react/src/pages/admin/hooks/useUserManagement.ts`**
```typescript
import { useState, useCallback } from 'react';
import { message } from 'antd';
import { User } from '../types/admin.types';

export const useUserManagement = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(false);
    const [userModalVisible, setUserModalVisible] = useState(false);
    const [selectedUser, setSelectedUser] = useState<User | null>(null);

    const loadUsers = useCallback(async () => {
        setLoading(true);
        try {
            // API-Call-Logik
            setUsers(users);
        } catch (error) {
            message.error('Failed to load users');
        } finally {
            setLoading(false);
        }
    }, []);

    const handleUserSave = useCallback(async (userData: Partial<User>) => {
        // User-Save-Logik
    }, []);

    return {
        users,
        loading,
        userModalVisible,
        selectedUser,
        setUserModalVisible,
        setSelectedUser,
        loadUsers,
        handleUserSave,
    };
};
```

#### Tag 3-4: Komponenten aufteilen
**Datei: `frontend-react/src/pages/admin/components/UserManagement.tsx`**
```typescript
import React from 'react';
import { Table, Button, Space } from 'antd';
import { useUserManagement } from '../hooks/useUserManagement';
import { User } from '../types/admin.types';

const UserManagement: React.FC = () => {
    const {
        users,
        loading,
        userModalVisible,
        selectedUser,
        setUserModalVisible,
        setSelectedUser,
        loadUsers,
        handleUserSave,
    } = useUserManagement();

    // UI-Logik für User-Management
    return (
        <div>
            {/* User-Management UI */}
        </div>
    );
};

export default UserManagement;
```

#### Tag 5: Hauptkomponente vereinfachen
**Datei: `frontend-react/src/pages/admin/Admin.tsx`**
```typescript
import React from 'react';
import { Tabs } from 'antd';
import UserManagement from './components/UserManagement';
import SystemConfig from './components/SystemConfig';
import SystemStats from './components/SystemStats';
import AuditLogs from './components/AuditLogs';

const { TabPane } = Tabs;

const Admin: React.FC = () => {
    return (
        <div>
            <Tabs defaultActiveKey="users">
                <TabPane tab="Users" key="users">
                    <UserManagement />
                </TabPane>
                <TabPane tab="System Config" key="config">
                    <SystemConfig />
                </TabPane>
                <TabPane tab="Statistics" key="stats">
                    <SystemStats />
                </TabPane>
                <TabPane tab="Audit Logs" key="logs">
                    <AuditLogs />
                </TabPane>
            </Tabs>
        </div>
    );
};

export default Admin;
```

### Woche 4: App.tsx Refactoring

#### Tag 1-2: Routing auslagern
**Datei: `frontend-react/src/routing/AppRouter.tsx`**
```typescript
import React, { Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { routes } from './routes';
import LoadingSpinner from '../components/LoadingSpinner';

const AppRouter: React.FC = () => {
    return (
        <Suspense fallback={<LoadingSpinner />}>
            <Routes>
                {routes.map(({ path, component: Component }) => (
                    <Route
                        key={path}
                        path={path}
                        element={<Component />}
                    />
                ))}
            </Routes>
        </Suspense>
    );
};

export default AppRouter;
```

**Datei: `frontend-react/src/routing/routes.ts`**
```typescript
import { lazy } from 'react';

// Lazy-Loading-Komponenten
const HomePage = lazy(() => import('../pages/Home'));
const DashboardPage = lazy(() => import('../pages/Dashboard'));
const ChatPage = lazy(() => import('../pages/Chat'));
const AdminPage = lazy(() => import('../pages/admin/Admin'));

export const routes = [
    { path: '/', component: HomePage },
    { path: '/dashboard', component: DashboardPage },
    { path: '/chat', component: ChatPage },
    { path: '/admin', component: AdminPage },
];
```

#### Tag 3-4: Provider auslagern
**Datei: `frontend-react/src/providers/AppProviders.tsx`**
```typescript
import React from 'react';
import { ConfigProvider } from 'antd';
import { I18nextProvider } from 'react-i18next';
import { BrowserRouter } from 'react-router-dom';
import i18n from '../i18n';
import { simpleTheme } from '../config/theme';

interface AppProvidersProps {
    children: React.ReactNode;
}

const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
    return (
        <I18nextProvider i18n={i18n}>
            <ConfigProvider theme={simpleTheme}>
                <BrowserRouter>
                    {children}
                </BrowserRouter>
            </ConfigProvider>
        </I18nextProvider>
    );
};

export default AppProviders;
```

#### Tag 5: App.tsx vereinfachen
**Datei: `frontend-react/src/App.tsx`**
```typescript
import React from 'react';
import AppProviders from './providers/AppProviders';
import AppRouter from './routing/AppRouter';
import ErrorBoundary from './components/ErrorBoundary';
import { useAppInit } from './initialization/useAppInit';

const App: React.FC = () => {
    const { initialized } = useAppInit();

    if (!initialized) {
        return <LoadingSpinner />;
    }

    return (
        <ErrorBoundary>
            <AppProviders>
                <AppRouter />
            </AppProviders>
        </ErrorBoundary>
    );
};

export default App;
```

## Phase 3: Monitoring und Tests (Woche 5-6)

### Woche 5: Monitoring Refactoring

#### Tag 1-2: Core-Komponenten auslagern
**Datei: `backend/app/monitoring/core/metrics.py`**
```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

@dataclass
class Metric:
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetricsCollector:
    def __init__(self, max_metrics: int = 10000, retention_hours: int = 24):
        self.max_metrics = max_metrics
        self.retention_hours = retention_hours
        self.metrics: List[Metric] = []
    
    def record_metric(self, name: str, value: float, metric_type: MetricType, **kwargs):
        # Ausgelagerte Metriken-Logik
```

#### Tag 3-4: Collectors auslagern
**Datei: `backend/app/monitoring/collectors/system_monitor.py`**
```python
import psutil
from typing import Dict

class SystemMonitor:
    def __init__(self):
        pass
    
    def get_system_metrics(self) -> Dict[str, float]:
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
        }
    
    def get_detailed_system_info(self) -> Dict[str, Any]:
        # Ausgelagerte System-Monitoring-Logik
```

#### Tag 5: Hauptmonitor vereinfachen
**Datei: `backend/app/monitoring/performance_monitor.py`**
```python
from backend.app.monitoring.core.metrics import MetricsCollector
from backend.app.monitoring.core.alerts import AlertManager
from backend.app.monitoring.collectors.system_monitor import SystemMonitor
from backend.app.monitoring.collectors.database_monitor import DatabaseMonitor

class PerformanceMonitor:
    def __init__(self, db):
        self.metrics = MetricsCollector()
        self.alerts = AlertManager()
        self.system_monitor = SystemMonitor()
        self.database_monitor = DatabaseMonitor(db)
    
    async def start_monitoring(self):
        # Vereinfachte Monitoring-Logik
```

### Woche 6: Test-Refactoring

#### Tag 1-2: Test-Helpers erstellen
**Datei: `tests/helpers/user_helpers.py`**
```python
from unittest.mock import MagicMock
from backend.app.models.user import User, UserRole

def create_mock_user(
    user_id: str = "user-123",
    email: str = "test@example.com",
    role: UserRole = UserRole.USER
) -> MagicMock:
    mock_user = MagicMock()
    mock_user.id = user_id
    mock_user.email = email
    mock_user.role = role
    mock_user.has_permission.return_value = True
    return mock_user

def create_test_user_data(**kwargs) -> dict:
    default_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "user"
    }
    default_data.update(kwargs)
    return default_data
```

#### Tag 3-4: Test-Dateien aufteilen
**Datei: `tests/unit/backend/api/users/test_user_crud.py`**
```python
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from tests.helpers.user_helpers import create_mock_user, create_test_user_data

class TestUserCRUD:
    @pytest.mark.fast
    def test_create_user_success(self, client: TestClient, test_admin_headers: dict):
        # Ausgelagerte CRUD-Tests
        
    @pytest.mark.fast
    def test_get_user_success(self, client: TestClient, test_admin_headers: dict):
        # Ausgelagerte CRUD-Tests
        
    @pytest.mark.fast
    def test_update_user_success(self, client: TestClient, test_admin_headers: dict):
        # Ausgelagerte CRUD-Tests
```

#### Tag 5: Test-Konfiguration verbessern
**Datei: `tests/conftest.py`**
```python
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

@pytest.fixture
def mock_user_service():
    return MagicMock()

@pytest.fixture
def mock_ai_service():
    return MagicMock()

@pytest.fixture
def test_client(mock_user_service, mock_ai_service):
    # Test-Client mit gemockten Services
```

## Phase 4: Dependency Injection (Woche 7-8)

### Woche 7: DI-Container Setup

#### Tag 1-2: Container-Konfiguration
**Datei: `backend/app/core/container.py`**
```python
from dependency_injector import containers, providers
from backend.app.services.ai.ai_service import AIService
from backend.app.services.user_service import UserService
from backend.app.monitoring.performance_monitor import PerformanceMonitor

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    
    # Database
    database = providers.Singleton(Database, url=config.database.url)
    
    # Services
    ai_service = providers.Singleton(AIService)
    user_service = providers.Singleton(UserService, db=database)
    performance_monitor = providers.Singleton(PerformanceMonitor, db=database)
```

#### Tag 3-4: Service-Interfaces
**Datei: `backend/app/services/interfaces/ai_service.py`**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AIServiceInterface(ABC):
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def get_embeddings(
        self,
        text: str,
        model: str
    ) -> List[float]:
        pass
```

#### Tag 5: Service-Implementation
**Datei: `backend/app/services/ai/ai_service.py`**
```python
from backend.app.services.interfaces.ai_service import AIServiceInterface
from backend.app.services.ai.core.cost_tracker import CostTracker
from backend.app.services.ai.providers.base import BaseProvider

class AIService(AIServiceInterface):
    def __init__(self, provider: BaseProvider):
        self.provider = provider
        self.cost_tracker = CostTracker()
    
    async def chat_completion(self, messages, **kwargs):
        # Vereinfachte Implementation
```

### Woche 8: Integration und Testing

#### Tag 1-2: Integration Tests
**Datei: `tests/integration/test_ai_service_integration.py`**
```python
import pytest
from backend.app.core.container import Container
from backend.app.services.ai.ai_service import AIService

class TestAIServiceIntegration:
    @pytest.fixture
    def container(self):
        container = Container()
        container.config.from_dict({
            "ai": {
                "provider": "litellm",
                "default_model": "gpt-3.5-turbo"
            }
        })
        return container
    
    def test_ai_service_injection(self, container):
        ai_service = container.ai_service()
        assert isinstance(ai_service, AIService)
```

#### Tag 3-4: Performance Tests
**Datei: `tests/performance/test_refactored_performance.py`**
```python
import pytest
import time
from backend.app.core.container import Container

class TestRefactoredPerformance:
    def test_ai_service_performance(self):
        container = Container()
        ai_service = container.ai_service()
        
        start_time = time.time()
        # Performance-Test-Logik
        end_time = time.time()
        
        assert (end_time - start_time) < 1.0  # Max 1 Sekunde
```

#### Tag 5: Dokumentation und Review
- Code-Review aller Refactoring-Änderungen
- Dokumentation der neuen Architektur
- Team-Schulung für neue Patterns

## Erfolgsmessung und Monitoring

### Wöchentliche Metriken
```bash
# Dateigröße-Analyse
find . -name "*.py" -o -name "*.ts" -o -name "*.tsx" | xargs wc -l | sort -nr

# Code-Duplikation-Analyse
# (Tool: jscpd oder ähnliches)

# Test-Coverage
pytest --cov=backend --cov=frontend-react --cov-report=html
```

### Qualitätsmetriken
- **Dateigröße**: Ziel: <300 Zeilen pro Datei
- **Komplexität**: Ziel: <10 Cyclomatic Complexity
- **Duplikation**: Ziel: <5% Code-Duplikation
- **Test-Coverage**: Ziel: >90%

### Rollback-Plan
1. **Feature Branches**: Alle Änderungen in separaten Branches
2. **Staging Environment**: Vollständige Tests vor Production
3. **Gradual Rollout**: Schrittweise Deployment
4. **Monitoring**: Kontinuierliche Überwachung der Performance

## Nächste Schritte

1. **Team-Briefing**: Präsentation der Roadmap
2. **Pilot-Projekt**: Start mit CLI-Refactoring
3. **Code-Review-Prozess**: Einführung von Review-Richtlinien
4. **CI/CD-Pipeline**: Automatisierte Qualitätsprüfungen
5. **Dokumentation**: Kontinuierliche Aktualisierung der Architektur-Dokumentation