# 2020/8/24
#Author: pengyonglin
#
import os
import requests
from bs4 import BeautifulSoup


class infohtml:
    def __init__(self, pid):
        self.id = pid.upper()
        self.url = 'http://www.rcsb.org/structure/'+pid.upper()
        self.__soup = self.cooker()

    def __str__(self):
        return '蛋白质PDB ID为：%s，网址是：%s' % (self.id, self.url)

    def cooker(self):
        try:
            r = requests.get(self.url, timeout=5)
            soup = BeautifulSoup(r.text, 'lxml')
            return soup
        except:
            print('连接异常！', self.id)
            return None

    def general_info(self):
        gen_info = {}
        soup = self.__soup
        if soup:
            e = soup.select('span#structureID')
            if e:
                gen_info['Entry'] = e[0].get_text()
            else:
                gen_info['Entry'] = ''
            t = soup.select('span#structureTitle')
            if t:
                gen_info['Title'] = t[0].get_text()
            else:
                gen_info['Title'] = ''
            c = soup.select('li#header_classification>strong>a')
            if c:
                gen_info['Classification'] = c[0].get_text()
            else:
                gen_info['Classification'] = ''
            # o = soup.select('li#header_organism>a')
            o = soup.select('li#header_organism')
            if o:  # 多个物种并存
                gen_info['Organism'] = o[0].get_text().split('&nbsp')[1]
            else:
                gen_info['Organism'] = ''
            m = soup.select('li#exp_header_0_method')
            if m:
                gen_info['Method'] = m[0].get_text().split('&nbsp')[1]
            else:
                gen_info['Method'] = ''
            r = soup.select('li#header_deposited-released-dates')
            if r:
                gen_info['Released'] = r[0].get_text().split('&nbsp')[3]
            else:
                gen_info['Released'] = ''
            if gen_info['Method'] == 'X-RAY DIFFRACTION':
                gen_info['Resolution'] = soup.select('li#exp_header_0_diffraction_resolution')[
                    0].get_text().split('&nbsp')[1]
            else:
                gen_info['Resolution'] = soup.select('li#exp_header_0_em_resolution')[
                    0].get_text().split('&nbsp')[1]
        return gen_info

    def literature_info(self):
        lit_info = {}
        soup = self.__soup
        if soup:
            # lit_info['Citation'] = soup.select(
            #     'div#primarycitation > h4')[0].get_text()
            p = soup.select('li#pubmedLinks>a')
            if p:
                lit_info['PubMed'] = p[0].get_text()
            else:
                lit_info['PubMed'] = ''
            d = soup.select('li#pubmedDOI>a')
            if d:
                lit_info['DOI'] = d[0].get_text()
            else:
                lit_info['DOI'] = ''
        return lit_info

    def macromolecules_info(self):
        # 多个Entity（聚合物）
        mac_info = {}
        molecule = []
        chains = []
        organism_sep = []
        gene = []
        uniport = []
        soup = self.__soup
        if soup:
            # entities = soup.findall(
            #     'table', attrs={'class': 'table table-bordered table-condensed tableEntity'})
            entities = soup.select(
                'table[class="table table-bordered table-condensed tableEntity"]')
            entity_start = entities[0].select('tr[class="info"]')[
                0].get_text().strip()
            entity_start = int(entity_start[-1])  # entity起始数不一定是1
            for s in range(len(entities)):
                td = entities[s].select(
                    'tr#macromolecule-entityId-'+str(s+entity_start)+'-rowDescription>td')  #
                if td:
                    molecule.append(td[0].get_text())
                    chains.append(td[1].get_text())
                    organism_sep.append(td[3].get_text().replace('&nbsp', ''))
                else:
                    molecule.append('')
                    chains.append('')
                    organism_sep.append('')
                # g = entities[s].select(
                #     'tr#macromolecule-entityId-'+str(s+1)+'-rowDescription>td>a')  ##
                g = entities[s].select('td[style="word-break: break-all;"]>a')
                if g:
                    # gene.append(g[0].get_text())  #entity包含两个或多个基因
                    gene.append(','.join([i.get_text() for i in g[0:-1]]))
                else:
                    gene.append('')
                u = entities[s].select(
                    'span[class="label label-rcsb"]')
                if u:
                    uniport.append(u[0].get_text())
                else:
                    uniport.append('')
        mac_info['Molecule'] = ';'.join(molecule)
        mac_info['Chains'] = ';'.join(chains)
        mac_info['Organism_sep'] = ';'.join(organism_sep)
        mac_info['Gene'] = ';'.join(gene)
        mac_info['Uniport'] = ';'.join(uniport)
        return mac_info

    def smolecule_info(self):
        pass


def downloader(pid, topath):
    url_root = 'https://files.rcsb.org/download/'  #PDB数据库网址，下载结构文件
    filename = pid+'.pdb'
    url_get = url_root+filename
    topath = os.path.join(topath, filename)
    try:
        r = requests.get(url_get, stream=True)
        content_size = int(r.headers['content-length'])
        print('正在下载：', pid, content_size)
        with open(topath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=512):
                f.write(chunk)
    except:
        print(pid, '下载失败！')
