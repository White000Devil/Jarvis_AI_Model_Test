import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import platform
import shutil
from utils.logger import logger

class DeploymentManager:
    """
    Manages the deployment of services and applications, including Docker and Kubernetes integration.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.docker_enabled = config.get("DOCKER_ENABLED", False)
        self.kubernetes_enabled = config.get("KUBERNETES_ENABLED", False)
        self.active_deployments: Dict[str, Dict[str, Any]] = {} # deployment_id -> deployment_info
        
        self._check_dependencies()
        logger.info("Deployment Manager initialized.")

    def _check_dependencies(self):
        """Checks if Docker and Kubernetes tools are available."""
        if self.docker_enabled:
            if shutil.which("docker"):
                logger.info("Docker CLI found.")
            else:
                self.docker_enabled = False
                logger.warning("Docker CLI not found. Docker deployments will be disabled.")
        
        if self.kubernetes_enabled:
            if shutil.which("kubectl"):
                logger.info("Kubectl CLI found.")
            else:
                self.kubernetes_enabled = False
                logger.warning("Kubectl CLI not found. Kubernetes deployments will be disabled.")

    async def create_deployment_config(self, name: str, environment: str, replicas: int = 1,
                                       image: str = "nginx:latest", ports: List[int] = None,
                                       env_vars: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Creates a standardized deployment configuration.
        """
        config_id = f"deploy_cfg_{datetime.now().timestamp()}"
        deployment_config = {
            "id": config_id,
            "name": name,
            "environment": environment,
            "replicas": replicas,
            "image": image,
            "ports": ports if ports else [],
            "env_vars": env_vars if env_vars else {},
            "created_at": datetime.now().isoformat(),
            "status": "created"
        }
        logger.info(f"Deployment configuration '{name}' created: {config_id}")
        return deployment_config

    async def build_docker_image(self, context_path: str, tag: str) -> bool:
        """
        Simulates building a Docker image.
        In a real scenario, this would execute `docker build`.
        """
        if not self.docker_enabled:
            logger.warning("Docker is not enabled. Cannot build image.")
            return False
        
        logger.info(f"Simulating Docker image build for tag: {tag} from context: {context_path}")
        # Example: await asyncio.create_subprocess_exec("docker", "build", "-t", tag, context_path)
        await asyncio.sleep(3) # Simulate build time
        logger.info(f"Docker image '{tag}' simulated build complete.")
        return True

    async def deploy_docker_container(self, deployment_config: Dict[str, Any]) -> str:
        """
        Simulates deploying a Docker container.
        In a real scenario, this would execute `docker run` or `docker compose up`.
        """
        if not self.docker_enabled:
            logger.warning("Docker is not enabled. Cannot deploy container.")
            return "disabled"
        
        deploy_id = f"docker_deploy_{datetime.now().timestamp()}"
        logger.info(f"Simulating Docker container deployment for '{deployment_config['name']}' (ID: {deploy_id})")
        
        # Example: await asyncio.create_subprocess_exec("docker", "run", "-d", deployment_config['image'])
        await asyncio.sleep(2) # Simulate deployment time
        
        self.active_deployments[deploy_id] = {
            "config_id": deployment_config["id"],
            "type": "docker",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "name": deployment_config["name"],
            "image": deployment_config["image"]
        }
        logger.info(f"Docker container '{deployment_config['name']}' deployed successfully. Deployment ID: {deploy_id}")
        return deploy_id

    async def deploy_to_kubernetes(self, deployment_config: Dict[str, Any]) -> str:
        """
        Simulates deploying to Kubernetes.
        In a real scenario, this would apply Kubernetes manifests using `kubectl apply`.
        """
        if not self.kubernetes_enabled:
            logger.warning("Kubernetes is not enabled. Cannot deploy to Kubernetes.")
            return "disabled"
        
        deploy_id = f"k8s_deploy_{datetime.now().timestamp()}"
        logger.info(f"Simulating Kubernetes deployment for '{deployment_config['name']}' (ID: {deploy_id})")
        
        # Example: Generate K8s YAML and apply it
        # await asyncio.create_subprocess_exec("kubectl", "apply", "-f", "generated_manifest.yaml")
        await asyncio.sleep(5) # Simulate deployment time
        
        self.active_deployments[deploy_id] = {
            "config_id": deployment_config["id"],
            "type": "kubernetes",
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "name": deployment_config["name"],
            "image": deployment_config["image"]
        }
        logger.info(f"Kubernetes deployment '{deployment_config['name']}' successful. Deployment ID: {deploy_id}")
        return deploy_id

    async def undeploy(self, deployment_id: str) -> bool:
        """
        Simulates undeploying a service.
        """
        if deployment_id in self.active_deployments:
            deploy_info = self.active_deployments[deployment_id]
            logger.info(f"Simulating undeployment of {deploy_info['type']} deployment: {deploy_info['name']} (ID: {deployment_id})")
            
            # Example: `docker stop` or `kubectl delete`
            await asyncio.sleep(1) # Simulate undeployment time
            
            del self.active_deployments[deployment_id]
            logger.info(f"Deployment {deployment_id} undeployed successfully.")
            return True
        logger.warning(f"Attempted to undeploy non-existent deployment: {deployment_id}")
        return False

    def get_deployment_stats(self) -> Dict[str, Any]:
        """Returns statistics about active deployments and system resources."""
        # Mock system metrics
        cpu_usage = 40.0 + (datetime.now().second % 20) # 40-60%
        memory_usage = 55.0 + (datetime.now().second % 15) # 55-70%
        disk_usage = 70.0 + (datetime.now().second % 10) # 70-80%

        return {
            "enabled": self.docker_enabled or self.kubernetes_enabled,
            "docker_enabled": self.docker_enabled,
            "kubernetes_enabled": self.kubernetes_enabled,
            "active_deployments": len(self.active_deployments),
            "deployment_types": {d["type"] for d in self.active_deployments.values()},
            "system_metrics": {
                "cpu": {"usage_percent": round(cpu_usage, 2), "cores": platform.processor()},
                "memory": {"percent": round(memory_usage, 2), "total_gb": 16}, # Mock total
                "disk": {"percent": round(disk_usage, 2), "total_gb": 500} # Mock total
            },
            "last_update": datetime.now().isoformat()
        }
