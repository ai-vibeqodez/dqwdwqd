# 2-docker-build-push

## Goal
Создать `reusable__docker_build_and_push.yml` для build и push Docker образов.

## Context
Для контейнеризованных проектов нужен переиспользуемый workflow:
- Builds Docker image
- Tags с версией проекта
- Pushes на registry (Docker Hub, ghcr.io, Quay, etc)
- Поддерживает multi-platform builds (linux/amd64, linux/arm64)
- Опционально: scan на vulnerabilities

## Implementation Plan

### 1. Create `reusable__docker_build_and_push.yml`
```yaml
on:
  workflow_call:
    inputs:
      registry:
        type: string
        required: true
      image_name:
        type: string
        required: true
      version:
        type: string
        required: true
      dockerfile_path:
        type: string
        required: false
        default: './Dockerfile'
      build_context:
        type: string
        required: false
        default: '.'
      platforms:
        type: string
        required: false
        default: 'linux/amd64,linux/arm64'
      registry_username:
        type: string
        required: false
      registry_password:
        type: string
        required: false
    outputs:
      image_uri:
        value: ${{ jobs.build.outputs.image_uri }}
      digest:
        value: ${{ jobs.build.outputs.digest }}
```

### 2. Job: build_and_push
1. Checkout repo
2. Setup QEMU and buildx
3. Login to registry (if credentials provided)
4. Build image:
   - Tag: `${{ inputs.registry }}/${{ inputs.image_name }}:${{ inputs.version }}`
   - Also tag as `latest`
   - Platforms: parse comma-separated list
5. Push to registry
6. Output: image_uri, digest

### 3. Options for different registries
- **GitHub Container Registry**: login via docker/login-action with github.token
- **Docker Hub**: username/password
- **Private registries**: custom URL + basic auth or token

### 4. Multi-platform build
Use docker/buildx with QEMU

### 5. Test cases
- Build and push to ghcr.io ✓
- Multi-platform (amd64 + arm64) ✓
- Tags v1.2.3 and latest ✓
- Registry login handles different providers ✓

## Acceptance Criteria
- ✓ Builds Docker image from Dockerfile
- ✓ Tags with version and optional `latest`
- ✓ Supports multiple registries
- ✓ Multi-platform builds
- ✓ Outputs image URI and digest
- ✓ Handles auth securely (via secrets)

## Effort Estimate
2-3 hours

## Blocking Issues
None — uses standard docker/build-push-action

## Notes
- GitHub remains default
- Private instances: allow FQDN input
- Future: add vulnerability scanning (trivy, snyk)
