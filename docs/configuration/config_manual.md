# 配置管理模块使用手册

## 模块位置
`config/__init__.py`

## 功能概述
提供多环境配置管理解决方案，包含以下核心功能：
- 开发/测试/生产环境配置隔离
- 敏感信息环境变量注入
- 主流数据库连接支持
- 服务组件开关控制
- 安全参数集中管理

## 核心配置项说明

### 基础配置类 (Config)
| 配置项                 | 类型    | 默认值                          | 说明                     |
|-----------------------|---------|--------------------------------|--------------------------|
| SECRET_KEY            | str     | 随机生成                        | 应用安全密钥             |
| MAIL_SERVER           | str     | localhost                      | SMTP服务器地址           |
| MONGODB_ENABLE        | bool    | False                         | MongoDB服务开关          |
| REDIS_ENABLE          | bool    | False                         | Redis服务开关           |
| CELERY_ENABLE         | bool    | False                         | Celery任务队列开关       |
| CORS_ENABLE           | bool    | False                         | 跨域资源共享开关         |

### 环境变量映射
```python
# 示例：通过环境变量覆盖配置
export MIO_MAIL_SERVER=smtp.example.com
export MIO_REDIS_ENABLE=1
```

## 多环境配置指南

### 开发环境配置
```python
class DevelopmentConfig(Config):
    DEBUG = True
    MONGODB_SETTINGS = {
        "host": "mongodb://admin:password@localhost/dbname",
        "connect": False
    }
    SQLALCHEMY_DATABASE_URI = "postgresql+pg8000://admin:password@localhost:5432/dbname"
    REDIS_URL = "redis://localhost:6379/0"
```

### 生产环境配置
```python
class ProductionConfig(Config):
    REDIS_URL = "unix:///dev/shm/redis.sock?db=0"  # 使用Unix Domain Socket
    CELERY_BROKER_URL = "redis://localhost:6379/1"  # 独立数据库
    MAIL_USE_TLS = True  # 强制加密传输
```

## 服务连接配置

### MongoDB连接规范
```python
MONGODB_SETTINGS = {
    "host": "mongodb://{user}:{password}@{host}/{db}"
            "?directConnection=true&compressors=zstd",
    "connect": False  # 延迟连接
}
```

### PostgreSQL连接示例
```python
SQLALCHEMY_DATABASE_URI = 
    "postgresql+pg8000://admin:password@localhost:5432/dbname"
```

### Redis高可用配置
```python
REDIS_URL = "redis://:password@master1:6379,slave1:6380/0"
           "?socket_timeout=10&retry_on_timeout=true"
```

## 安全最佳实践
1. 密钥管理：
   ```python
   # 必须通过环境变量设置生产密钥
   export SECRET_KEY='your-256-bit-secret'
   ```
2. 数据库凭据：
   - 使用加密的配置管理服务
   - 开发环境与生产环境凭证隔离
3. 网络策略：
   - 数据库仅允许内网访问
   - Redis启用密码认证

## 配置继承关系
```mermaid
classDiagram
    Config <|-- DevelopmentConfig
    Config <|-- TestingConfig
    Config <|-- ProductionConfig
    class Config{
        +SECRET_KEY
        +init_app()
    }
```

## 版本历史
- v2.3 (2024-05) 增加ZSTD压缩支持
- v1.7 (2024-03) 统一配置接口
- v1.0 (2024-01) 初始配置模块版本

> 警告：禁止在版本控制系统中提交真实凭证