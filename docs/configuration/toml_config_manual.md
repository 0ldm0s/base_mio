# TOML配置管理手册

## 文件位置
`config/config.toml`

## 配置项说明

### 蓝图配置
```toml
[[blueprint]]
[blueprint.main]
class = "web.main"  # 主蓝图模块路径
```

| 参数  | 类型   | 必需 | 默认值 | 说明                      |
|-------|--------|------|--------|--------------------------|
| class | string | 是   | 无     | 蓝图类的完整导入路径        |

### 登录管理器配置
```toml
[config.login_manager]
enable = false             # 登录系统开关
session_protection = "strong"  # 会话保护级别
login_view = "main.login"  # 登录路由端点
```

| 参数             | 类型    | 允许值                  | 默认值   | 说明                          |
|------------------|---------|-------------------------|----------|------------------------------|
| enable           | bool    | true/false              | false    | 是否启用登录管理系统           |
| session_protection| string  | "basic"/"strong"/"none" | "strong" | 会话保护强度级别               |
| login_view       | string  | 有效路由端点            | 无       | 未认证用户的跳转路由           |

### CSRF保护配置
```toml
[config.csrf]
enable = false  # CSRF保护开关
```

| 参数   | 类型 | 必需 | 默认值 | 说明                |
|--------|------|------|--------|--------------------|
| enable | bool | 否   | false  | 是否启用CSRF令牌验证 |

## 配置继承规则
1. TOML配置优先级高于环境变量
2. 相同配置项按以下顺序覆盖：
   - config.toml
   - 环境变量
   - 代码默认值

## 最佳实践

### 生产环境配置示例
```toml
[[blueprint]]
[blueprint.api_v1]
class = "web.api.v1"  # API蓝图路径

[config.login_manager]
enable = true
session_protection = "strong"
login_view = "api_v1.auth_login"

[config.csrf]
enable = true
```

### 多蓝图注册
```toml
[[blueprint]]
[blueprint.admin]
class = "web.admin.views"

[[blueprint]]
[blueprint.openapi]
class = "web.openapi.docs"
```

## 安全规范
1. 生产环境必须配置：
   ```toml
   [config.login_manager]
   enable = true
   session_protection = "strong"
   
   [config.csrf]
   enable = true
   ```
2. 会话保护级别说明：
   - "basic": 基础保护（默认）
   - "strong": 每次登录生成新会话ID
   - "none": 禁用保护

## 调试技巧
```bash
# 检查配置加载情况
python3 -c "from config import config; print('当前生效配置:', config['production'].__dict__)"
```

## 版本历史
- v1.2 (2024-05) 增加多蓝图支持
- v1.1 (2024-03) 新增CSRF配置项
- v1.0 (2024-01) 初始TOML配置版本

> 注意：修改配置后需重启服务生效