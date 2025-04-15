# Celery 命令行集成手册

## 模块位置
`mio/ext/celery/__init__.py`

## 功能概述
提供与Celery命令行工具的深度集成，支持以下操作：
- 启动Celery Worker
- 发送远程控制命令
- 统一参数解析机制

## 核心命令格式
```bash
flask celery run [选项]
```

### 选项说明
| 选项   | 必填 | 说明                          | 示例值                          |
|--------|------|-------------------------------|---------------------------------|
| -A     | 是   | Celery应用模块路径            | tasks.app                       |
| -w     | 否   | Worker启动参数                | "loglevel=info concurrency=4"   |
| -ctl   | 否   | 控制命令参数                  | "shutdown"                      |

## 参数解析规则

### Worker参数解析示例
```python
# 输入参数
-w "pool=gevent loglevel=debug"

# 转换后命令行
celery -A tasks.app worker --pool=gevent --loglevel=debug
```

### 控制参数解析示例
```python
# 输入参数
-ctl "rate_limit=taskA 10/m"

# 转换后命令行
celery -A tasks.app control --rate-limit=taskA 10/m
```

### 参数转换规则表
| 原始参数格式      | 转换规则                      | 转换结果              |
|-------------------|-------------------------------|-----------------------|
| key=value         | 自动转为长参数格式            | --key=value           |
| 单字母参数        | 自动添加单横线前缀            | -c                    |
| 多字母参数        | 自动添加双横线前缀            | --loglevel            |

## 典型使用场景

### 场景1：启动基础Worker
```bash
flask celery run -A tasks.app -w "pool=prefork loglevel=info"
```

### 场景2：发送远程控制命令
```bash
flask celery run -A tasks.app -ctl "status"
```

### 场景3：带特殊字符参数
```bash
# 使用等号嵌套值
flask celery run -A tasks.app -w "queues=high_priority,low_priority"
```

## 高级配置指南

### 自动参数转换逻辑
```python
# 参数解析流程
输入参数 -> 按空格分割 -> 自动转换参数格式 -> 构建完整命令行
```

### 异常处理机制
- 缺少-A参数时自动退出并提示
- 非法参数格式将直接传递给Celery处理
- 执行失败返回Celery原生错误信息

## 开发注意事项
1. 参数中的等号处理逻辑（代码FIXME标记处）可能影响复杂参数传递
2. 建议使用官方推荐的参数格式（如`--loglevel=info`）
3. 控制命令需确保Celery实例已正确配置消息中间件

> 提示：可通过`celery --help`查看完整的Celery命令行选项