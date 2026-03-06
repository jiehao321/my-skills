---
name: code-review-assistant
description: 代码审查助手。分析代码质量、发现潜在问题、提供改进建议。
---

# Code Review Assistant

代码审查技能，帮助发现代码问题并提供改进建议。

## 审查维度

### 1. 代码结构
- 模块划分是否清晰
- 函数/类是否过长
- 重复代码是否提取
- 命名是否规范

### 2. 安全性
- 敏感信息是否泄露
- SQL 注入风险
- XSS 漏洞
- 权限校验

### 3. 性能
- 数据库查询是否优化 (N+1 问题)
- 是否有不必要的循环
- 缓存是否使用
- 大数据处理方式

### 4. 错误处理
- 异常是否捕获
- 错误信息是否友好
- 是否有降级处理

### 5. 代码规范
- 格式是否一致
- 注释是否充分
- 文档是否更新

## 快速审查命令

### Git Diff 审查
```bash
# 查看未提交的改动
git diff

# 查看某个文件的改动
git diff path/to/file.py

# 查看与主分支的差异
git diff main..HEAD

# 查看某次提交的改动
git show commit-hash
```

### 代码统计
```bash
# 文件行数
wc -l path/to/file.py

# 项目代码行数
find . -name "*.py" -exec wc -l {} + | sort -n

# 统计函数数量
grep -c "def " path/to/file.py

# 统计类数量
grep -c "^class " path/to/file.py
```

### 静态分析工具
```bash
# Python
pip install pylint flake8 mypy
pylint path/to/file.py
flake8 path/to/file.py
mypy path/to/file.py

# JavaScript/TypeScript
npm install -g eslint
eslint path/to/file.js
```

### 安全扫描
```bash
# GitHub 安全扫描
git secrets scan

# 敏感信息检测
grep -r "password\|secret\|api_key\|token" --include="*.py" .
```

## 审查检查清单

### Python
- [ ] 导入顺序: 标准库 → 第三方库 → 本地模块
- [ ] 异常捕获具体类型，不使用 `except:`
- [ ] 使用 f-string 或 .format()，不用 % 格式化
- [ ] 类型注解是否完整
- [ ] 上下文管理器 (with) 是否使用
- [ ] 列表/字典推导式是否使用
- [ ] 是否有TODO注释

### JavaScript/TypeScript
- [ ] const/let 使用正确
- [ ] 箭头函数适当使用
- [ ] async/await 正确使用
- [ ] 解构赋值适当使用
- [ ] 组件是否使用 memo/PuseMemo
- [ ] 接口类型是否定义

### 数据库
- [ ] 查询是否有索引
- [ ] 是否存在 N+1 查询
- [ ] 事务是否正确使用
- [ ] 连接是否正确关闭
- [ ] SQL 是否有注入风险

### API 设计
- [ ] HTTP 方法使用正确
- [ ] 状态码使用规范
- [ ] 错误信息结构一致
- [ ] 是否有版本控制
- [ ] 认证/授权是否正确

## 输出格式

```markdown
## Code Review: filename.py

### 问题 (Issues)
1. **[严重]** 行 45: SQL 注入风险
   - 问题: 使用字符串拼接 SQL
   - 建议: 使用参数化查询

2. **[中等]** 行 80: 函数过长 (50+ 行)
   - 建议: 拆分为多个小函数

3. **[轻微]** 行 12: 缺少类型注解
   - 建议: 添加参数和返回值类型

### 优点 (Good Practices)
- 行 30: 错误处理完善
- 行 55: 代码注释清晰
- 行 70: 使用上下文管理器

### 总体评价
代码质量良好，建议修复严重问题后合并。
```

## 自动审查脚本

```bash
#!/bin/bash
# quick-review.sh

echo "=== Quick Code Review ==="
echo ""

echo "--- File Statistics ---"
find . -name "*.py" -o -name "*.js" -o -name "*.ts" | head -5 | while read f; do
    echo "$f: $(wc -l < $f) lines"
done

echo ""
echo "--- Potential Issues ---"
grep -rn "except:" --include="*.py" . | head -5
grep -rn "TODO\|FIXME\|HACK" --include="*.py" . | head -5
```
