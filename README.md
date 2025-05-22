# 龙仔Telegram Bot后端

## 项目介绍

龙仔Telegram Bot是一个基于Python的Telegram机器人后端，提供AI聊天和图像生成功能。机器人使用Ollama作为AI模型后端，支持自定义角色设定、聊天记忆和图像生成等功能。

## 目录结构

- `changelog.txt` - 更新日志
- `chat_only.py` - 只适用于基础对话的后端，无画图功能
- `flux_workflow.json` - 使用支持绘图的后端后，适用的ComfyUI工作流的API格式
- `image.py` - 用于调用ComfyUI API的绘图脚本
- `requirements.txt` - 项目依赖文件
- `start.py` - 包含完整功能的龙仔后端
- `config.json` - 配置文件，包含LoRA预设等设置

## 功能特性

### 基础功能

- AI聊天对话，支持上下文记忆
- 自定义角色设定（名字、年龄、描述等）
- 图像生成功能，支持自定义提示词
- LoRA预设切换，支持多种角色风格
- 自定义LoRA项目管理，支持上传图片训练LoRA

### 最新更新

- 生图功能强势回归
- 回复速度大幅提升
- 支持自定义上传图片并训练LoRA
- 更多优化和改进

## 安装指南

### 环境要求

- Python 3.8+
- Ollama服务
- ComfyUI（用于图像生成）

### 安装步骤

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置Telegram Bot Token

在`chat_only.py`和`start.py`的开头，均有token配置选项：

```python
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
```

您需要将token设置到系统环境变量中，或者直接在代码中替换为您的token（不推荐）。

设置环境变量的方法：

- Linux:
```bash
export TELEGRAM_BOT_TOKEN=xxxxxx(此处输入你的token)
```

- Windows (PowerShell):
```powershell
$env:TELEGRAM_BOT_TOKEN=xxxxxx(此处输入你的token)
```

3. 配置AI模型

如果您使用Ollama部署本地模型，只需修改模型名称：

```python
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "lzv2:latest")
```

您可以直接修改默认值`lzv2:latest`为您自己的模型名称。

4. 配置ComfyUI（用于图像生成）

确保ComfyUI服务已启动，默认地址为`127.0.0.1:8188`。如需修改，请在`image.py`中更新`server_address`变量。

## 使用指南

### 启动机器人

- 启动基础聊天机器人（无图像生成功能）：
```bash
python chat_only.py
```

- 启动完整功能机器人（包含图像生成）：
```bash
python start.py
```

### 可用命令

#### 核心命令

- `/start` - 开始与机器人对话
- `/set_name [名字]` - 设置AI名字
- `/set_age [年龄]` - 设置AI年龄
- `/set_desc [描述]` - 添加描述（不会覆盖原有描述）
- `/myprofile` - 查看当前设定
- `/reset` - 重置对话历史
- `/help` - 显示帮助信息
- `/log` - 查看更新日志

#### 绘图相关命令

- `/image [提示词]` - 生成图片，例如：`/image a cute boy`
- `/image_option [预设名称]` - 切换生图预设（可用预设：凯文/龙仔/李球球）
- `/image_prompt` - 获取图片提示词示例
- `/random_image` - 使用随机提示词生成图片
- `/custom_lora` - 自定义LoRA项目管理

### 自定义LoRA项目

1. 使用`/custom_lora`命令进入项目管理
2. 选择现有项目或创建新项目
3. 上传图片进行训练

## 配置文件说明

`config.json`文件包含LoRA预设配置，可以根据需要修改：

```json
{
    "default_lora": {
        "lora1_name": "xxx.safetensors",
        "lora1_strength": 1.0,
        "lora2_name": "xxx.safetensors",
        "lora2_strength": 0.8
    },
    "lora_presets": {
        "预设名称": {
            "lora1_name": "xxx.safetensors",
            "lora1_strength": 1.0,
            "lora2_name": "xxx.safetensors",
            "lora2_strength": 0.8
        }
    }
}
```

## 注意事项

- 图像生成功能仅在私聊中可用
- 确保ComfyUI服务已正确配置并启动
- 自定义LoRA项目需要足够的存储空间

## 故障排除

- 如果遇到连接问题，请检查Ollama和ComfyUI服务是否正常运行
- 如果图像生成失败，请检查ComfyUI配置和工作流文件
- 如果命令无响应，请尝试重启机器人

