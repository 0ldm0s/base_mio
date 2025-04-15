# 加密工具模块使用手册

## 模块概述
`crypto_utils` 提供基础加密算法实现和安全工具类，包含以下核心功能：
- 常用哈希算法（MD5）
- 数据编码（Base64标准/URL安全版）
- 文件校验（CRC32）
- 可配置的加密/解密流程
- 密钥格式验证（PEM/SSH）
- 椭圆曲线数字签名（需cryptography库）

```python
from mio.util.Helper import crypto_utils

# 生成MD5哈希
hash = crypto_utils.md5("secret")

# Base64编码解码
encoded = crypto_utils.base64_encode(b"data")
decoded = crypto_utils.base64_decode(encoded)

# 文件CRC校验
crc = crypto_utils.crc_file("/path/to/file")
```

## 数据编码工具
### `base64_encode(message: bytes, is_bytes=True)`
原始Base64编码
```python
# 编码字节数据
encoded_bytes = crypto_utils.base64_encode(b"binary_data")

# 编码为字符串
encoded_str = crypto_utils.base64_encode(b"data", is_bytes=False)
```

### `base64_txt_encode(message: str)`
文本专用Base64编码
```python
text_encoded = crypto_utils.base64_txt_encode("中文文本")
```

### `base64url_encode(_input: bytes)`
URL安全Base64编码
```python
url_safe = crypto_utils.base64url_encode(b"data?with=special_chars")
```

## 密钥管理
### `is_pem_format(key: bytes)`
验证PEM格式密钥
```python
with open("key.pem", "rb") as f:
    if crypto_utils.is_pem_format(f.read()):
        print("Valid PEM format")
```

### `is_ssh_key(key: bytes)`
验证SSH密钥格式
```python
if crypto_utils.is_ssh_key(b"ssh-rsa AAAAB3Nz..."):
    print("Valid SSH public key")
```

## 数字签名工具
### `der_to_raw_signature(der_sig: bytes, curve)`
DER转RAW签名格式
```python
from cryptography.hazmat.primitives.asymmetric import ec
private_key = ec.generate_private_key(ec.SECP256R1())
raw_sig = crypto_utils.der_to_raw_signature(der_sig, private_key.curve)
```

### `raw_to_der_signature(raw_sig: bytes, curve)`
RAW转DER签名格式
```python
der_sig = crypto_utils.raw_to_der_signature(raw_sig, curve)
```

## 底层数值转换
### `bytes_from_int(val: int)`
整数转字节序列
```python
bytes_data = crypto_utils.bytes_from_int(0x1234)
```

### `number_to_bytes(num: int, num_bytes: int)`
带长度限制的整数转换
```python
# 将整数转换为4字节表示
bytes_4 = crypto_utils.number_to_bytes(123456, 4)
```

### `bytes_to_number(_string: bytes)`
字节转整数
```python
num = crypto_utils.bytes_to_number(b"\x01\x02")
```

### `to_base64url_uint(val: int)`
大整数Base64URL编码
```python
big_num = 0x1234567890ABCDEF
encoded = crypto_utils.to_base64url_uint(big_num)
```

### `from_base64url_uint(val: str|bytes)`
Base64URL解码为整数
```python
original_num = crypto_utils.from_base64url_uint("EjRWeJCrze8")
```

## 核心函数说明

### `easy_encrypted(text, is_decode, key, expiry, console_log)`
动态密钥加密方法

| 参数        | 类型     | 必填 | 说明                  |
|-------------|----------|------|---------------------|
| text        | str      | 是   | 待处理文本             |
| is_decode   | bool     | 否   | 操作模式（默认True解密）|
| key         | str      | 否   | 加密密钥（默认取应用密钥）|
| expiry      | int      | 否   | 有效期（秒）           |
| console_log | Logger   | 否   | 日志记录器             |

```python
# 加密示例
encrypted = crypto_utils.easy_encrypted("plaintext", 
                                      is_decode=False, 
                                      expiry=3600,
                                      key="custom_secret")

# 带日志的解密示例
decrypted = crypto_utils.easy_encrypted(encrypted, 
                                      console_log=logger)
```

### `der_to_raw_signature(der_sig, curve)`
椭圆曲线签名转换（需要cryptography库）

| 参数     | 类型            | 说明                |
|----------|-----------------|-------------------|
| der_sig  | bytes           | DER编码的签名        |
| curve    | EllipticCurve   | 椭圆曲线对象         |

### `is_pem_format(key)`
验证PEM格式密钥

```python
with open("private.pem", "rb") as f:
    if crypto_utils.is_pem_format(f.read()):
        print("Valid PEM format")
```

### `is_ssh_key(key)`
验证SSH密钥格式

```python
ssh_pubkey = b"ssh-rsa AAAAB3Nz..."
if crypto_utils.is_ssh_key(ssh_pubkey):
    print("Valid SSH key")
```

## 高级功能
### Base64 URL安全编码
```python
url_safe = crypto_utils.base64url_encode(b"data?with=special_chars")
decoded = crypto_utils.base64url_decode(url_safe)
```

### 数字签名转换
```python
# 需要安装cryptography库
from cryptography.hazmat.primitives.asymmetric import ec

private_key = ec.generate_private_key(ec.SECP256R1())
raw_sig = crypto_utils.der_to_raw_signature(der_sig, private_key.curve)
```

## 安全注意事项
1. ⚠️ MD5仅适用于非安全场景，禁止用于密码存储
2. 密钥管理规范：
   - 生产环境密钥长度应≥32字符
   - 定期轮换加密密钥（建议每90天）
   - 禁止硬编码密钥到源码中
3. 有效期控制：
   ```python
   # 设置1小时有效期的加密数据
   crypto_utils.easy_encrypted(..., expiry=3600)
   ```
4. 日志安全：
   - 通过console_log参数记录错误时，自动屏蔽敏感信息
   - 禁止记录完整密钥或未加密数据

## 异常处理规范
| 异常类型                 | 触发条件                      | 解决方案               |
|--------------------------|-----------------------------|----------------------|
| RuntimeError             | 缺少cryptography库           | 安装必要依赖           |
| ValueError               | 无效的Base64输入             | 检查数据编码格式       |
| UnicodeDecodeError       | 非UTF-8字符解码              | 指定正确编码参数       |
| TypeError                | 无效的密钥格式               | 使用is_pem_format验证 |

## 性能优化建议
1. 批量处理数据时使用上下文管理器：
   ```python
   with open("large_file.bin", "rb") as f:
       while chunk := f.read(4096):
           crypto_utils.md5(chunk)
   ```
2. 启用ZLIB加速：
   ```bash
   pip install zlib-ng
   ```

## 版本记录
- v1.3 (2025-04) 增加SSH密钥验证功能
- v1.2 (2025-03) 增加椭圆曲线支持
- v1.1 (2025-01) 优化密钥派生算法
- v1.0 (2024-12) 基础加密功能实现