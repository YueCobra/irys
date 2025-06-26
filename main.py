import sys
import os
from loguru import logger
import asyncio
import httpx
from dotenv import load_dotenv
# 加载 .env 文件
load_dotenv()

# 读取环境变量
yes_captcha_key = os.getenv('YESCAPTCHA_KEY')


class IrySwap(object):
    def __init__(self,address,proxy = None):
        self.address = address
        self.snake_cost = 0.02
        self.frogger_cost = 0.05
        self.tetris_cost = 0.1
        self.http = httpx.AsyncClient(timeout=20,proxy=proxy)
        # yescaptcha配置
        self.websiteKey = '0x4AAAAAAA6vnrvBCtS4FAl-'
        self.websiteURL = 'https://irys.xyz/faucet'
        self.yescaptcha_url = "https://api.yescaptcha.com"

    async def request_faucet(self,captcha_token):
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            # 'cookie': '_ga=GA1.1.362875673.1749012201; _ga_R81GG8F2BB=GS2.1.s1749091501$o5$g0$t1749092372$j60$l0$h0; _ga_EG4KQLLHZ6=GS2.1.s1749627631$o15$g0$t1749627631$j60$l0$h0; _ga_N7ZGKKSTW8=GS2.1.s1750936939$o7$g0$t1750936939$j60$l0$h0',
            'origin': 'https://irys.xyz',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://irys.xyz/faucet',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        json_data = {
            'captchaToken': captcha_token,
            'walletAddress': self.address,
        }
        try:
            resp = await self.http.post('https://irys.xyz/api/faucet', headers=headers, json=json_data)
            logger.info(f"领取结果: {resp.text}")
        except Exception as e:
            logger.error(f"领取出错:{e}")
    async def get_captcha_result(self, task_id):
        json_data = {
            "clientKey": yes_captcha_key,
            "taskId": task_id
        }
        try:
            resp = await self.http.post(self.yescaptcha_url + '/getTaskResult', json=json_data)
            print(resp.json())
            return resp.json()
        except Exception as e:
            return {"errorId": 1, "errorDescription": "自定义错误：请求崩溃了"}


    async def get_2catpcha(self):

        json_data = {
            "clientKey": yes_captcha_key,
            "task": {
                "websiteURL": self.websiteURL,
                "websiteKey": self.websiteKey,
                "type": "TurnstileTaskProxyless",
                "isInvisible": False,
            },
            "softID": "72106"
        }
        resp = await self.http.post(self.yescaptcha_url + '/createTask', json=json_data)
        if "taskId" in resp.json():
            taskId = resp.json()["taskId"]
            while True:  # 重试两次
                try:
                    resp = await self.get_captcha_result(taskId)
                    if resp["errorId"] == 0:
                        if resp["status"] == "ready":
                            token = resp["solution"]["token"]
                            logger.info(f"识别成功:token={token}")
                            return token
                        elif resp["status"] == "processing":
                            print("识别中...请等待2s后查询识别结果")
                            await asyncio.sleep(2)
                    else:
                        print(f"识别失败：{resp['errorDescription']}")
                        return None
                except Exception as e:
                    logger.error(f"识别出错:{e}")
        else:
            print("taskId 不存在，识别请求发送有问题")
            return None

def load_wallets():
    try:
        # 获取当前目录
        if getattr(sys, 'frozen', False):
            # 如果是打包后的 EXE
            current_dir = os.path.dirname(sys.executable)
        else:
            # 如果是脚本
            current_dir = os.path.dirname(os.path.abspath(__file__))

        files_path = os.path.join(current_dir, "files")
        for filename in os.listdir(files_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(files_path, filename)

                lines = []
                # 读取文件并写入列表
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        # 去掉行末的换行符并分割
                        address, proxy = line.strip().split('---')
                        lines.append({'address': address, 'proxy': proxy})
                        print(f'Address: {address}, Proxy: {proxy}')
                # 打印结果
                return lines

    except Exception as e:
        print(f"erro: {e}")
        return None

def load_proxies():
    try:
        # 获取当前目录
        if getattr(sys, 'frozen', False):
            # 如果是打包后的 EXE
            current_dir = os.path.dirname(sys.executable)
        else:
            # 如果是脚本
            current_dir = os.path.dirname(os.path.abspath(__file__))

        files_path = os.path.join(current_dir, "files")
        for filename in os.listdir(files_path):
            if filename.endswith('proxies.txt'):
                file_path = os.path.join(files_path, filename)

                lines = []
                # 读取文件并写入列表
                with open(file_path, 'r', encoding='utf-8') as file:
                    lines = file.readlines()  # 读取每一行并保存到列表中
                # 去除每行末尾的换行符
                lines = [line.strip() for line in lines]
                # 打印结果
                print(lines)
                return lines

    except Exception as e:
        print(f"erro: {e}")
        return None

async def task_run(item):
    """任务"""
    try:
        address = item['address']
        proxy = item['proxy']
        iry = IrySwap(address,proxy)
        token = await iry.get_2catpcha()
        if token is None:
            logger.error("识别失败")
            return
        await asyncio.sleep(0.3)
        await iry.request_faucet(token)
    except Exception as e:
        logger.error(f"{e}")


async def limit_with_semaphore(item,semaphore):
    async with semaphore:
        await task_run(item)

async def main():
    str_input = input("请输入并发数量:")
    try:
        concurrency = int(str_input)
    except ValueError:
        logger.error("输入错误 默认启动1个线程")
        concurrency = 1
    semaphore = asyncio.Semaphore(concurrency)

    wallets = load_wallets()


    # 定义任务列表
    if wallets is None:
        logger.info("钱包数量为0")
        return
    tasks = [limit_with_semaphore(item, semaphore) for item in wallets]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
