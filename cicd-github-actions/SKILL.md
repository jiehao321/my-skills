---
name: cicd-github-actions
description: GitHub Actions CI/CD 技能。包含自动化测试、构建、部署、发布。
---

# GitHub Actions CI/CD

## 1. 基础工作流

### Python CI
```yaml
name: Python CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Node.js CI
```yaml
name: Node.js CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install
      run: npm ci
    
    - name: Test
      run: npm test
    
    - name: Build
      run: npm run build
```

## 2. 多阶段部署

### 预览部署
```yaml
name: Deploy Preview

on:
  pull_request:
    types: [opened, synchronize, closed]

jobs:
  deploy-preview:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy Preview
      run: |
        # 构建并部署预览环境
        echo "Deploying preview for PR ${{ github.event.pull_request.number }}"
    
    - name: Comment Preview URL
      uses: actions/github-script@v7
      with:
        script: |
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            body: 'Preview deployed: https://preview-${{ github.event.pull_request.number }}.example.com'
          })
```

### 生产部署
```yaml
name: Deploy Production

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
    - uses: actions/checkout@v4
    
    - name: Login to Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and Push
      run: |
        docker build -t app:${{ github.sha }} .
        docker push app:${{ github.sha }}
    
    - name: Deploy
      run: |
        # 部署命令
        kubectl set image deployment/app app=app:${{ github.sha }}
```

## 3. 自动发布

### PyPI 发布
```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
```

### Docker Hub 发布
```yaml
name: Docker Publish

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  push:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: name/app
        tags: |
          type=ref,event=branch
          type=sha,prefix=
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
```

## 4. 缓存优化

### Docker 缓存
```yaml
- uses: docker/setup-buildx-action@v3

- uses: docker/build-push-action@v5
  with:
    context: .
    push: false
    load: true
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## 5. 条件执行

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - run: pytest
```

## 6.  secrets 使用

| Secret | 用途 |
|--------|------|
| PYPI_API_TOKEN | PyPI 发布 |
| DOCKERHUB_TOKEN | Docker Hub |
| AWS_ACCESS_KEY_ID | AWS 部署 |
| KUBECONFIG | K8s 配置 |
