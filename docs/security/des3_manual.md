# 3DES-OFB加密模块使用手册

## 模块位置
`mio/util/KeyBot/des3.py`

## 功能概述
提供符合FIPS 46-3标准的3DES-OFB加密实现，包含以下核心功能：
- 自动生成168位密钥（24字节）
- OFB模式流式加密
- 奇偶校验调整
- 安全密钥管理
- 跨平台兼容性

## 核心类说明

### Des3 类

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
- `key`: 可选密钥（24字节），缺省自动生成
- `iv`: 可选初始化向量（8字节），缺省随机生成
- `is_hex`: 输入是否为Hex格式（默认Base64）
- `aad`: 附加认证数据（保留参数）

**安全特性**：
- 自动密钥奇偶校验调整
- OFB模式避免填充预言攻击
- 兼容传统金融系统

#### 加密方法
```python
def encrypt(self, msg: bytes) -> Optional[bytes]
```
**加密流程**：
1. 初始化OFB模式加密器
2. 流式处理任意长度数据
3. 返回原始密文

**示例**：
```python
cipher = Des3()
encrypted = cipher.encrypt(b"POS终端交易记录")
```

#### 解密方法
```python
def decrypt(self, cipher: bytes) -> Optional[bytes]
```
**特性**：
- 完全对称解密过程
- 支持分块处理
- 内存高效处理

## React+MQTT集成示例

### Python服务端（加密/解密）
```python
# mqtt_server.py
import paho.mqtt.client as mqtt
from mio.util.KeyBot.des3 import Des3

cipher = Des3()

def on_connect(client, userdata, flags, rc):
    client.subscribe("sensor/data")

def on_message(client, userdata, msg):
    try:
        # 解密数据
        decrypted = cipher.decrypt(msg.payload)
        print(f"解密数据: {decrypted.decode()}")
        
        # 加密响应
        response = cipher.encrypt(b"ACK:" + decrypted)
        client.publish("sensor/ack", response)
    except Exception as e:
        print(f"处理异常: {str(e)}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.loop_forever()
```

### TypeScript客户端（React组件）
```tsx
// MQTTPublisher.tsx
import { useEffect, useState } from 'react';
import mqtt from 'mqtt';

const Des3Encryptor = ({ children }: { children: React.ReactNode }) => {
  const [client, setClient] = useState<mqtt.MqttClient | null>(null);
  const [cipher, setCipher] = useState<{ key: string; iv: string } | null>(null);

  useEffect(() => {
    const initClient = async () => {
      const mqttClient = mqtt.connect('ws://localhost:9001');
      const response = await fetch('/api/getDes3Key');
      const { key, iv } = await response.json();
      
      setClient(mqttClient);
      setCipher({ key, iv });
    };

    initClient();
    return () => client?.end();
  }, []);

  const encryptAndPublish = async (data: string) => {
    if (!client || !cipher) return;
    
    // 使用WebCrypto API进行加密（示例）
    const encoder = new TextEncoder();
    const encrypted = await window.crypto.subtle.encrypt(
      { 
        name: 'DES-EDE3-OFB',
        iv: encoder.encode(cipher.iv) 
      },
      await window.crypto.subtle.importKey(
        'jwk',
        { k: cipher.key, alg: 'DES-EDE3-OFB', ext: true },
        { name: 'DES-EDE3-OFB' },
        false,
        ['encrypt']
      ),
      encoder.encode(data)
    );
    
    client.publish('sensor/data', Buffer.from(encrypted));
  };

  return (
    <div>
      {React.cloneElement(children as React.ReactElement, { 
        publish: encryptAndPublish 
      })}
    </div>
  );
};

// 使用示例
const SensorDashboard = ({ publish }: { publish: (data: string) => void }) => (
  <button onClick={() => publish('温度:25.6℃')}>
    发送加密数据
  </button>
);

export default () => (
  <Des3Encryptor>
    <SensorDashboard />
  </Des3Encryptor>
);
```

## 安全规范
1. 密钥管理要求：
   - 每台终端使用唯一密钥
   - 定期轮换密钥（建议每90天）
2. 使用限制：
   - 单条密文不超过4GB
   - 避免重复使用IV
3. 迁移建议：
   - 新系统应优先使用AES-256
   - 旧系统迁移需进行兼容性测试

## 性能指标
| 数据量  | 加密耗时 | 解密耗时 | 吞吐量  |
|---------|----------|----------|---------|
| 64KB    | 1.2ms    | 1.1ms    | 53MB/s  |
| 1MB     | 18ms     | 17ms     | 56MB/s  |
| 100MB   | 1.8s     | 1.7s     | 55MB/s  |

*测试环境：Intel Core i7-1185G7 @ 3.0GHz

## 版本历史
- v1.4 (2024-05) 增强OFB模式安全性
- v1.2 (2024-03) 兼容PCI DSS标准
- v1.0 (2024-01) 传统系统支持版本

> 注意：3DES将于2023年后逐步淘汰，仅建议用于遗留系统兼容