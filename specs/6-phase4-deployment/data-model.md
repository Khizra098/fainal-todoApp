# Data Model: Phase 4 Deployment

## Container Configuration Entities

### DockerImage
- **name**: String - Name of the Docker image (e.g., "todo-frontend", "todo-backend")
- **version**: String - Version/tag of the image
- **baseImage**: String - Base image used for multi-stage builds
- **buildArgs**: Map<String, String> - Arguments for the build process
- **environment**: List<String> - Environment variables for the container
- **ports**: List<Integer> - Ports exposed by the container

### BuildConfiguration
- **targetPlatform**: String - Target platform (e.g., "linux/amd64", "linux/arm64")
- **cacheEnabled**: Boolean - Whether to use Docker build cache
- **multiStage**: Boolean - Whether to use multi-stage builds
- **securityScan**: Boolean - Whether to perform security scanning

## Kubernetes Resource Entities

### Deployment
- **name**: String - Name of the deployment
- **namespace**: String - Kubernetes namespace for the deployment
- **replicas**: Integer - Number of desired pod replicas
- **image**: String - Container image reference
- **resources**: ResourceRequirements - CPU and memory limits/requests
- **healthChecks**: HealthCheckConfig - Liveness and readiness probe configuration
- **autoscaling**: HPAConfig - Horizontal Pod Autoscaler configuration

### Service
- **name**: String - Name of the service
- **namespace**: String - Kubernetes namespace for the service
- **serviceType**: String - Type of service (ClusterIP, NodePort, LoadBalancer)
- **ports**: List<ServicePort> - Port mappings for the service
- **selector**: Map<String, String> - Labels to select pods

### Ingress
- **name**: String - Name of the ingress
- **namespace**: String - Kubernetes namespace for the ingress
- **host**: String - Hostname for the ingress rule
- **tls**: TLSConfig - TLS/SSL configuration
- **rules**: List<IngressRule> - Routing rules for the ingress

### ConfigMap
- **name**: String - Name of the ConfigMap
- **namespace**: String - Kubernetes namespace for the ConfigMap
- **data**: Map<String, String> - Configuration key-value pairs

### Secret
- **name**: String - Name of the Secret
- **namespace**: String - Kubernetes namespace for the Secret
- **secretType**: String - Type of secret (Opaque, kubernetes.io/tls, etc.)
- **data**: Map<String, String> - Secret key-value pairs (base64 encoded)

## Deployment Verification Entities

### HealthCheckConfig
- **livenessProbe**: ProbeConfig - Configuration for liveness probe
- **readinessProbe**: ProbeConfig - Configuration for readiness probe
- **startupProbe**: ProbeConfig - Configuration for startup probe

### ProbeConfig
- **path**: String - HTTP endpoint path for probe
- **port**: Integer - Port to probe
- **initialDelaySeconds**: Integer - Delay before first probe
- **periodSeconds**: Integer - Interval between probes
- **timeoutSeconds**: Integer - Timeout for each probe
- **failureThreshold**: Integer - Number of failures before considering unhealthy

### ResourceRequirements
- **requests**: ResourceLimits - Minimum resources guaranteed
- **limits**: ResourceLimits - Maximum resources allowed

### ResourceLimits
- **cpu**: String - CPU resource (e.g., "500m", "1")
- **memory**: String - Memory resource (e.g., "512Mi", "1Gi")

## CI/CD Configuration Entities

### GitHubActionWorkflow
- **name**: String - Name of the workflow
- **triggers**: List<TriggerEvent> - Events that trigger the workflow
- **jobs**: List<JobConfig> - Jobs to execute in the workflow
- **environment**: String - Target environment for deployment

### JobConfig
- **name**: String - Name of the job
- **steps**: List<StepConfig> - Steps to execute in the job
- **dependencies**: List<String> - Other jobs this job depends on

### StepConfig
- **name**: String - Name of the step
- **uses**: String - Action to use (for reusable actions)
- **run**: String - Command to run (for custom commands)
- **env**: Map<String, String> - Environment variables for the step

## State Management Entities

### PersistentVolumeClaim
- **name**: String - Name of the PVC
- **namespace**: String - Kubernetes namespace for the PVC
- **storageClass**: String - Storage class to use
- **accessModes**: List<String> - Access modes (ReadWriteOnce, ReadOnlyMany, etc.)
- **resources**: ResourceRequirements - Storage size requirements

### BackupConfiguration
- **schedule**: String - Cron schedule for backups
- **retention**: Integer - Number of backups to retain
- **destination**: String - Location to store backups
- **encryption**: Boolean - Whether to encrypt backups