# 2020/8/18
#Author: pengyonglin
#
import os
import time
from selenium import webdriver
import requests
import re


def pocasaPocket(pdbfile, presult):
    # POCASA 预测蛋白质结合口袋
    url_pocasa = 'http://g6altair.sci.hokudai.ac.jp/g6/service/pocasa'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # 静默模式
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url_pocasa)
    # html=driver.page_source ##源代码
    # url=driver.current_url ##url
    time.sleep(2)
    # 提交表单
    ele_file = driver.find_element_by_id('pdbfilename')
    ele_file.clear()
    ele_file.send_keys(pdbfile)
    ele_sub = driver.find_element_by_xpath(
        '/html/body/form/div[@style="text-align:center"]/input[@type="submit"]')
    ele_sub.click()
    time.sleep(10)
    html = driver.page_source
    hrefs = re.findall(r'href="(.*?)">', html)
    url_center = url_pocasa+hrefs[3][1:]
    fp_center = os.path.join(presult, hrefs[3].split('/')[-1])
    url_topn = url_pocasa+hrefs[4][1:]
    fp_topn = os.path.join(presult, hrefs[4].split('/')[-1])
    r = requests.get(url_center, stream=True)
    with open(fp_center, 'wb') as f:
        for chunk in r.iter_content(chunk_size=512):
            f.write(chunk)
    r = requests.get(url_topn, stream=True)
    with open(fp_topn, 'wb') as f:
        for chunk in r.iter_content(chunk_size=512):
            f.write(chunk)
    time.sleep(3)
    driver.close()


def writeConf(pocfile):
    with open(pocfile) as f:
        centers = f.readlines()
    centers_ = [i.split()[6:9] for i in centers]
    protein = os.path.basename(pocfile).replace('_Pocket_DepthCenters.pdb', '')
    #print(protein, '有', len(centers), '个口袋')
    # receptor = 'receptor = '+protein+'.pdbqt'
    size_x = 'size_x = 30'
    size_y = 'size_y = 30'
    size_z = 'size_z = 30'
    # 选择第一个口袋
    center_x = 'center_x = '+centers_[0][0]
    center_y = 'center_y = '+centers_[0][1]
    center_z = 'center_z = '+centers_[0][2]
    # out=
    # log=
    exhaustiveness = 'exhaustiveness = 16'
    # cpu = 'cpu = 48'
    conf = [center_x, center_y, center_z,
            ' ', size_x, size_y, size_z, ' ', exhaustiveness]
    conf_ = [i+'\n' for i in conf]
    conffile = protein+'.conf'
    conffile_ = os.path.join(os.path.split(pocfile)[0], conffile)
    with open(conffile_, 'w') as f:
        f.writelines(conf_)
