# irys领水

##### 需要yescaptcha  注册地址： https://yescaptcha.com/i/4UcvE0
![image](https://github.com/user-attachments/assets/033043af-4481-4d6a-aa34-1faf65844c90)



1、克隆/下载仓库

```
git clone https://github.com/YueCobra/irys.git
#进入目录
cd irys
```

2、配置虚拟环境(可选)

```
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3、安装依赖

```
pip install -r requirements.txt
```

4、启动项目

```
#复制如图所示密钥配置在 .env文件中的  YESCAPTCHA_KEY='' 字段
#address.txt 配置规则：address---proxy  注：不配代理会领水出错
#运行项目 
python main.py
```
