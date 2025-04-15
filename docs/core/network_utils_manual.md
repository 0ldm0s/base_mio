# network_utils.py 网络工具模块手册

## 模块位置
`mio/util/Helper/network_utils.py`

## 功能概述
提供网络操作相关工具集，主要包含以下功能：
- IP地址验证与转换（IPv4/IPv6）
- 端口可用性检测（TCP/UDP）
- HTTP请求简化封装（支持RESTful）
- 网络接口信息获取（含虚拟接口）
- 公网IP探测
- URL有效性验证
- 文件下载功能

## 核心函数说明

### 1. 客户端信息处理
#### `get_real_ip(idx=0, show_all=False, ipv6only=False) -> str`
```python
def get_real_ip(idx: int = 0, show_all: bool = False, ipv6only: bool = False) -> str
```
**特性**：
- 支持多级代理检测（Cloudflare/X-Forwarded-For）
- 自动处理IPv4映射地址（::ffff:）
- 支持多IP选择（索引控制）

**优先级检测头**：
1. CF-Connecting-IP
2. X-Client
3. X-Real-IP
4. Remote-Addr

**示例**：
```python
client_ip = get_real_ip()  # 返回主要客户端IP
all_ips = get_real_ip(show_all=True)  # 返回全部代理链IP
```

#### `check_is_ip(ip_addr: str) -> bool`
```python
def check_is_ip(ip_addr: str) -> bool
```
**验证范围**：
- 严格校验IP格式（非域名）
- 支持IPv4/IPv6
- 排除内网地址

### 2. 用户代理分析
#### `check_ua(keys: List[str]) -> bool`
```python
def check_ua(keys: List[str]) -> bool
```
**检测能力**：
- 不区分大小写匹配
- 支持子字符串检测
- 多关键字OR逻辑

**示例**：
```python
if check_ua(["Android", "Mobile"]):
    print("移动端访问")
```

#### `check_bot() -> bool`
```python
def check_bot() -> bool
```
**检测规则**：
- 包含bot/spider关键字
- 排除常见浏览器标识
- Google特定检测

#### `check_ie() -> bool`
```python
def check_ie() -> bool
```
**兼容性检测**：
- 识别IE浏览器
- 检测兼容模式
- 支持新版Edge排除

### 3. 系统环境检测
#### `get_canonical_os_name() -> str`
```python
def get_canonical_os_name() -> str
```
**支持系统**：
- Windows/Mac/Linux
- BSD变种
- Apple Silicon检测
- ARM架构识别

**返回值示例**：
```python
"windows" | "mac_m1" | "linux_aarch64" | "freebsd"
```

#### `get_variable_from_request(key_name, default, method, force_str) -> Any`
```python
def get_variable_from_request(
    key_name: str,
    default: Any = "",
    method: str = "check",
    force_str: bool = False
) -> Any
```
**参数说明**：
- `method`: 检测位置（post/get/header）
- `force_str`: 强制字符串输出

**安全特性**：
- 自动类型转换
- 空值处理
- CSRF令牌保护

### 4. IP地址验证
#### `validate_ip(ip: str) -> bool`
**IP格式验证**
```python
def validate_ip(ip: str) -> bool
```
**支持类型**：
- IPv4 (192.168.1.1)
- IPv6 (2001:db8::8a2e:370:7334)
- 域名 (example.com)

**使用示例**：
```python
if validate_ip("203.0.113.42"):
    print("有效IP地址")
```

### 2. 端口检测
```python
def check_port_available(host: str, 
                       port: int, 
                       timeout: float = 1.5) -> bool
```
**参数说明**：
- `host`: 目标主机（IP或域名）
- `port`: 检测端口号
- `timeout`: 超时时间（秒）

**返回值**：
- True: 端口可用
- False: 端口不可用或超时

**使用示例**：
```python
# 检测本机80端口
if check_port_available("127.0.0.1", 80):
    print("Web服务端口已就绪")
```

### 2. HTTP请求封装
```python
def http_request(url: str,
                method: str = "GET",
                headers: dict = None,
                params: dict = None,
                data: dict = None,
                timeout: int = 10) -> Tuple[int, dict]
```
**参数说明**：
- `method`: 支持GET/POST/PUT/DELETE
- `timeout`: 超时时间（秒）

**返回值**：
- (状态码, 响应字典)
  - 成功示例：(200, {"status": "OK", "data": {...}})
  - 失败示例：(-1, {"error": "Timeout"})

**使用示例**：
```python
status, response = http_request(
    "https://api.example.com/data",
    method="POST",
    data={"key": "value"}
)
```

### 5. 网络诊断工具
#### `traceroute(host: str, max_hops: int = 30) -> Dict[int, str]`
**路由追踪实现**
```python
def traceroute(host: str, max_hops: int = 30) -> Dict[int, str]
```
**返回数据结构**：
```python
{
    1: "192.168.1.1",
    2: "10.8.0.1",
    ...
}
```

#### `network_latency_test(host: str, port: int = 80) -> float`
**网络延迟测试**
```python
def network_latency_test(host: str, port: int = 80) -> float
```
**实现原理**：
发送ICMP请求测量往返时间（RTT）

**使用示例**：
```python
latency = network_latency_test("example.com")
print(f"网络延迟：{latency:.2f}ms")
```

### 6. 公网IP探测
#### `get_public_ip() -> str`
**获取本机公网IP地址**
```python
def get_public_ip() -> str
```
**实现原理**：
通过访问第三方API（https://api.ipify.org）获取

**使用示例**：
```python
public_ip = get_public_ip()
print(f"公网IP地址：{public_ip}")
```

### 6. 高级网络工具
#### `download_file(url: str, save_path: str, timeout: int = 30) -> bool`
**文件下载工具**
```python
def download_file(url: str, save_path: str, timeout: int = 30) -> bool
```
**特性**：
- 支持大文件分块下载
- 自动处理重定向
- 进度显示（当有控制台日志时）

**使用示例**：
```python
success = download_file(
    "https://example.com/file.zip",
    "downloads/file.zip",
    timeout=60
)
```

#### `is_valid_url(url: str) -> bool`
**URL格式验证**
```python
def is_valid_url(url: str) -> bool
```
**验证规则**：
- 包含协议头（http/https）
- 有效域名格式
- 允许包含端口号和路径

**使用示例**：
```python
if is_valid_url("https://example.com:8080/api/v1"):
    print("有效URL格式")
```

## 网络接口信息获取
```python
def get_local_interfaces() -> List[Dict[str, str]]
```
**返回数据结构**：
```python
[
    {
        "name": "eth0",
        "ipv4": "192.168.1.100",
        "ipv6": "fe80::a00:27ff:fe4a:5d4c",
        "mac": "08:00:27:4a:5d:4c"
    }
]
```

## 命令行集成

### 端口扫描示例
```bash
flask cli exe -cls=mio.util.Helper.network_utils.check_port_available \
  -arg="host=127.0.0.1||port=8080"
```

### HTTP服务检测
```bash
flask cli exe -cls=mio.util.Helper.network_utils.http_request \
  -arg="url=http://localhost:8000/health"
```

## 客户端安全防护
### 请求头验证最佳实践
```python
# 检测爬虫访问
if check_bot():
    logging.warning("Bot访问被阻止")
    
# 获取安全参数
user_id = get_variable_from_request("user_id", method="post")
```

## 异常处理指南
| 错误类型              | 触发条件                  | 解决方案                 |
|-----------------------|--------------------------|--------------------------|
| ConnectionError       | 网络连接失败              | 检查目标主机可达性       |
| TimeoutError          | 请求超时                  | 调整timeout参数          |
| ValueError            | 无效IP/端口格式           | 使用validate_ip辅助函数  |
| SSLError              | 证书验证失败              | 添加verify=False参数      |
| TooManyRedirects      | 重定向次数过多            | 检查URL是否正确          |

## 性能优化建议
1. 批量端口检测使用线程池
2. HTTP请求启用连接池
3. 频繁调用的接口信息使用缓存（建议缓存时间≤5分钟）

> 注意：生产环境使用需配置合理的超时时间和重试机制

## 性能优化建议（新增）
### 连接池配置示例
```python
import requests
from requests.adapters import HTTPAdapter

session = requests.Session()
# 设置连接池最大数量
adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
session.mount('http://', adapter)
session.mount('https://', adapter)

# 在http_request中使用自定义session
status, response = http_request("https://api.example.com", session=session)
```

## 版本更新记录
- v2.1 (2025-03) 新增文件下载分块功能
- v2.0 (2025-01) 支持IPv6地址验证
- v1.5 (2024-12) 初始版本发布