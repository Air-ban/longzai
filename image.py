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
def read_json(api_file="api_demo.json"):
    with open(api_file, "r", encoding="utf-8") as file_json:
        prompt_text = json.load(file_json)
    return prompt_text

# 定义文本到图像的函数
def text_to_image(prompt_text, local_save_dir='./output', api_file='api_demo.json'):
    prompt = read_json(api_file)
    
    # 更新文本提示
    prompt["6"]["inputs"]["text"] = prompt_text
    
    # 如果需要，可以在这里更新其他参数，例如：
    # prompt["17"]["inputs"]["steps"] = 30
    # prompt["27"]["inputs"]["width"] = 768
    # prompt["27"]["inputs"]["height"] = 768
    
    ws = websocket.WebSocket()
    ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
    images = get_images(ws, prompt)
    
    os.makedirs(local_save_dir, exist_ok=True)
    for node_id in images:
        for i, image_data in enumerate(images[node_id]):
            image = Image.open(io.BytesIO(image_data))
            save_path = f"{local_save_dir}/{prompt_text[:20]}_{i}.png"
            image.save(save_path)
            print(f"Saved image to {save_path}")
    ws.close()

# 主函数，执行绘图操作
if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='使用 ComfyUI API 进行文本到图像生成')
    parser.add_argument('--prompt', type=str, required=True, help='自定义的文本提示词')
    parser.add_argument('--api_file', type=str, default='api_demo.json', help='工作流 JSON 文件路径')
    parser.add_argument('--local_save_dir', type=str, default='./output', help='生成图像的保存目录')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 调用文本到图像函数
    text_to_image(
        prompt_text=args.prompt,
        api_file=args.api_file,
        local_save_dir=args.local_save_dir
    )