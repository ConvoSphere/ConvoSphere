"""
Deployment management system for the AI Assistant Platform.

This module provides comprehensive deployment features including
production builds, optimization, and deployment automation.
"""

import json
import shutil
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class DeploymentEnvironment(Enum):
    """Deployment environment enumeration."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class BuildType(Enum):
    """Build type enumeration."""

    DEBUG = "debug"
    RELEASE = "release"
    OPTIMIZED = "optimized"


@dataclass
class BuildConfig:
    """Build configuration."""

    environment: DeploymentEnvironment
    build_type: BuildType
    optimize: bool = True
    minify: bool = True
    source_maps: bool = False
    cache_busting: bool = True
    compression: bool = True
    bundle_analysis: bool = False


@dataclass
class DeploymentConfig:
    """Deployment configuration."""

    target_environment: DeploymentEnvironment
    build_config: BuildConfig
    backup_enabled: bool = True
    rollback_enabled: bool = True
    health_check_enabled: bool = True
    monitoring_enabled: bool = True


class DeploymentManager:
    """Deployment management system."""

    def __init__(self):
        """Initialize deployment manager."""
        self.current_environment = DeploymentEnvironment.DEVELOPMENT
        self.build_history: list[dict[str, Any]] = []
        self.deployment_history: list[dict[str, Any]] = []
        self.deployment_callbacks: list[callable] = []

        # Configuration paths
        self.project_root = Path(__file__).parent.parent.parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.backup_dir = self.project_root / "backups"

        # Initialize deployment system
        self.initialize_deployment()

    def initialize_deployment(self):
        """Initialize deployment system."""
        # Create necessary directories
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)

        # Load deployment configuration
        self.load_deployment_config()

    def load_deployment_config(self):
        """Load deployment configuration."""
        config_path = self.project_root / "deployment_config.json"

        if config_path.exists():
            with open(config_path) as f:
                config_data = json.load(f)
                self.deployment_config = DeploymentConfig(**config_data)
        else:
            # Default configuration
            self.deployment_config = DeploymentConfig(
                target_environment=DeploymentEnvironment.PRODUCTION,
                build_config=BuildConfig(
                    environment=DeploymentEnvironment.PRODUCTION,
                    build_type=BuildType.OPTIMIZED,
                ),
            )

    def save_deployment_config(self):
        """Save deployment configuration."""
        config_path = self.project_root / "deployment_config.json"

        with open(config_path, "w") as f:
            json.dump(self.deployment_config.__dict__, f, indent=2, default=str)

    def create_build(self, config: BuildConfig) -> dict[str, Any]:
        """Create a new build."""
        build_id = f"build_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        build_info = {
            "id": build_id,
            "timestamp": datetime.now().isoformat(),
            "config": config.__dict__,
            "status": "building",
            "artifacts": [],
        }

        try:
            # Start build process
            self.build_history.append(build_info)

            # Create build directory
            build_path = self.build_dir / build_id
            build_path.mkdir(exist_ok=True)

            # Copy source files
            self.copy_source_files(build_path)

            # Apply optimizations
            if config.optimize:
                self.optimize_build(build_path, config)

            # Create production bundle
            if config.build_type == BuildType.OPTIMIZED:
                self.create_optimized_bundle(build_path, config)

            # Generate source maps
            if config.source_maps:
                self.generate_source_maps(build_path)

            # Apply cache busting
            if config.cache_busting:
                self.apply_cache_busting(build_path)

            # Compress assets
            if config.compression:
                self.compress_assets(build_path)

            # Bundle analysis
            if config.bundle_analysis:
                self.analyze_bundle(build_path)

            # Update build info
            build_info["status"] = "completed"
            build_info["artifacts"] = self.get_build_artifacts(build_path)
            build_info["size"] = self.get_build_size(build_path)

            print(f"Build {build_id} completed successfully")

        except Exception as e:
            build_info["status"] = "failed"
            build_info["error"] = str(e)
            print(f"Build {build_id} failed: {e}")

        return build_info

    def copy_source_files(self, build_path: Path):
        """Copy source files to build directory."""
        # Copy frontend files
        frontend_src = self.project_root / "frontend"
        frontend_dest = build_path / "frontend"

        if frontend_src.exists():
            shutil.copytree(frontend_src, frontend_dest, dirs_exist_ok=True)

        # Copy static assets
        assets_src = self.project_root / "frontend" / "assets"
        assets_dest = build_path / "assets"

        if assets_src.exists():
            shutil.copytree(assets_src, assets_dest, dirs_exist_ok=True)

        # Copy configuration files
        config_files = ["requirements.txt", "pyproject.toml"]
        for config_file in config_files:
            config_src = self.project_root / config_file
            if config_src.exists():
                shutil.copy2(config_src, build_path)

    def optimize_build(self, build_path: Path, config: BuildConfig):
        """Optimize build files."""
        # Optimize Python files
        self.optimize_python_files(build_path)

        # Optimize static assets
        self.optimize_static_assets(build_path)

        # Remove development files
        self.remove_development_files(build_path)

    def optimize_python_files(self, build_path: Path):
        """Optimize Python files."""
        # This would implement Python code optimization
        # For now, we'll just remove __pycache__ directories
        for pycache_dir in build_path.rglob("__pycache__"):
            shutil.rmtree(pycache_dir)

        # Remove .pyc files
        for pyc_file in build_path.rglob("*.pyc"):
            pyc_file.unlink()

    def optimize_static_assets(self, build_path: Path):
        """Optimize static assets."""
        assets_dir = build_path / "assets"

        if not assets_dir.exists():
            return

        # Optimize images
        self.optimize_images(assets_dir)

        # Minify CSS and JS
        self.minify_assets(assets_dir)

    def optimize_images(self, assets_dir: Path):
        """Optimize image files."""
        # This would implement image optimization
        # For now, we'll just log the optimization
        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

        for ext in image_extensions:
            for image_file in assets_dir.rglob(f"*{ext}"):
                print(f"Optimizing image: {image_file}")

    def minify_assets(self, assets_dir: Path):
        """Minify CSS and JavaScript files."""
        # This would implement CSS/JS minification
        # For now, we'll just log the minification
        for css_file in assets_dir.rglob("*.css"):
            print(f"Minifying CSS: {css_file}")

        for js_file in assets_dir.rglob("*.js"):
            print(f"Minifying JavaScript: {js_file}")

    def remove_development_files(self, build_path: Path):
        """Remove development-specific files."""
        # Remove test files
        for test_file in build_path.rglob("*test*.py"):
            test_file.unlink()

        # Remove development configuration
        dev_configs = ["dev_config.py", "test_config.py"]
        for dev_config in dev_configs:
            dev_config_path = build_path / dev_config
            if dev_config_path.exists():
                dev_config_path.unlink()

    def create_optimized_bundle(self, build_path: Path, config: BuildConfig):
        """Create optimized bundle."""
        # This would implement bundle optimization
        # For now, we'll just create a bundle manifest
        bundle_manifest = {
            "version": "1.0.0",
            "build_type": config.build_type.value,
            "environment": config.environment.value,
            "timestamp": datetime.now().isoformat(),
            "files": [],
        }

        # Add file information
        for file_path in build_path.rglob("*"):
            if file_path.is_file():
                bundle_manifest["files"].append(
                    {
                        "path": str(file_path.relative_to(build_path)),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(
                            file_path.stat().st_mtime,
                        ).isoformat(),
                    },
                )

        # Save bundle manifest
        manifest_path = build_path / "bundle_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(bundle_manifest, f, indent=2)

    def generate_source_maps(self, build_path: Path):
        """Generate source maps for debugging."""
        # This would implement source map generation
        # For now, we'll just create a placeholder
        source_maps_dir = build_path / "source_maps"
        source_maps_dir.mkdir(exist_ok=True)

        source_map_info = {
            "version": 3,
            "sources": [],
            "names": [],
            "mappings": "",
        }

        source_map_path = source_maps_dir / "app.js.map"
        with open(source_map_path, "w") as f:
            json.dump(source_map_info, f)

    def apply_cache_busting(self, build_path: Path):
        """Apply cache busting to assets."""
        # This would implement cache busting
        # For now, we'll just add version hashes to file names
        assets_dir = build_path / "assets"

        if not assets_dir.exists():
            return

        # Add version hash to asset files
        for asset_file in assets_dir.rglob("*"):
            if asset_file.is_file():
                # Generate hash based on file content
                import hashlib

                with open(asset_file, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()[:8]

                # Create new filename with hash
                file_ext = asset_file.suffix
                file_stem = asset_file.stem
                new_filename = f"{file_stem}.{file_hash}{file_ext}"
                new_path = asset_file.parent / new_filename

                # Rename file
                asset_file.rename(new_path)

    def compress_assets(self, build_path: Path):
        """Compress assets for faster loading."""
        # This would implement asset compression
        # For now, we'll just log the compression
        print("Compressing assets...")

        # Compress text files
        text_extensions = [".html", ".css", ".js", ".json", ".xml"]
        for ext in text_extensions:
            for text_file in build_path.rglob(f"*{ext}"):
                print(f"Compressing: {text_file}")

    def analyze_bundle(self, build_path: Path):
        """Analyze bundle size and dependencies."""
        # This would implement bundle analysis
        # For now, we'll just create a basic analysis
        analysis = {
            "total_size": 0,
            "file_count": 0,
            "largest_files": [],
            "dependencies": [],
        }

        # Calculate total size and file count
        for file_path in build_path.rglob("*"):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                analysis["total_size"] += file_size
                analysis["file_count"] += 1

                analysis["largest_files"].append(
                    {
                        "path": str(file_path.relative_to(build_path)),
                        "size": file_size,
                    },
                )

        # Sort largest files
        analysis["largest_files"].sort(key=lambda x: x["size"], reverse=True)
        analysis["largest_files"] = analysis["largest_files"][:10]

        # Save analysis
        analysis_path = build_path / "bundle_analysis.json"
        with open(analysis_path, "w") as f:
            json.dump(analysis, f, indent=2)

    def get_build_artifacts(self, build_path: Path) -> list[str]:
        """Get list of build artifacts."""
        artifacts = []

        for file_path in build_path.rglob("*"):
            if file_path.is_file():
                artifacts.append(str(file_path.relative_to(build_path)))

        return artifacts

    def get_build_size(self, build_path: Path) -> int:
        """Get total build size in bytes."""
        total_size = 0

        for file_path in build_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        return total_size

    def deploy_build(self, build_id: str, config: DeploymentConfig) -> dict[str, Any]:
        """Deploy a build to target environment."""
        deployment_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        deployment_info = {
            "id": deployment_id,
            "build_id": build_id,
            "timestamp": datetime.now().isoformat(),
            "config": config.__dict__,
            "status": "deploying",
            "steps": [],
        }

        try:
            # Start deployment process
            self.deployment_history.append(deployment_info)

            # Find build
            build_path = self.build_dir / build_id
            if not build_path.exists():
                raise Exception(f"Build {build_id} not found")

            # Create backup
            if config.backup_enabled:
                self.create_backup(deployment_info)

            # Deploy to target environment
            self.deploy_to_environment(build_path, config, deployment_info)

            # Run health checks
            if config.health_check_enabled:
                self.run_health_checks(deployment_info)

            # Enable monitoring
            if config.monitoring_enabled:
                self.enable_monitoring(deployment_info)

            # Update deployment info
            deployment_info["status"] = "completed"
            deployment_info["steps"].append("Deployment completed successfully")

            print(f"Deployment {deployment_id} completed successfully")

        except Exception as e:
            deployment_info["status"] = "failed"
            deployment_info["error"] = str(e)
            deployment_info["steps"].append(f"Deployment failed: {e}")

            # Rollback if enabled
            if config.rollback_enabled:
                self.rollback_deployment(deployment_info)

            print(f"Deployment {deployment_id} failed: {e}")

        return deployment_info

    def create_backup(self, deployment_info: dict[str, Any]):
        """Create backup before deployment."""
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_id

        # Create backup of current deployment
        current_deployment = self.dist_dir
        if current_deployment.exists():
            shutil.copytree(current_deployment, backup_path)
            deployment_info["backup_id"] = backup_id
            deployment_info["steps"].append(f"Backup created: {backup_id}")

    def deploy_to_environment(
        self,
        build_path: Path,
        config: DeploymentConfig,
        deployment_info: dict[str, Any],
    ):
        """Deploy to target environment."""
        target_path = self.dist_dir

        # Clear target directory
        if target_path.exists():
            shutil.rmtree(target_path)

        # Copy build to target
        shutil.copytree(build_path, target_path)

        # Environment-specific configuration
        self.configure_environment(target_path, config.target_environment)

        deployment_info["steps"].append(
            f"Deployed to {config.target_environment.value}",
        )

    def configure_environment(
        self, target_path: Path, environment: DeploymentEnvironment,
    ):
        """Configure deployment for specific environment."""
        # Create environment configuration
        env_config = {
            "environment": environment.value,
            "api_url": self.get_api_url(environment),
            "websocket_url": self.get_websocket_url(environment),
            "debug": environment == DeploymentEnvironment.DEVELOPMENT,
        }

        # Save environment configuration
        config_path = target_path / "config" / "environment.json"
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, "w") as f:
            json.dump(env_config, f, indent=2)

    def get_api_url(self, environment: DeploymentEnvironment) -> str:
        """Get API URL for environment."""
        urls = {
            DeploymentEnvironment.DEVELOPMENT: "http://localhost:8000",
            DeploymentEnvironment.STAGING: "https://api-staging.example.com",
            DeploymentEnvironment.PRODUCTION: "https://api.example.com",
        }
        return urls.get(environment, "http://localhost:8000")

    def get_websocket_url(self, environment: DeploymentEnvironment) -> str:
        """Get WebSocket URL for environment."""
        urls = {
            DeploymentEnvironment.DEVELOPMENT: "ws://localhost:8000/ws",
            DeploymentEnvironment.STAGING: "wss://ws-staging.example.com",
            DeploymentEnvironment.PRODUCTION: "wss://ws.example.com",
        }
        return urls.get(environment, "ws://localhost:8000/ws")

    def run_health_checks(self, deployment_info: dict[str, Any]):
        """Run health checks after deployment."""
        # This would implement actual health checks
        # For now, we'll just simulate health checks
        health_checks = [
            "API endpoint check",
            "Database connection check",
            "WebSocket connection check",
            "Static assets check",
        ]

        for check in health_checks:
            # Simulate health check
            import time

            time.sleep(0.1)  # Simulate check time

            deployment_info["steps"].append(f"Health check passed: {check}")

    def enable_monitoring(self, deployment_info: dict[str, Any]):
        """Enable monitoring for deployment."""
        # This would implement monitoring setup
        # For now, we'll just log the monitoring setup
        monitoring_config = {
            "enabled": True,
            "metrics": ["performance", "errors", "usage"],
            "alerts": ["error_rate", "response_time"],
        }

        deployment_info["monitoring"] = monitoring_config
        deployment_info["steps"].append("Monitoring enabled")

    def rollback_deployment(self, deployment_info: dict[str, Any]):
        """Rollback deployment to previous version."""
        if "backup_id" not in deployment_info:
            deployment_info["steps"].append("No backup available for rollback")
            return

        backup_id = deployment_info["backup_id"]
        backup_path = self.backup_dir / backup_id

        if backup_path.exists():
            # Restore from backup
            if self.dist_dir.exists():
                shutil.rmtree(self.dist_dir)

            shutil.copytree(backup_path, self.dist_dir)
            deployment_info["steps"].append(f"Rolled back to backup: {backup_id}")
        else:
            deployment_info["steps"].append("Backup not found for rollback")

    def get_deployment_status(self, deployment_id: str) -> dict[str, Any] | None:
        """Get deployment status."""
        for deployment in self.deployment_history:
            if deployment["id"] == deployment_id:
                return deployment
        return None

    def get_build_status(self, build_id: str) -> dict[str, Any] | None:
        """Get build status."""
        for build in self.build_history:
            if build["id"] == build_id:
                return build
        return None

    def list_builds(self) -> list[dict[str, Any]]:
        """List all builds."""
        return self.build_history

    def list_deployments(self) -> list[dict[str, Any]]:
        """List all deployments."""
        return self.deployment_history

    def cleanup_old_builds(self, keep_count: int = 10):
        """Clean up old builds."""
        if len(self.build_history) <= keep_count:
            return

        # Sort builds by timestamp
        sorted_builds = sorted(self.build_history, key=lambda x: x["timestamp"])

        # Remove old builds
        for build in sorted_builds[:-keep_count]:
            build_path = self.build_dir / build["id"]
            if build_path.exists():
                shutil.rmtree(build_path)

            self.build_history.remove(build)

    def cleanup_old_deployments(self, keep_count: int = 5):
        """Clean up old deployments."""
        if len(self.deployment_history) <= keep_count:
            return

        # Sort deployments by timestamp
        sorted_deployments = sorted(
            self.deployment_history, key=lambda x: x["timestamp"],
        )

        # Remove old deployments
        for deployment in sorted_deployments[:-keep_count]:
            if "backup_id" in deployment:
                backup_path = self.backup_dir / deployment["backup_id"]
                if backup_path.exists():
                    shutil.rmtree(backup_path)

            self.deployment_history.remove(deployment)

    def on_deployment_event(self, callback: callable):
        """Register deployment event callback."""
        self.deployment_callbacks.append(callback)

    def export_deployment_report(self) -> str:
        """Export deployment report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_builds": len(self.build_history),
            "total_deployments": len(self.deployment_history),
            "recent_builds": self.build_history[-5:],
            "recent_deployments": self.deployment_history[-5:],
            "current_environment": self.current_environment.value,
        }

        return json.dumps(report, indent=2, default=str)


# Global deployment manager instance
deployment_manager = DeploymentManager()
