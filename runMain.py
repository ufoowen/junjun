from data.getData import GetValues
from core.runRequests import RunRequests
from core.common import Common  
from log.logger import RecordLogging
from data.dependData import DependData 
from emailout.send_email import SendEmail
from core.saveCookie import SaveCookies 
from data.getConfigdata import GetConfigValue
from core.readJson import ReadJson
import os,time,json
BASE=os.path.dirname(__file__)
cookiepath=os.path.join(BASE,'dataconfig\\cookies.json')
runtimefile = os.path.join(BASE,'emailout\\report.json')
class RunMain(object):
    '''执行主流程类'''
    def __init__(self):
        self.get_value=GetValues()
        self.run_req=RunRequests() 
        self.comm=Common()
        self.logs=RecordLogging() 
        self.send_mail=SendEmail() 
        self.conf=GetConfigValue()
    #执行入口
    def runMain(self):
        start_time = time.time() 
        response=None
        pass_count=[] #统计case通过数量
        fail_count=[]  #统计case失败数量
        no_run_count=[] #统计case未执行数量
        case_lines=self.get_value.get_case_rows() 
        for i in range(1,case_lines): 
            isrun = self.get_value.get_excel_isexecute(i) 
            if isrun:
                url=self.get_value.get_excel_url(i) 
                isheader=self.get_value.get_excel_isheader(i) 
                request_type=self.get_value.get_request_type(i) 
                request_data=self.get_value.get_xlsid_go_json(i) 
                exp_result=self.get_value.get_exp_result(i) #
                # exp_result=self.get_value.get_expect_data_for_mysql(i) #t通过sql去数据库获取预期结果
                depend_case_id=self.get_value.isdepend_case_id(i) #获取是否有依赖case_id
                if depend_case_id!=None: 
                    self.depend_data=DependData(depend_case_id) 
                    #获取依赖的响应数据
                    depend_response_data=self.depend_data.get_data_for_key(i)
                    #获取数据依赖字段
                    depend_field=self.get_value.get_data_depend_field(i)
                    request_data[depend_field]=depend_response_data
                if isheader=="YES": 
                    header=self.conf.get_item_value('header')#获取配置文件的header
                    response = self.run_req.run_request(url, request_data, request_type,header) 
                elif isheader=="write":
                    response = self.run_req.run_request(url, request_data, request_type)
                    cook=SaveCookies(i)
                    cook.write_cookie() #将cookie写入json文件
                elif isheader=="cookie":
                    json_da=ReadJson(cookiepath)
                    cookie=json_da.get_json_data() 
                    response= self.run_req.run_request(url, request_data, request_type,cookie)
                else:
                    response = self.run_req.run_request(url, request_data, request_type)
                if self.comm.isinclude(exp_result,response):
                    self.get_value.get_write_data(i,"测试通过")
                    pass_count.append(i) #把通过case加入列表
                else:
                    self.get_value.get_write_data(i,"测试失败")
                    self.logs.logger.error("第%s条case预期结果与实际结果不一致!"%i)
                    fail_count.append(i)  ##把失败case加入列表
                    self.get_value.write_reality_result(i,response) 
            else:
                # self.logs.logger.info("第%s条case未执行!"%i)
                no_run_count.append(i)
        end_start = time.time()  # 程序结束时间
        runtime = "%ds" % (end_start - start_time) 
        data = open(runtimefile,'r',encoding='utf-8') #写入到json
        dat = json.loads(data.read())
        dat["runtime"] = runtime
        data.close()
        with open(runtimefile,"w",encoding='utf-8') as f:
            dats=json.dumps(dat,indent=2,ensure_ascii=False)
            f.write(dats)

        self.send_mail.send_email_Main(pass_count,fail_count,no_run_count) 


if __name__=="__main__":
    run=RunMain()
    result=run.runMain()

