import os
import time
import json
import asyncio
from telegram import Bot
from telegram.error import TelegramError

class TelegramNotifier:
    def __init__(self, config_path, token):
        self.config_path = config_path
        self.token = token
        self.bot = Bot(token=token)
        self.last_modified = os.path.getmtime(config_path)
        self.processed_presets = set()
        self._load_config()

    def _load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.white_list = config.get('white_list', [])
                for preset in config.get('user_lora', {}):
                    self.processed_presets.add(preset)
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            self.white_list = []
            print("初始配置加载失败")

    async def _send_message(self, chat_id, message):
        try:
            await self.bot.send_message(chat_id=chat_id, text=message)
            print(f"消息已发送至 chat_id: {chat_id}")
        except TelegramError as e:
            print(f"Telegram错误：{str(e)}")
        except Exception as e:
            print(f"网络或未知错误：{str(e)}")

    def _update_config(self, config, preset_name):
        config['white_list'].append(preset_name)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        self.processed_presets.add(preset_name)

    async def _monitor_task(self):
        while True:
            try:
                current_modified = os.path.getmtime(self.config_path)
                if current_modified != self.last_modified:
                    try:
                        with open(self.config_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                            for preset_name, preset_data in config.get('user_lora', {}).items():
                                if preset_name in self.white_list or preset_name in self.processed_presets:
                                    continue
                                chat_id = preset_data['chat_id']
                                print(f"首次检测到新预设 {preset_name}，chat_id: {chat_id}")
                                await self._send_message(chat_id, f"您好！预设 {preset_name} 已成功训练完毕。")
                                self._update_config(config, preset_name)
                            self.last_modified = current_modified
                    except FileNotFoundError:
                        print("错误：配置文件未找到")
                    except json.JSONDecodeError:
                        print("错误：配置文件解析失败")
                    except KeyError as e:
                        print(f"错误：缺少必要字段 {e}")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"通用异常：{str(e)}")
                await asyncio.sleep(5)

    def monitor(self):
        asyncio.create_task(self._monitor_task())

if __name__ == '__main__':
    notifier = TelegramNotifier('d:/longzai_test/config.json', '8101052682:AAFHdZglMXKvGqEzCCDgrV7RNJ5OEpxqSm8')
    notifier.monitor()