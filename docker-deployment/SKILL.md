---
name: docker-deployment
description: Docker 容器化部署技能。包含 Dockerfile、Docker Compose、K8s、生产环境部署。
---

# Docker 部署技能

## 1. Dockerfile

### Python 后端
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0"]
```

### Node.js 前端
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/.next /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 多阶段构建
```dockerfile
# 构建阶段
FROM python:3.11 AS builder
WORKDIR /build
COPY . .
RUN pip install -r requirements.txt --target=/wheels
RUN pip install --target=/wheels pyinstaller && \
    pyinstaller --onefile app.py

# 运行阶段
FROM python:3.11-slim
COPY --from=builder /wheels /wheels
COPY --from=builder /dist/app /app
ENV PATH="/wheels:$PATH"
CMD ["/app"]
```

## 2. Docker Compose

### 开发环境
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///db.db
    volumes:
      - ./backend:/app
    command: python -m uvicorn main:app --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

### 生产环境
```yaml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      args:
        - BUILD_ENV=production
    restart: always
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    restart: always
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - backend
      - frontend
```

## 3. K8s 部署

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: novel-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: novel-agent
  template:
    metadata:
      labels:
        app: novel-agent
    spec:
      containers:
      - name: backend
        image: novel-agent/backend:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: novel-agent
spec:
  selector:
    app: novel-agent
  ports:
  - port: 80
    targetPort: 8000
```

## 4. 最佳实践

### 镜像优化
- 使用 Alpine 基础镜像
- 多阶段构建减小体积
- .dockerignore 排除不需要文件
- 层缓存优化顺序

### 安全
- 不使用 root 用户运行
- 敏感信息用 Secret
- 定期更新基础镜像

### 监控
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```
