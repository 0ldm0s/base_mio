# 数据验证工具模块使用手册

## 模块位置
`mio/util/Helper/validation_utils.py`

## 功能概述
提供全面的数据验证工具集，包含以下核心功能：
- 常用格式验证（邮箱/手机号）
- 类型安全判断
- 布尔值智能转换
- 字典结构验证
- 权限状态检查

## 核心函数说明

### 1. 格式验证工具
#### `check_email(email) -> bool`
```python
def check_email(email: str) -> bool
```
**验证规则**：
- 允许4级子域名
- 支持国际化字符
- 长度限制：6-254字符

**示例**：
```python
is_valid = check_email("user.name+tag@sub.domain.com")  # 返回True
```

#### `check_chinese_mobile(mobile) -> bool`
```python
def check_chinese_mobile(mobile: str) -> bool
```
**严格校验**：
- 11位数字
- 1开头
- 排除非常用号段（199/198等）

### 2. 类型验证工具
#### `is_number(s) -> bool`
```python
def is_number(s: Any) -> bool
```
**支持类型**：
- 整数/浮点数
- 科学计数法字符串
- Unicode数字字符（如"①"）
- 货币字符串（"¥123.45"）

**边界案例**：
```python
is_number("²³")  # 返回True（Unicode数字）
is_number("1.2e3")  # 返回True
```

### 3. 数据转换工具
#### `get_bool(obj) -> bool`
```python
def get_bool(obj: Any) -> bool
```
**转换规则**：
| 输入类型       | 转换规则                      |
|---------------|-----------------------------|
| 数字          | 1=True, 其他数字=False       |
| 字符串        | "yes"/"true"等转为True       |
| None          | 默认返回False                |

**应用场景**：
```python
get_bool("Yes")  # True
get_bool(0)      # False
```

### 4. 字典验证工具
#### `in_dict(dic, key) -> bool`
```python
def in_dict(dic: dict, key: str) -> bool
```
**特性**：
- 严格键名匹配（非值检查）
- 支持嵌套字典（仅检查第一层）

#### `is_enable(dic, key) -> bool`
```python
def is_enable(dic: dict, key: str) -> bool
```
**权限验证流程**：
1. 检查键是否存在
2. 验证值为布尔类型
3. 返回实际布尔值

## 最佳实践
### 用户注册验证
```python
if not check_email(user_email):
    raise ValueError("邮箱格式错误")
if not check_chinese_mobile(user_mobile):
    raise ValueError("手机号格式错误")
```

### 权限系统集成
```python
permissions = {"admin": True, "edit": False}
if is_enable(permissions, "admin"):
    grant_admin_access()
```

## 异常处理指南
| 异常类型         | 触发条件                  | 解决方案               |
|------------------|--------------------------|-----------------------|
| ValueError       | 非字符串格式输入          | 前置类型转换          |
| TypeError        | 非字典类型输入            | 添加类型检查          |
| AttributeError   | 无效对象属性访问          | 使用in_dict预先检查   |

## 性能优化建议
1. 高频正则验证预编译Pattern对象
2. 复杂字典检查使用字典生成式
3. 批量验证采用向量化操作

## 版本记录
- v2.2 (2024-05) 增强国际化邮箱支持
- v2.1 (2024-03) 优化手机号验证性能
- v2.0 (2024-01) 重构类型验证核心逻辑

> 注意：生产环境使用时应结合具体业务场景调整验证规则