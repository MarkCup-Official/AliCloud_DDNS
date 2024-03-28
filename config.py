# 必须修改的设置

ACCESS_KEY=""                   # 你的账户的 Access Key, 可在RAM访问控制中获取
ACCESS_KEY_SECRET=""            # Access Key 的密钥

DOMAIN="example.com"            # 目标域名地址(必须使用阿里云DNS)
RECORDS_IPV4=["www","@"]        # 目标解析记录, 如果要解析@.exmaple.com，主机记录要填写”@”，而不是空
RECORDS_IPV6=[]

# 可选修改的设置

ALI_DNS_API="alidns.cn-hangzhou.aliyuncs.com"   # 阿里云dns的api地址, 可以修改为你服务器地区的地址加速访问

CREATE=True # 如果记录不存在, 则自动创建

# 修改以下地址需要确保返回的值是json, 程序会读取josn中第一个"ip"键, 位于'start.py'第67和81行
IPV4CHECK="https://api.ipify.org?format=json"  # 检测本地公网ipv4的地址
IPV6CHECK="https://api6.ipify.org?format=json" # 检测本地公网ipv6的地址

TTL=600     # 设置解析生效时间

FREQUENCY=60 # ip检测频率, 单位s