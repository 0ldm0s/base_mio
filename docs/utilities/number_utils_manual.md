# 数字处理工具模块使用手册

## 模块位置
`mio/util/Helper/number_utils.py`

## 功能概述
提供安全可靠的数字处理工具集，包含以下核心功能：
- 多类型数字安全求和
- 高精度四舍五入
- 随机数生成（非字符串）
- 数值格式验证与清洗

## 核心函数说明

### 1. 安全数值计算
#### `do_sum(*args) -> Decimal`
```python
def do_sum(*args) -> Decimal
```
**功能特点**：
- 自动过滤非数字参数（str/float/int）
- 支持Decimal高精度计算
- 线程安全

**示例**：
```python
sum_result = do_sum("12.34", 56, "invalid", 78.9)  # 返回Decimal('147.24')
```

### 2. 随机数生成
#### `random_number(random_length=8) -> int`
```python
def random_number(random_length: int = 8) -> int
```
**安全特性**：
- 首位非零保证
- 纯数字输出（非字符串）
- 长度自动校正（≥1位）

**应用场景**：
```python
# 生成8位交易流水号
txn_id = random_number(8)  # 示例：58273649
```

### 3. 高精度舍入
#### `rounded(numerical, decimal=2) -> Decimal`
```python
def rounded(numerical: Any, decimal: int = 2) -> Decimal
```
**银行家舍入规则**：
- 四舍六入五成双
- 精确处理0.5边界情况
- 支持负数运算

**对比常规舍入**：
```python
rounded(2.675, 2)  # 返回Decimal('2.68') 
round(2.675, 2)    # 返回2.67
```

## 最佳实践
### 金融计算场景
```python
# 计算订单总金额（自动过滤无效值）
amounts = [item['price'] for item in order_items]
total = do_sum(*amounts).quantize(Decimal('0.00'))
```

### 验证码生成方案
```python
# 生成6位短信验证码
sms_code = random_number(6)  # 示例：317582
```

## 异常处理指南
| 异常类型         | 触发条件                | 解决方案               |
|------------------|-------------------------|-----------------------|
| InvalidOperation | 无效Decimal转换        | 前置数据清洗          |
| TypeError        | 非数值类型迭代输入      | 使用前验证is_number   |
| OverflowError    | 超出数值范围            | 启用异常捕获机制      |

## 性能优化建议
1. 批量计算优先使用Decimal上下文
2. 高频随机数生成使用独立Random实例
3. 数值验证使用短路判断优化

## 版本记录
- v2.3 (2024-05) 增强银行家舍入算法
- v2.2 (2024-03) 优化随机数生成性能
- v2.1 (2024-01) 增加多线程安全支持

> 注意：所有金额计算默认使用Decimal类型，避免浮点精度问题