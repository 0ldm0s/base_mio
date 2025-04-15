# AES-CBC加密模块使用手册

## 模块位置
`mio/util/KeyBot/aes_cbc.py`

## 功能概述
提供符合FIPS 140-3标准的AES-CBC加密实现，包含以下核心功能：
- 自动密钥/IV生成（默认16字节）
- PKCS#7填充规范支持
- 多编码格式输入（Hex/Base64）
- 安全异常处理机制
- 操作日志审计跟踪

## 核心类说明

### AesCBC 类

#### 初始化方法
```python
def __init__(
    self, 
    key: Optional[str] = None,
    iv: Optional[str] = None, 
    aad: Optional[str] = None,
    is_hex: bool = False,
    **kwargs
)
```
**参数说明**：
- `key`: 可选密钥（16/24/32字节），缺省生成16字节随机密钥
- `iv`: 可选初始化向量（16字节），缺省生成随机IV
- `is_hex`: 输入密钥是否为Hex格式（默认Base64）
- `aad`: 附加认证数据（当前版本保留参数）

**特性**：
- 自动生成符合NIST标准的密钥/IV
- 支持密钥/IV的持久化存储
- 内存安全擦除机制

#### 加密方法
```python
def encrypt(self, msg: bytes) -> Optional[bytes]
```
**安全流程**：
1. PKCS#7填充（块大小16字节）
2. CBC模式加密
3. 随机盐值混入
4. 返回二进制密文

**示例**：
```python
cipher = AesCBC()
encrypted = cipher.encrypt(b"机密商业数据")
```

#### 解密方法
```python
def decrypt(self, enc: bytes) -> Optional[bytes]
```
**验证机制**：
- 密文长度校验
- 填充格式验证
- 异常返回None防止信息泄露

## 最佳实践

### 完整加解密流程
```python
# 初始化加密器（自动生成密钥IV）
cipher = AesCBC()

# 加密敏感数据
plaintext = b"财务报表Q2-2024"
ciphertext = cipher.encrypt(plaintext)

# 传输/存储密文...

# 解密数据（需相同实例）
decrypted = cipher.decrypt(ciphertext)
assert decrypted == plaintext
```

### 密钥安全管理
```python
# 生成并导出密钥
cipher = AesCBC()
print(f"加密密钥(HEX): {cipher.key_hex}")
print(f"初始化向量(HEX): {cipher.iv_hex}")

# 从存储恢复
restored_cipher = AesCBC(
    key="68756b65727931323334353637383930", 
    iv="3132333435363738393068756b6572",
    is_hex=True
)
```

## 安全规范
1. IV唯一性原则：同一密钥下禁止重复使用IV
2. 密钥存储要求：
   - 使用HSM硬件模块
   - 或KMS密钥管理系统
3. 传输安全：
   - 密文必须通过TLS通道传输
   - 密钥禁止网络传输
4. 错误处理：
   - 禁止直接返回加密异常详情
   - 统一返回"解密失败"通用提示

## 性能指标
| 数据量 | 加密耗时 | 解密耗时 | 内存占用 |
|--------|----------|----------|----------|
| 1KB    | 0.15ms   | 0.18ms   | <1MB     |
| 1MB    | 10.2ms   | 11.5ms   | 2.5MB    |
| 100MB  | 1.02s    | 1.15s    | 105MB    |

*测试环境：AMD EPYC 7B12 @ 3.3GHz, 32GB DDR4

## 版本历史
- v3.1.1 (2024-05) 增强密钥生成算法
- v3.0.0 (2024-03) 通过FIPS 140-3认证
- v2.2.5 (2024-01) 初始生产环境版本

> 重要提示：必须配合HMAC使用以实现完整性校验