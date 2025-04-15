# 字符串处理工具模块使用手册

## 模块位置
`mio/util/Helper/string_utils.py`

## 功能概述
提供全面的字符串处理工具集，包含以下核心功能：
- 安全HTML/XSS过滤
- 多种随机字符串生成
- 类型安全转换
- 字典参数安全提取
- 编码强制转换

## 核心函数说明

### 1. 安全过滤工具
#### `safe_html_code(string_html, is_all, strip, strip_comments)`
```python
def safe_html_code(
    string_html: Optional[str] = "",
    is_all: bool = True,
    strip=True,
    strip_comments=True
) -> str
```
**安全特性**：
- 白名单机制（允许35+HTML标签/属性）
- CSS样式过滤（保留6种安全属性）
- 自动清理恶意脚本和注释
- 支持XSS防御

**示例**：
```python
clean_html = safe_html_code(user_input, is_all=False)
```

### 2. 随机字符串生成
#### `random_number_str(random_length=8) -> str`
```python
def random_number_str(random_length: int = 8) -> str
```
**安全特性**：
- 纯数字字符串生成
- 允许前导零（与random_number区别）
- 固定长度输出

**示例**：
```python
# 生成订单编号
order_no = random_number_str(12)  # 示例："048372619583"
```

#### `random_str(random_length, letters)`
```python
def random_str(random_length: int = 8, letters: int = 0) -> str
```
**模式说明**：
- 0: 混合大小写
- 1: 仅小写
- 2: 仅大写

#### `random_char(size, special, letters)`
```python
def random_char(size: int = 6, special: bool = False, letters: int = 0) -> str
```
**安全增强**：
- 特殊字符可选启用
- 密码强度控制
- 排除易混淆字符

### 3. 类型转换工具
#### `str2int(text, default)`
```python
def str2int(text: str, default: Optional[int] = 0) -> Optional[int]
```
**特性**：
- 自动过滤非数字字符
- 支持科学计数法转换
- Decimal中间转换保证精度

#### `force_bytes(value)`
```python
def force_bytes(value: Union[str, bytes]) -> bytes
```
**编码保障**：
- 强制UTF-8编码
- 异常类型安全
- 内存优化处理

### 4. 数据提取工具
#### `get_args_from_dict(dt, ky, default, force_str, check_type)`
```python
def get_args_from_dict(
    dt: Dict,
    ky: str,
    default: Optional[Any] = "",
    force_str: bool = False,
    check_type: bool = True
) -> Optional[Any]
```
**参数说明**：
- `force_str`: 强制返回字符串格式
- `check_type`: 类型严格校验（默认开启）

**安全特性**：
- 自动修剪字符串两端空格
- 类型不一致时返回默认值
- 空值自动转换处理

**示例**：
```python
params = {"page": "1", "size": 20}
page = get_args_from_dict(params, "page", 1)  # 返回1（字符串"1"转为int）
```

#### `get_keyword(keyword, default, **kwargs)`
```python
def get_keyword(
    keyword: str,
    default: Any,
    **kwargs: Dict[str, Any]
) -> Tuple[T, Dict[str, Any]]
```
**线程安全特性**：
- 原子化数据弹出
- 类型注解完备
- 原始数据保护

## 最佳实践
### 用户输入处理方案
```python
# 清理用户输入的富文本
safe_content = safe_html_code(request.form['content'], is_all=False)

# 安全获取请求参数
page_size, params = get_keyword('page_size', 20, **request.args)
```

### 密码重置令牌生成
```python
# 生成12位安全令牌
reset_token = random_char(12, special=True, letters=1)
```

## 异常处理指南
| 异常类型         | 触发条件                  | 解决方案               |
|------------------|--------------------------|-----------------------|
| TypeError        | 非字符串/字节流输入       | 前置类型验证          |
| KeyError         | 字典键不存在              | 使用get_keyword防护   |
| UnicodeEncodeError| 非常规字符编码            | 指定errors处理策略    |

## 性能优化建议
1. 高频HTML过滤使用lxml加速
2. 随机生成使用SystemRandom增强安全性
3. 大文本处理采用流式清理

## 版本记录
- v3.1 (2024-05) 增强HTML标签白名单
- v3.0 (2024-03) 重构安全过滤引擎
- v2.5 (2024-01) 增加类型安全转换

> 注意：处理用户输入时务必使用safe_html_code进行过滤