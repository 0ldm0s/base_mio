# file_utils.py 模块使用手册

## 模块位置
`mio/util/Helper/file_utils.py`

## 功能概述
提供基础文件操作工具集，包含以下核心功能：
- 文件锁机制（分布式锁实现）
- 文本文件读写（自动编码处理）
- 目录遍历（递归/非递归模式）
- 路径匹配（Ant风格路径匹配）
- 文件校验（存在性检查、类型验证）
- 列表清理（无效项过滤）
- 路径标准化处理

## 核心函数说明

### 1. 文件锁操作
#### `file_unlock(filename: str) -> Tuple[int, str]`
**解锁操作**
```python
def file_unlock(filename: str) -> Tuple[int, str]
```
**参数说明**：
- `filename`: 要解锁的文件名

**返回值**：
- (状态码, 信息)：1=解锁成功，-1=异常

**使用示例**：
```python
status, msg = file_unlock("data.lock")
if status == 1:
    print("解锁成功")
```
```python
def file_lock(filename: str, 
             txt: str = " ",
             exp: int = None,
             reader: bool = False) -> Tuple[int, str]
```
**参数说明**：
- `filename`: 锁文件名（自动存储在项目lock目录）
- `txt`: 锁定时的附加信息（默认空格）
- `exp`: 过期时间（分钟）
- `reader`: 是否返回锁文件内容

**返回值**：
- (状态码, 信息)：1=锁定成功，0=已被锁定，-1=异常

**使用示例**：
```python
# 获取文件锁（有效期30分钟）
status, msg = file_lock("data.lock", exp=30)
if status == 1:
    # 执行需要同步的操作
    file_unlock("data.lock")
```

### 2. 安全文件读写
```python
def read_txt_file(filename: str,
                 encoding: str = "UTF-8",
                 console_log=None) -> str

def write_txt_file(filename: str,
                  txt: str = " ",
                  encoding: str = "UTF-8") -> Tuple[bool, str]
```

**特性**：
- 自动处理文件编码问题
- 错误日志可定向到控制台输出
- 写入前自动清除旧文件

**最佳实践**：
```python
# 安全读取配置文件
config = read_txt_file("config/app.conf")

# 带错误日志的写入操作
success, msg = write_txt_file("log/audit.log",
                             "操作记录",
                             console_log=logger)
```

### 3. 目录遍历
```python
def get_file_list(root_path: str,
                 files: Optional[List[str]] = None,
                 is_sub: bool = False,
                 is_full_path: bool = True,
                 include_hide_file: bool = False) -> List[str]
```

**参数说明**：
- `is_sub`: 是否递归子目录
- `is_full_path`: 返回完整路径
- `include_hide_file`: 包含隐藏文件

**使用示例**：
```python
# 获取src目录下所有py文件（递归）
py_files = get_file_list("src", is_sub=True)
py_files = [f for f in py_files if f.endswith(".py")]
```

### 6. 路径匹配工具
#### `ant_path_matcher(ant_path: str, expected_path: str) -> bool`
**Ant风格路径匹配**
```python
def ant_path_matcher(ant_path: str, expected_path: str) -> bool
```
**匹配规则**：
- `*` 匹配任意字符（除路径分隔符）
- `**` 匹配任意路径
- `?` 匹配单个字符

**使用示例**：
```python
if ant_path_matcher("src/**/*.py", "src/utils/helper.py"):
    print("路径匹配成功")
```

### 7. 列表处理工具
#### `check_file_in_list(file: str, file_list: List[str] = None) -> bool`
**检查文件是否在列表中**
```python
def check_file_in_list(file: str, file_list: List[str] = None) -> bool
```
**特性**：
- 不区分大小写
- 支持前缀匹配

#### `chear_list(waiting: List, check_type: type = str) -> List`
**清理列表无效项**
```python
def chear_list(waiting: List, check_type: type = str) -> List
```
**过滤规则**：
- 移除非指定类型的元素
- 字符串类型自动去除两端空格
- 过滤空字符串

**使用示例**：
```python
cleaned = chear_list(["a", 1, None, "  "], check_type=str)
# 结果：["a"]
```

## 异常处理指南
| 异常类型              | 触发条件                  | 处理建议                 |
|-----------------------|--------------------------|--------------------------|
| FileNotFoundError     | 文件不存在                | 检查路径有效性           |
| UnicodeDecodeError    | 编码不匹配                | 指定正确编码格式         |
| PermissionError       | 权限不足                  | 检查文件权限设置         |

## 性能优化建议
1. 批量文件操作时使用`get_file_list`代替多次`os.listdir`
2. 频繁读写操作建议配合文件锁使用
3. 大文件处理使用流式读取（见`read_txt_file`实现）

## 版本兼容性
- Python ≥ 3.8
- 编码标准：UTF-8
- 依赖：标准库 os/re/time/typing/zlib
- 可选依赖：flask（用于获取应用密钥）

> 注意：所有路径参数均基于项目根目录，通过`get_root_path()`自动解析