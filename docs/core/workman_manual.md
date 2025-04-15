# WorkMan.py 守护进程模块手册

## 模块位置
`cli/WorkMan.py`

## 类结构说明

### Daemon 基类
```python
class Daemon(object):
    def __get_logger__(self, name: str) -> LogHandler:
    def hello(self, app, kwargs):
```

## 命令行调用

### 调用格式
```bash
flask cli exe -cls=cli.WorkMan.Daemon.hello [参数选项]
```

#### 参数说明
| 选项      | 说明                          | 示例值                          |
|-----------|-------------------------------|---------------------------------|
| -cls      | 完整类方法路径                | cli.WorkMan.Daemon.hello        |
| -arg      | 参数键值对(||分割)           | "user=admin||token=abc123"      |
| -pid      | PID文件路径（可选）           | /var/run/service.pid           |

### 调用示例
```bash
# 基础调用
FLASK_APP=mio.shell flask cli exe -cls=cli.WorkMan.Daemon.hello

# 带参数调用
flask cli exe -cls=cli.WorkMan.Daemon.hello \
  -arg="service_name=payment||log_level=debug"

# 生产环境调用（记录PID）
flask cli exe -cls=cli.WorkMan.Daemon.hello \
  -pid=/var/run/my_service.pid
```

## 参数处理规范

### 参数解析流程
1. `-arg`参数按`||`分割为多个键值对
2. 每个键值对按第一个`=`号分割键和值
3. 自动转换为字典传入`hello`方法

```python
# 输入参数示例
-arg="host=127.0.0.1||port=8080"

# 转换为kwargs：
{
  "host": "127.0.0.1",
  "port": "8080"
}
```

### app参数注入
- `app`参数由Flask自动注入`current_app`
- 在方法中可直接访问应用配置：
```python
def hello(self, app, kwargs):
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
```

## 开发扩展指南

### 方法重写模板
```python
class CustomDaemon(Daemon):
    def hello(self, app, kwargs):
        """ 自定义状态检测 """
        # 访问应用配置
        timeout = app.config.get('HEALTH_CHECK_TIMEOUT', 30)
        
        # 处理传入参数
        check_level = kwargs.get('check_level', 'basic')
        
        return {
            "status": "OK",
            "version": "1.0.0",
            "config": {
                "timeout": timeout,
                "check_level": check_level
            }
        }
```

## 日志追踪
```bash
# 查看实时日志
tail -f logs/mio.log | grep Daemon.hello

# 典型日志输出
[2025-04-16 03:20:11] Daemon.hello - 收到健康检查请求
[2025-04-16 03:20:11] Daemon.hello - 当前Python版本: 3.9.6
```

> 注意：所有cli命令需在FLASK_APP环境变量正确配置后执行