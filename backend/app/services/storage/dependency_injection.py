"""
Dependency injection system for storage providers.

This module provides a dependency injection container for storage services
to improve maintainability and testability.
"""

from typing import Dict, Any, Type, Optional, Callable
from dataclasses import dataclass
from loguru import logger

from .base import StorageProvider
from .config import StorageConfig
from .factory import StorageFactory
from .manager import StorageManager
from .connection_pool import StorageConnectionPool
from .batch_operations import StorageBatchManager


@dataclass
class ServiceDefinition:
    """Service definition for dependency injection."""
    service_type: Type
    factory: Callable
    singleton: bool = True
    instance: Optional[Any] = None


class StorageContainer:
    """Dependency injection container for storage services."""
    
    def __init__(self):
        self._services: Dict[str, ServiceDefinition] = {}
        self._factories: Dict[str, Callable] = {}
        self._instances: Dict[str, Any] = {}
        
        # Register default services
        self._register_default_services()
    
    def _register_default_services(self):
        """Register default storage services."""
        # Storage Factory
        self.register_service(
            "storage_factory",
            StorageFactory,
            lambda: StorageFactory(),
            singleton=True
        )
        
        # Connection Pool
        self.register_service(
            "connection_pool",
            StorageConnectionPool,
            lambda: StorageConnectionPool(),
            singleton=True
        )
        
        # Batch Manager
        self.register_service(
            "batch_manager",
            StorageBatchManager,
            lambda: StorageBatchManager(),
            singleton=True
        )
    
    def register_service(
        self,
        name: str,
        service_type: Type,
        factory: Callable,
        singleton: bool = True
    ):
        """Register a service in the container."""
        self._services[name] = ServiceDefinition(
            service_type=service_type,
            factory=factory,
            singleton=singleton
        )
        logger.debug(f"Registered service: {name}")
    
    def register_factory(self, name: str, factory: Callable):
        """Register a factory function."""
        self._factories[name] = factory
        logger.debug(f"Registered factory: {name}")
    
    def get_service(self, name: str) -> Any:
        """Get a service instance."""
        if name not in self._services:
            raise ValueError(f"Service not found: {name}")
        
        service_def = self._services[name]
        
        # Return singleton instance if available
        if service_def.singleton and service_def.instance is not None:
            return service_def.instance
        
        # Create new instance
        instance = service_def.factory()
        
        # Store singleton instance
        if service_def.singleton:
            service_def.instance = instance
        
        return instance
    
    def get_factory(self, name: str) -> Callable:
        """Get a factory function."""
        if name not in self._factories:
            raise ValueError(f"Factory not found: {name}")
        
        return self._factories[name]
    
    def create_storage_manager(self, config: StorageConfig) -> StorageManager:
        """Create a storage manager with dependencies."""
        # Get required services
        factory = self.get_service("storage_factory")
        connection_pool = self.get_service("connection_pool")
        batch_manager = self.get_service("batch_manager")
        
        # Create storage manager with dependencies
        manager = StorageManager(config)
        
        # Inject dependencies (if StorageManager supports it)
        if hasattr(manager, 'set_connection_pool'):
            manager.set_connection_pool(connection_pool)
        
        if hasattr(manager, 'set_batch_manager'):
            manager.set_batch_manager(batch_manager)
        
        return manager
    
    def create_provider(self, config: StorageConfig) -> StorageProvider:
        """Create a storage provider with dependencies."""
        factory = self.get_service("storage_factory")
        return factory.create_provider(config)
    
    def get_registered_services(self) -> Dict[str, str]:
        """Get list of registered services."""
        return {
            name: service_def.service_type.__name__
            for name, service_def in self._services.items()
        }
    
    def clear_instances(self):
        """Clear all singleton instances (useful for testing)."""
        for service_def in self._services.values():
            service_def.instance = None
        self._instances.clear()
        logger.debug("Cleared all service instances")


class StorageServiceLocator:
    """Service locator pattern for storage services."""
    
    def __init__(self):
        self._container = StorageContainer()
        self._default_config: Optional[StorageConfig] = None
    
    def set_default_config(self, config: StorageConfig):
        """Set default storage configuration."""
        self._default_config = config
    
    def get_storage_manager(self, config: Optional[StorageConfig] = None) -> StorageManager:
        """Get storage manager instance."""
        if config is None:
            if self._default_config is None:
                raise ValueError("No default configuration set")
            config = self._default_config
        
        return self._container.create_storage_manager(config)
    
    def get_storage_provider(self, config: Optional[StorageConfig] = None) -> StorageProvider:
        """Get storage provider instance."""
        if config is None:
            if self._default_config is None:
                raise ValueError("No default configuration set")
            config = self._default_config
        
        return self._container.create_provider(config)
    
    def get_connection_pool(self) -> StorageConnectionPool:
        """Get connection pool instance."""
        return self._container.get_service("connection_pool")
    
    def get_batch_manager(self) -> StorageBatchManager:
        """Get batch manager instance."""
        return self._container.get_service("batch_manager")
    
    def get_factory(self) -> StorageFactory:
        """Get storage factory instance."""
        return self._container.get_service("storage_factory")


# Global service locator
storage_service_locator = StorageServiceLocator()


def get_storage_manager(config: Optional[StorageConfig] = None) -> StorageManager:
    """Get storage manager instance (convenience function)."""
    return storage_service_locator.get_storage_manager(config)


def get_storage_provider(config: Optional[StorageConfig] = None) -> StorageProvider:
    """Get storage provider instance (convenience function)."""
    return storage_service_locator.get_storage_provider(config)


def get_connection_pool() -> StorageConnectionPool:
    """Get connection pool instance (convenience function)."""
    return storage_service_locator.get_connection_pool()


def get_batch_manager() -> StorageBatchManager:
    """Get batch manager instance (convenience function)."""
    return storage_service_locator.get_batch_manager()


class StorageServiceProvider:
    """FastAPI dependency provider for storage services."""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self._manager: Optional[StorageManager] = None
        self._provider: Optional[StorageProvider] = None
    
    @property
    def manager(self) -> StorageManager:
        """Get storage manager instance."""
        if self._manager is None:
            self._manager = storage_service_locator.get_storage_manager(self.config)
        return self._manager
    
    @property
    def provider(self) -> StorageProvider:
        """Get storage provider instance."""
        if self._provider is None:
            self._provider = storage_service_locator.get_storage_provider(self.config)
        return self._provider
    
    async def health_check(self) -> bool:
        """Perform health check."""
        return await self.manager.health_check()
    
    async def get_info(self) -> Dict[str, Any]:
        """Get storage information."""
        return await self.manager.get_storage_info()


def create_storage_provider(config: StorageConfig) -> StorageServiceProvider:
    """Create storage service provider (FastAPI dependency)."""
    return StorageServiceProvider(config)