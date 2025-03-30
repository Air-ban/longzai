import websocket
import uuid
import json
import urllib.request
import urllib.parse
import os
from PIL import Image
import io
import argparse

# 设置 ComfyUI 的服务器地址和客户端 ID
server_address = "127.0.0.1:8188"  # 如果远程访问，替换为实际的 IP 和端口
client_id = str(uuid.uuid4())

# 定义向 ComfyUI 发送绘图任务的函数
def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

# 定义获取生成的图像数据的函数
def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()

# 定义获取任务历史记录的函数
def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

# 定义获取生成的图像的函数
def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break
                else:
                    continue
    
    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
        output_images[node_id] = images_output
    return output_images

# 定义读取工作流 JSON 文件的函数
def read_json(api_file="flux_workflow.json"):
    with open(api_file, "r", encoding="utf-8") as file_json:
        prompt_text = json.load(file_json)
    return prompt_text

# 定义文本到图像的函数
def text_to_image(prompt_text, local_save_dir='./output', api_file='flux_workflow.json', lora1_name=None, lora1_strength=None, lora2_name=None, lora2_strength=None):
    prompt = read_json(api_file)
    
    # 更新文本提示
    prompt["6"]["inputs"]["text"] = prompt_text
    
    # 如果需要，可以在这里更新其他参数，例如：
    prompt["17"]["inputs"]["steps"] = 18
    prompt["27"]["inputs"]["width"] = 1024
    prompt["27"]["inputs"]["height"] = 1024
    
    # 更新 LoRA 设置
    if lora1_name is not None:
        prompt["31"]["inputs"]["lora_name"] = lora1_name
    if lora1_strength is not None:
        prompt["31"]["inputs"]["strength_model"] = lora1_strength
    if lora2_name is not None:
        prompt["32"]["inputs"]["lora_name"] = lora2_name
    if lora2_strength is not None:
        prompt["32"]["inputs"]["strength_model"] = lora2_strength
    
    ws = websocket.WebSocket()
    ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
    images = get_images(ws, prompt)
    
    os.makedirs(local_save_dir, exist_ok=True)
    save_paths = []  # 用于存储生成的图片路径
    
    # 使用计数器生成唯一的数字文件名
    counter = 1
    for node_id in images:
        for i, image_data in enumerate(images[node_id]):
            image = Image.open(io.BytesIO(image_data))
            save_path = f"{local_save_dir}/image_{counter}.png"
            image.save(save_path)
            save_paths.append(save_path)
            counter += 1
    ws.close()
    
    # 返回所有生成的图片路径
    return save_paths

# 主函数，执行绘图操作
if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='使用 ComfyUI API 进行文本到图像生成')
    parser.add_argument('--prompt', type=str, required=True, help='自定义的文本提示词')
    parser.add_argument('--api_file', type=str, default='flux_workflow.json', help='工作流 JSON 文件路径')
    parser.add_argument('--local_save_dir', type=str, default='./output', help='生成图像的保存目录')
    parser.add_argument('--lora1_name', type=str, help='第一个 LoRA 的名称')
    parser.add_argument('--lora1_strength', type=float, help='第一个 LoRA 的强度')
    parser.add_argument('--lora2_name', type=str, help='第二个 LoRA 的名称')
    parser.add_argument('--lora2_strength', type=float, help='第二个 LoRA 的强度')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 调用文本到图像函数
    save_paths = text_to_image(
        prompt_text=args.prompt,
        api_file=args.api_file,
        local_save_dir=args.local_save_dir,
        lora1_name=args.lora1_name,
        lora1_strength=args.lora1_strength,
        lora2_name=args.lora2_name,
        lora2_strength=args.lora2_strength
    )
    
    # 打印所有生成的图片路径
    for path in save_paths:
        print(path)