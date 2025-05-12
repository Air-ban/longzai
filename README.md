# 龙仔Telegram Bot后端使用助手
## 目录结构
- changelog.txt 更新日志
- chat_only.py 只适用于基础对话的后端，无画图功能
- flux_workflow.json 使用支持绘图的后端后，适用的comfyui工作流的API格式
- image.py 用于调用Comfyui API的绘图脚本
- requirements.txt 项目依赖文件 
- start.py 包含完整功能的龙仔后端

### 使用指南
对于普通用户来说，只需要先安装依赖，然后配置好token和模型，即可一键启动，以下是一些步骤

- 第一步，安装依赖，使用下列指令一键安装即可

`pip install -r requirements.txt`

- 第二部，配置token

在chat_only.py和start.py的开头，均有token配置选项

`TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")`

看得出来，需要将token设置到系统变量当中，当然，如果你希望明文（不推荐）显示token在文件内，直接将后面的部分替换为token即可

如何设置环境变量呢？

在Linux中

`export TELEGRAM_BOT_TOKEN=xxxxxx(此处输入你的token)`

在Windows中（Powershell）

`$env:TELEGRAM_BOT_TOKEN=xxxxxx(此处输入你的token)`

- 第三步，配置模型

如果你的模型在本地，并且和我一样使用ollama部署，那么，你只需要修改模型名称就可以了

`$OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "lzv2:latest")`

此处，既可以设置变量，也可以直接修改，建议直接明文写在文件内，也就是后面`lzv2:latest`的部分，直接修改为你自己的模型名称即可

配置好模型名称后，配置ollama服务器，不过配置一般都不用动

- 第四步，启动！

