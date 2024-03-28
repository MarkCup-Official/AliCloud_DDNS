import config,requests,time,logging
from datetime import datetime

from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

IPV4_RECORDIDS=[]
IPV6_RECORDIDS=[]
ipv4 = None
ipv6 = None

def MainLoop():
    ipv4 = None
    ipv6 = None

    for r in config.RECORDS_IPV4:
        id,value=GetDomainRecordID(r,config.DOMAIN)
        if id==None and config.CREATE:
            id=CreateDomainRecord(r,config.DOMAIN,"A","0.0.0.0",config.TTL)
            value="0.0.0.0"
        if id!=None:
            if value!="0.0.0.0":
                UpdateDomainRecord(id,r,"A","0.0.0.0",config.TTL)
            IPV4_RECORDIDS.append((id,r))
        else:
            print(f"警告: 解析记录{r}不存在, 已停止此解析记录的动态修改, 请手动创建或开启自动创建")
    for r in config.RECORDS_IPV6:
        id,value=GetDomainRecordID(r,config.DOMAIN)
        if id==None and config.CREATE:
            id=CreateDomainRecord(r,config.DOMAIN,"AAAA","::",config.TTL)
            value="::"
        if id!=None:
            if value!="::":
                UpdateDomainRecord(id,r,"AAAA","::",config.TTL)
            IPV6_RECORDIDS.append((id,r))
        else:
            print(f"警告: 解析记录{r}不存在, 已停止此解析记录的动态修改, 请手动创建或开启自动创建")

    print("开始动态解析修改:")
    while True:
        if len(IPV4_RECORDIDS)>0:
            ipv4_new = GetLocalIPV4()
            if ipv4_new!=ipv4:
                print(f"检测到ipv4变动:{ipv4_new}, 开始修改解析:")
                for id in IPV4_RECORDIDS:
                    UpdateDomainRecord(id[0],id[1],"A",ipv4_new,config.TTL)
                ipv4=ipv4_new
        if len(IPV6_RECORDIDS)>0:
            ipv6_new = GetLocalIPV6()
            if ipv6_new!=ipv6:
                print(f"检测到ipv6变动:{ipv6_new}, 开始修改解析:")
                for id in IPV6_RECORDIDS:
                    UpdateDomainRecord(id[0],id[1],"AAAA",ipv6_new,config.TTL)
                ipv6=ipv6_new
        
        time.sleep(config.FREQUENCY)

# 获取本机公网ip
def GetLocalIPV4():
    ipv4 = None
    try:
        # 获取公网IPv4地址
        response_ipv4 = requests.get(config.IPV4CHECK)
        if response_ipv4.status_code == 200:
            ipv4 = response_ipv4.json()['ip']
        else:
            print("Error getting IPv4:", response_ipv4.status_code)
    except Exception as e:
        print("Error:", e)
    
    return ipv4
def GetLocalIPV6():
    ipv6 = None
        
    try:
        # 获取公网IPv6地址
        response_ipv6 = requests.get(config.IPV6CHECK)
        if response_ipv6.status_code == 200:
            ipv6 = response_ipv6.json()['ip']
        else:
            print("Error getting IPv6:", response_ipv6.status_code)
    except Exception as e:
        print("Error:", e)
    
    return ipv6

# 创建连接
def CreateClient():
    conf = open_api_models.Config()
    conf.endpoint = config.ALI_DNS_API
    conf.access_key_id = config.ACCESS_KEY
    conf.access_key_secret=config.ACCESS_KEY_SECRET
    return Alidns20150109Client(conf)

# 获取解析记录ID
def GetDomainRecordID(record,domain):
    client=CreateClient()

    describe_domain_records_request = alidns_20150109_models.DescribeDomainRecordsRequest(
        domain_name=domain,
        key_word=record
    )
    runtime = util_models.RuntimeOptions()

    try:
        r=client.describe_domain_records_with_options(describe_domain_records_request, runtime)
        for r in r.body.domain_records.record:
            if r.rr==record:
                print(f"成功查询解析记录{record}的ID:"+r.record_id)
                return r.record_id,r.value

    except Exception as error:
        print("阿里云API错误:"+error.message)
        print(error.data.get("Recommend"))
        UtilClient.assert_as_string(error.message)
    return None,None

# 创建解析记录
def CreateDomainRecord(record,domain,type,value,ttl):
    client=CreateClient()

    describe_domain_records_request = alidns_20150109_models.AddDomainRecordRequest(
        domain_name=domain,
        rr=record,
        type=type,
        value=value,
        ttl=ttl
    )
    runtime = util_models.RuntimeOptions()

    try:
        r=client.add_domain_record_with_options(describe_domain_records_request, runtime)
        print(f"成功创建解析记录{record},解析记录ID:{r.body.record_id}")
        return r.body.record_id

    except Exception as error:
        print("阿里云API错误:"+error.message)
        print(error.data.get("Recommend"))
        UtilClient.assert_as_string(error.message)
    return None

# 更改解析记录
def UpdateDomainRecord(recordid,record,type,value,ttl):
    client=CreateClient()

    update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
        record_id=recordid,
        rr=record,
        type=type,
        value=value,
        ttl=ttl
    )
    runtime = util_models.RuntimeOptions()

    try:
        client.update_domain_record_with_options(update_domain_record_request, runtime)
        print(f"成功更改解析记录{record},type={type},value={value}")
        return True
    except Exception as error:
        print("阿里云API错误:"+error.message)
        print(error.data.get("Recommend"))
        UtilClient.assert_as_string(error.message)
    return False

if __name__=="__main__":
    logging.basicConfig(filename='log.log', level=logging.INFO)
    # 重定向print函数
    def print_to_log(*args, **kwargs):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = ' '.join(map(str, args))
        logging.info(f"[{current_time}] {message}", **kwargs)
    print = print_to_log
    MainLoop()
