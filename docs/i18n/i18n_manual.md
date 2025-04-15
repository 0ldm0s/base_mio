# 国际化(i18n)模块使用手册

## 模块位置
`mio/util/i19n/__init__.py`

## 功能概述
提供多语言支持解决方案，包含以下核心功能：
- 多语言文件加载与管理（TOML格式）
- 动态文本检索与回退机制
- 自动资源文件发现
- 与Flask框架深度集成
- 统一日志记录

## 核心组件说明

### LocalTextHelper 类

#### 初始化方法
```python
def __init__(self, app: Flask, translations_path: str = "translations")
```
**参数说明**：
- `app`: Flask应用实例（自动读取DEFAULT_LANGUAGE配置）
- `translations_path`: 翻译文件目录（相对于项目根目录）

**初始化流程**：
1. 检查并加载指定目录下的.toml文件
2. 解析文件内容到内存字典
3. 合并所有语言资源
4. 设置默认语言（从Flask配置读取）

**目录结构示例**：
```
translations/
├─ common.toml
├─ user/
│  ├─ en-US.toml
│  ├─ zh-CN.toml
```

#### 文本获取方法
```python
def get_text(self, msg_id: str, lang: str) -> str
```
**查找逻辑**：
1. 精确匹配msg_id，使用`文件名.键名`结构（如"user.UnauthorizedAccessMsg"）
2. 检查请求语言是否存在
3. 回退到默认语言
4. 最终回退空字符串

**使用示例**：
```python
i18n = LocalTextHelper(app)
error_msg = i18n.get_text("login.SessionExpired", "zh-CN")
```

## TOML文件格式规范
```toml
# common.toml 示例
# user.toml 示例
[UnauthorizedAccessMsg]
zh-CN = "非鉴权访问"
en-US = "Unauthorized access"
ja-JP = "不正なアクセス"

# system.toml 示例
[SessionExpired]
zh-CN = "会话已过期"
en-US = "Session expired"
ja-JP = "セッションが期限切れです"
```

**键名规则**：
- 使用`文件名.键名`结构（如"user.UnauthorizedAccessMsg"）
- 文件名对应翻译文件前缀（如user.toml）
- 键名需与TOML文件内的表头完全一致
- 语言代码遵循RFC 5646标准

**正确调用示例**：
```python
# 获取user.toml中的UnauthorizedAccessMsg翻译
msg = i18n.get_text("user.UnauthorizedAccessMsg", "zh-CN")

# 获取system.toml中的SessionExpired翻译
msg = i18n.get_text("system.SessionExpired", "en-US")
```

## 最佳实践

### Flask集成方案
```python
app = Flask(__name__)
app.config["DEFAULT_LANGUAGE"] = "zh-CN"
i18n = LocalTextHelper(app)

@app.route("/")
def index():
    return i18n.get_text("home.title", request.accept_languages.best)
```

## 异常处理指南
| 异常类型            | 触发条件                  | 解决方案               |
|---------------------|--------------------------|-----------------------|
| FileNotFoundError   | 翻译目录不存在            | 检查translations_path |
| TomlDecodeError     | TOML文件格式错误          | 验证文件语法          |
| KeyError            | 无效msg_id               | 检查翻译键命名规范    |
| PermissionError     | 文件读取权限不足          | 调整目录权限          |

## 性能优化建议
1. 生产环境预加载常用语言包
2. 使用LRU缓存高频访问的翻译
3. 定期清理未使用的翻译资源
4. 启用内存监测防止资源泄露

## 版本记录
- v1.3 (2024-05) 增加TOML格式支持
- v1.2 (2024-03) 优化Flask集成方式
- v1.1 (2024-01) 实现基础多语言加载

> 注意：默认语言应在Flask配置中通过DEFAULT_LANGUAGE设置