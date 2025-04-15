# Web服务核心模块使用手册

## 模块位置
`mio/pymio.py`

## 功能概述
提供企业级Web服务解决方案，包含以下核心功能：
- 多配置环境支持（开发/测试/生产）
- 自动性能优化（UVLoop加速）
- 双模式服务部署（Hypercorn/Flask）
- 智能CPU资源管理
- 全链路日志追踪

## 核心配置参数

### 环境变量
| 变量名           | 默认值     | 说明                      |
|------------------|------------|--------------------------|
| MIO_CONFIG       | default    | 运行环境配置              |
| MIO_APP_CONFIG   | config     | 应用专属配置文件名         |
| MIO_UVLOOP       | 0          | 是否启用异步加速(0/1)     |
| MIO_DOMAIN_SOCKET| -          | Unix Domain Socket路径    |

### 命令行参数
```bash
--app_config=CONFIG_NAME  # 指定应用配置文件
--host=0.0.0.0           # 绑定IP地址
--port=5000              # 监听端口号
--cpu_limit=4            # 最大CPU核心数
--ds=/tmp/mio.sock       # Domain Socket路径
```

## 服务启动模式

### Hypercorn生产模式
```python
# 基于ASGI的异步高性能服务
from hypercorn.asyncio import serve
from hypercorn.config import Config
config = Config()
config.bind = ["unix:/tmp/mio.sock"]  # 或IP:PORT
config.worker_class = "uvloop"
asyncio.run(serve(app, config))
```

### Flask开发模式
```python
# 内置WSGI服务器（调试用）
app.run(host='0.0.0.0', port=5000, threaded=True)
```

## 最佳实践

### 生产环境部署
```bash
# 使用Unix Domain Socket + 多Worker
MIO_CONFIG=production \
MIO_UVLOOP=1 \
python pymio.py --cpu_limit=8 --ds=/var/run/mio.sock
```

### 性能调优建议
```python
# config.toml 配置示例
[performance]
max_buffer_size = 16384  # 16KB请求缓冲区
max_body_size = 10485760  # 10MB最大请求体
log_type = "json"  # 结构化日志
```

## 监控与日志
```python
# 访问日志格式
%(h)s(%(X-Forwarded-For)s) %(r)s %(s)s %(b)s "%(f)s" "%(a)s"

# 日志级别控制
DEBUG < INFO < WARNING < ERROR < CRITICAL
```

## 安全规范
1. 生产环境必须禁用DEBUG模式
2. 使用防火墙限制访问IP
3. 定期轮换Domain Socket文件
4. 设置合理的CPU限额防止过载

## 服务管理

### 启动脚本示例
```bash
#!/bin/bash
nohup python pymio.py \
  --host=0.0.0.0 \
  --port=8080 \
  --cpu_limit=$(nproc) \
  > /var/log/mio.log 2>&1 &
```

### 健康检查
```bash
curl -I http://localhost:8080/healthcheck
# 预期响应: HTTP/1.1 200 OK
```

## 版本历史
- v3.2 (2024-05) 增加UVLoop支持
- v2.5 (2024-03) 优化配置加载逻辑
- v1.8 (2024-01) 初始服务框架版本

> 重要提示：Windows系统仅支持Flask开发模式运行