# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import JavascriptException
from datetime import datetime
import requests
import time
import json


# API节点地址
WebApiUrl = 'http://10.211.55.9:53981'
# AccessKey ID
AccessID = 'k1ySpOeOAcQV8vNG'
# AccessKey密钥
AccessKey = 'q573ukqK0BPLY1SJjo58PQG00KFNg2HY'
# 集群ID
nodeClusterId = 1
# Telegram 机器人Token
telegram_token = "6040181193:AAEOK_BUTmFTm8cgEg9GyMtEWo1lt837KIw"
# Telegram 群ID（如检测到IP异常则通知）
telegram_group = "-4985059900"


site_url = []
post_data = {"type": "admin", "accessKeyId": AccessID, "accessKey": AccessKey}
response = requests.post('{}/APIAccessTokenService/getAPIAccessToken'.format(WebApiUrl), data=json.dumps(post_data))
r = response.json()
token = r['data']['token']
if not token:
    print('获取Token失效')
    exit()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'X-Edge-Access-Token': token
}
r = requests.post('{}/NodeService/findAllEnabledNodesDNSWithNodeClusterId'.format(WebApiUrl), data=json.dumps({"nodeClusterId": nodeClusterId, "isInstalled": True}), headers=headers)
data = r.json()
if data['code'] == 200:
    cdn_ips = data['data']['nodes']
    for cdn in cdn_ips:
        site_url.append({
            'name': cdn['name'],
            'ip': cdn['ipAddr'],
            'id': cdn['id']
        })
else:
    print('集群ID不正确:{}'.format(data['message']))

print(f'————>本次检测共：{len(site_url)}个IP')
print('——————————————————————————')

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(300, 300)
driver.get("https://www.itdog.cn/http/")

block_ip_list = []
def process_url(domain, index, allNum):
    timestamp = datetime.timestamp(datetime.now())
    link = f'http://{domain["ip"]}?t={int(timestamp)}'
    form_script = '''
        //在输入框输入域名
        var inputElement = document.getElementById('host');
        inputElement.value = arguments[0];
        //点击测试按钮
        check_form('fast')
	'''
    driver.execute_script(form_script, link)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
    progress_script = '''
        var url = arguments[0];
        var num = 0;
        var progressTime;
        clearInterval(progressTime);
        let checkPcoded = () => {
            if(document.querySelector('#host')){
                //$('.gg_link').remove();
                //document.querySelector('.pcoded-header').style = 'display:none';
                //document.querySelector('.pcoded-navbar').style = 'display:none';
                //document.querySelector('.page-header').style = 'display:none';
                //document.querySelector('.footer').style = 'display:none';
                //document.documentElement.style.marginLeft = (1000 - 1300) / 2 + 'px';
                progressTime = setInterval(function(){
                    testProgress()
                }, 2000)
            }else{
                checkPcoded();
            }
        }
        checkPcoded();

        function testProgress(){
            num++;
            var autoText = document.createElement('div');
            var number = document.querySelectorAll('.progress-bar')[0].textContent;
            autoText.textContent = '当前进度：' + number;
            autoText.style.position = 'fixed';
            autoText.style.top = '0';
            autoText.style.left = '0';
            autoText.style.zIndex = '999999';
            autoText.style.width = '100%';
            autoText.style.height = '4rem';
            autoText.style.border = 'none';
            autoText.style.fontSize = '1.3rem';
            autoText.style.color = '#fff';
            autoText.style.textAlign = 'center';
            autoText.style.lineHeight = '4rem';
            autoText.style.backgroundColor = '#ff5252';
		    document.body.appendChild(autoText);
            if(num>=60){
                clearInterval(progressTime);
                window.py_confirm_button_click = 'no';
            }
            if(number=='100%'){
                clearInterval(progressTime);
                //访问失败数量
                //var errNum = document.querySelectorAll('.time_out.badge.badge-danger.small')[0].textContent;
                var errNum = 0;
                //获取访问失败IP
                var nodeTrList = document.getElementById('simpletable').getElementsByClassName('node_tr');
                var ip_list = [];
                var diq_list = [];
                for (var i = 0; i < nodeTrList.length; i++) {
                    var nodeTr = nodeTrList[i];
                    if(nodeTr.getAttribute('time_out') && nodeTr.getAttribute('node_type')!='5'){
                        errNum++;
                        let diqu = nodeTr.querySelector('td.text-left').textContent.trim().split('\t\t\t\t\t\t\t\t\t\t')[1];
                        let diip = nodeTr.querySelector('td.real_ip div').textContent.trim();
                        ip_list.push(diip);
                        diq_list.push(`${diqu}:${diip}`);
                    }
                }
                var objiect = {
                    diq: diq_list,
                    ips: ip_list,
                    err: Number(errNum)
                }
                window.py_confirm_button_click = objiect;
            }
        }
	'''
    driver.execute_script(progress_script, link)
    confirm_button_click_value = None
    while not confirm_button_click_value:
        try:
            time.sleep(1)
            confirm_button_click_value = driver.execute_script("return window.py_confirm_button_click;")
            if confirm_button_click_value and confirm_button_click_value!='no':
                data = confirm_button_click_value
                print(f'🚫{data["err"]}节点({allNum}/{index}):{domain["ip"]}')
                print(str(','.join(data["diq"])))
                print('————————————————————————————————————')
                if data["err"] >= 10:
                    block_ip_list.append({
                        'id': domain['id'],
                        'ip': domain["ip"],
                        'err': data["err"],
                        'name': domain["name"]
                    })

            elif confirm_button_click_value == 'no':
                driver.refresh()
                process_url(domain['ip'], index, allNum)
        except:
            pass

def testIpList(list):
    for index, domain in enumerate(list):
        try:
            process_url(domain, index, len(list))
        except JavascriptException:
            print("JavaScript执行错误")
            break

testIpList(site_url)
driver.quit()

if block_ip_list:
    print('——————————————————————————')
    print(f'共{len(block_ip_list)}个被墙IP')
    print('——————————————————————————')
    today = datetime.now()
    message_text = 'CDN-IP自检:' + today.strftime('%Y-%m-%d %H:%M') + '\n'
    edit_ips = []
    for text in block_ip_list:
        edit_ips.append({
            "id": text["id"],
	        "enable": 0
        })
        message_text += f'【🚫{text["err"]}节点】{text["name"]}: {text["ip"]}\n'

    print(edit_ips)
    print(message_text)
    telegram_url = "https://api.telegram.org/bot{}/sendMessage".format(telegram_token)
    payload = {
        "chat_id": telegram_group,
        "text": message_text
    }
    requests.post(telegram_url, data=payload)