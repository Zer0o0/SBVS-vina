# 2020/8/24
#Author: pengyonglin
#

import os
import sys
import shutil

import csv
import pandas as pd
import multiprocessing as mp

import pdbInfo
from pdbInfo import downloader
import pdbContainer
from pdbContainer import pdbParser
import confWriter

from optparse import OptionParser

# 参数设置
usage = 'usage: %prog [options] -h<--help> -p<--pdbid> -o<--organism>'
optParser = OptionParser(usage=usage)
optParser.add_option('-p', '--pdbid', action='store', type='string', dest='PDBID',
                     help='待处理的蛋白的PDB ID文件，例如 "pdbids.txt"，一行一个ID')
optParser.add_option('-o', '--organism', action='store', type='string', dest='ORGANISM',
                     help='蛋白对应的物种，例如 "Homo sapiens"，仅支持PDB数据库中的物种，注意使用双引号')
(options, args) = optParser.parse_args()

pdbid = options.PDBID
organism = options.ORGANISM


if __name__ == '__main__':
    #进入protein目录
    path_protein = os.getcwd()
    path_protein_raw = os.path.join(path_protein, 'protein_raw')
    path_protein_clean = os.path.join(path_protein, 'protein_clean')
    path_protein_pdb = os.path.join(path_protein, 'protein_pdb')
    path_pocasa = os.path.join(path_protein, 'pocasa')
    info_file = os.path.join(
        path_protein, 'informations_of_pdb_items.csv')  # 保存蛋白信息
    info_file_keep = os.path.join(
        path_protein, 'informations_of_pdb_items_keep.csv')  # 保存过滤后的蛋白信息
    log_file_pocasa = os.path.join(path_pocasa, 'pocasa.log')
    log_file_info = os.path.join(path_protein, 'protein.log')
    # 获取蛋白信息（PDB）
    try:
        with open(pdbid, 'r') as f:
            pdbIDs = [i.strip() for i in f.readlines()]
    except:
        print('沒有找到PDB ID文件，检查是否存在或路径是否正确！')
    info_all = []
    for pid in pdbIDs:
        try:
            print('获取蛋白信息：', pid)
            protein = pdbInfo.infohtml(pid)
            info = {}
            general = protein.general_info()
            molecule = protein.macromolecules_info()
            literature = protein.literature_info()
            info.update(general)
            info.update(molecule)
            info.update(literature)
            info_all.append(info)
        except:
            with open(log_file_info, 'a') as f:
                f.write(pid+' 信息异常\n')
    with open(info_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Entry', 'Title', 'Classification', 'Organism', 'Method', 'Released', 'Resolution',
                      'Molecule', 'Chains', 'Organism_sep', 'Gene', 'Uniport', 'PubMed', 'DOI']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(info_all)
    print('获取蛋白质信息完成，正在下载蛋白质...')
    # 过滤蛋白信息，保留要下载的PDB ID
    # 同名的molecule保留一个（分辨率最高）
    info = pd.read_csv(info_file)
    info['Molecule2'] = info['Molecule'].str.lower()
    info_group = info.groupby('Molecule2')
    pdb_keep = []
    for k, v in info_group.groups.items():
        g = info.iloc[v, ].sort_values(by='Resolution')
        t = g.iloc[0, ]
        pdb_keep.append(t)
    pdb_keep_df = pd.concat(pdb_keep, axis=1).T
    pdb_keep_df.to_csv(info_file_keep, index=False)
    # 下载结构文件
    info_keep = pd.read_csv(info_file_keep)
    pdbIDs = list(info_keep['Entry'])
    pool = mp.Pool()
    for i in pdbIDs:
        pool.apply_async(downloader, args=(i,), kwds={
                         'topath': path_protein_raw})
    pool.close()
    pool.join()
    print('下载蛋白质结构信息完成，正在清洗结构...')
    # 清洗结构,保留PDB信息里的链ID
    #info_keep = pd.read_csv(info_file_keep)
    #pdbIDs = list(info_keep['Entry'])
    chainIDs = list(info_keep['Chains'])
    chainOrganism = list(info_keep['Organism_sep'])
    for i in range(len(pdbIDs)):
        ifn = pdbIDs[i]+'.pdb'
        pifn = os.path.join(path_protein_raw, ifn)
        with open(pifn, 'r') as f:
            pro = pdbParser(f)
        chas = chainIDs[i].split(';')
        chas_ = [''.join(i.split(', ')) for i in chas]
        org = chainOrganism[i].split(';')
        if organism:  # 指定物种
            for j in range(len(chas_)):
                if organism in org[j]:  # 仅提取指定物种的蛋白链
                    ofn = pdbIDs[i]+'-'+chas_[j]+'.pdb'
                    pofn = os.path.join(path_protein_clean, ofn)
                    with open(pofn, 'w') as f:
                        pro.writer(f, chas_[j])
        else:
            for j in range(len(chas_)):
                ofn = pdbIDs[i]+'-'+chas_[j]+'.pdb'
                pofn = os.path.join(path_protein_clean, ofn)
                with open(pofn, 'w') as f:
                    pro.writer(f, chas_[j])
    # 同聚物结构分离
    for i in os.listdir(path_protein_clean):
        pid = i.split('.')[0].split('-')[0]
        cha = i.split('.')[0].split('-')[1]
        # print(pid,cha)
        chas = list(cha)
        pifn = os.path.join(path_protein_clean, i)
        if len(chas) > 1:
            ofn = pid+'-'+chas[0]+'.pdb'
            pofn = os.path.join(path_protein_clean, ofn)
            with open(pifn, 'r') as f:
                pro = pdbParser(f)
            with open(pofn, 'w') as f:
                pro.writer(f, chas[0])
        else:
            pass
    # 迁移清理好的文件
    for i in os.listdir(path_protein_clean):
        if len(i) == 10:
            fromfile = os.path.join(path_protein_clean, i)
            tofile = os.path.join(path_protein_pdb, i)
            shutil.copyfile(fromfile, tofile)
    print('清洗蛋白结构完成，正在获取对接口袋信息...')
    # 蛋白质口袋预测和对接配置文件准备
    for i in os.listdir(path_protein_pdb):
        p = os.path.join(path_protein_pdb, i)
        try:
            print('获取口袋信息：', i[:4])
            confWriter.pocasaPocket(p, path_pocasa)
        except:
            with open(log_file_pocasa, 'a') as f:
                f.write(p+' 异常\n')
    pocfiles = [i for i in os.listdir(
        path_pocasa) if 'Pocket_DepthCenters' in i]
    for i in pocfiles:
        p = os.path.join(path_pocasa, i)
        confWriter.writeConf(p)
    print('蛋白质结构处理完成！')
