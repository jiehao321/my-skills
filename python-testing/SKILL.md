---
name: python-testing
description: Python 自动化测试技能。包含单元测试、集成测试、Mock、CI/CD。
---

# Python 测试技能

## 1. 单元测试

### pytest 基础
```python
import pytest

def test_example():
    assert 1 + 1 == 2

def test_with_fixture():
    assert True

# 运行
# pytest test_file.py -v
```

### 参数化测试
```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected
```

### Fixtures
```python
@pytest.fixture
def database():
    """数据库 fixture"""
    db = create_test_db()
    yield db
    db.cleanup()

def test_query(database):
    assert database.query("test") == []
```

## 2. Mock

### unittest.mock
```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    mock = Mock()
    mock.method.return_value = "mocked"
    assert mock.method() == "mocked"

@patch('module.function')
def test_patch(mock_fn):
    mock_fn.return_value = "patched"
    # ...
```

### pytest-mock
```python
def test_with_mocker(mocker):
    mock = mocker.patch('module.function')
    mock.return_value = "mocked"
    # ...
```

## 3. 集成测试

### FastAPI 测试
```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_novel():
    response = client.post(
        "/api/novel/create",
        json={"requirement": "test", "genre": "都市"}
    )
    assert response.status_code == 200
    assert "novel_id" in response.json()
```

### 数据库测试
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    yield Session()
```

## 4. 覆盖率

```bash
# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 最小覆盖率
pytest --cov=src --cov-fail-under=80
```

## 5. CI/CD

### GitHub Actions
```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov
```

## 6. 测试策略

### 测试金字塔
```
       /\
      /  \     E2E Tests (少量)
     /____\
    /      \
   /        \   Integration Tests (中量)
  /__________\
 /            \
/              \  Unit Tests (大量)
```

### 好的测试
- 快速 (Fast)
- 独立 (Independent)
- 可重复 (Repeatable)
- 自我验证 (Self-Validating)
- 及时 (Timely)
