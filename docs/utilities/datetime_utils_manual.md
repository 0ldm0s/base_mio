# 日期时间工具模块使用手册

## 模块位置
`mio/util/Helper/datetime_utils.py`

## 功能概述
提供全面的日期时间处理工具集，包含以下核心功能：
- 时间戳与字符串互转（支持时区调整）
- 智能日期范围计算（周/月/自定义）
- 微秒级时间处理
- 复杂日期运算（月数增减、跨时区转换）
- 业务场景快捷方法（昨日/今日获取）

## 核心函数说明

### 1. 时间获取与转换
#### `get_utc_now() -> int`
```python
def get_utc_now() -> int
```
**功能**：获取当前UTC时间戳（秒级）

**示例**：
```python
current_utc = get_utc_now()  # 返回类似1715827200
```

#### `get_local_now(hours, minutes) -> int`
```python
def get_local_now(hours: int = 0, minutes: int = 0) -> int
```
**参数说明**：
- `hours`/`minutes`: 时区偏移量（如北京+8）

**特性**：
- 自动处理时区转换
- 返回本地时间戳（秒级）

**示例**：
```python
# 获取北京时间戳
beijing_timestamp = get_local_now(hours=8)
```

### 2. 时间戳与字符串转换
#### `timestamp2str(timestamp, iso_format, hours, minutes)`
```python
def timestamp2str(
    timestamp: int, 
    iso_format: str = "%Y-%m-%d %H:%M:%S",
    hours: int = 0,
    minutes: int = 0
) -> Optional[str]
```
**参数说明**：
- `hours`/`minutes`: 时区偏移量（UTC+0为基准）

**示例**：
```python
# 将时间戳转换为北京时间
timestamp2str(1715827200, hours=8)  # 返回 "2024-05-16 00:00:00"
```

#### `str2timestamp(date, iso_format, hours, minutes)`
```python
def str2timestamp(
    date: str,
    iso_format: str = "%Y-%m-%d %H:%M:%S",
    hours: int = 0,
    minutes: int = 0
) -> Optional[int]
```
**特性**：
- 自动处理夏令时
- 支持非标准格式（如"%Y年%m月%d日"）

### 2. 日期范围计算
#### `get_this_week_range(timestamp, hours, minutes)`
```python
def get_this_week_range(
    timestamp: int,
    hours: int = 0,
    minutes: int = 0
) -> Tuple[int, int]
```
**返回**：(本周一零点时间戳, 下周一零点时间戳)

#### `get_this_month_range(timestamp, hours, minutes)`
```python
def get_this_month_range(
    timestamp: int,
    hours: int = 0,
    minutes: int = 0
) -> Tuple[int, int]
```
**算法特点**：
- 自动处理不同月份天数差异
- 支持跨年计算

### 3. 高级日期操作
#### `microtime(get_as_float, max_ms_lan, hours, minutes)`
```python
def microtime(
    get_as_float=False,
    max_ms_lan: int = 6,
    hours: int = 0,
    minutes: int = 0
) -> str
```
**功能**：高精度时间获取

**参数说明**：
- `get_as_float`: 返回浮点数格式（秒.微秒）
- `max_ms_lan`: 微秒精度位数（默认6位）

**示例**：
```python
# 获取带6位微秒的浮点时间
ts_float = microtime(get_as_float=True)  # 返回类似1715827200.123456

# 获取原始格式
ts_raw = microtime()  # 返回类似"0.123456 1715827200"
```

#### `add_months(timestamp, months)`
```python
def add_months(timestamp: int, months: int) -> int
```
**边界处理**：
- 月末日期增减保持月末特性（如1月31日+1个月=2月28日）
- 支持负数月份计算

#### `get_now_microtime(max_ms_lan, hours, minutes)`
```python
def get_now_microtime(
    max_ms_lan: int = 6,
    hours: int = 0,
    minutes: int = 0
) -> int
```
**精度控制**：
- 微秒级时间戳（13位整数）
- 可指定精度位数（默认6位）

### 4. 快捷方法
#### `get_today()` / `get_yesterday()`
```python
# 获取北京时间的今日日期
get_today(hours=8)  # 返回 "2024-05-16"

# 获取昨日时间戳
get_yesterday(is_timestamp=True, hours=8)
```

## 异常处理指南
| 异常类型         | 触发条件                | 解决方案               |
|------------------|-------------------------|-----------------------|
| ValueError       | 时间格式不匹配          | 检查iso_format参数     |
| OverflowError    | 时间戳超出范围          | 使用datetime替代timestamp |
| TypeError        | 参数类型错误            | 启用类型检查           |

## 最佳实践
### 跨时区协作方案
```python
# 旧金山团队（UTC-8）与北京团队（UTC+8）时间同步
beijing_time = timestamp2str(1715827200, hours=8)
sf_time = timestamp2str(1715827200, hours=-8)
```

### 财务报表周期计算
```python
# 获取上季度时间范围
start, end = get_month_range(2024, 4, long=-3)
```

## 性能优化
1. 批量处理使用`get_this_days_range`替代循环
2. 高频调用时缓存时区配置
3. 微秒操作使用整数运算替代浮点数

## 版本记录
- v3.2 (2024-05) 增加月末特性保持逻辑
- v3.1 (2024-03) 优化时区处理性能
- v3.0 (2024-01) 重构日期范围计算核心

> 注意：所有时间计算均基于服务器UTC时间，通过hours/minutes参数实现时区转换