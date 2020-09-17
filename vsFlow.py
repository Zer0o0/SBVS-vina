# 2020/8/18
#Author: pengyonglin
#

import os
import sys
import time
#from ini import VINA_ROOT


def runVina(receptorfile, ligandfile, conffile, topath='result_vina'):
    # AutoDock Vina 1.1.2
    # command: vina --config config.txt --ligand ligand.pdbqt --log log.txt
    name_receptor = receptorfile.split('/')[1].split('.')[0]
    name_ligand = ligandfile.split('/')[1].split('.')[0]
    outfile = name_receptor+'_'+name_ligand+'_out'+'.pdbqt'
    logfile = name_receptor+'_'+name_ligand+'.log'
    print('正在对接：', name_receptor, '和', name_ligand)
    cmd = r'vina --receptor %s --ligand %s --config %s --out %s/%s --log %s/%s' % (
        receptorfile, ligandfile, conffile, topath, outfile, topath, logfile)
    # print(cmd)
    os.system(cmd)


def getResult(path_result_vina, path_score):
    file_names = [f for f in os.listdir(
        path_result_vina) if f.endswith('.pdbqt')]
    everything = []
    failures = []
    print('Found', len(file_names), 'pdbqt files')
    for file_name in file_names:
        path_file_name = os.path.join(path_result_vina, file_name)
        file = open(path_file_name)
        lines = file.readlines()
        file.close()
        try:
            line = lines[1]
            result = float(line.split(':')[1].split()[0])
            everything.append([file_name.split('_out')[0], result])
        except:
            failures.append(file_name)
    everything.sort(key=lambda x: x[0])
    tqln = '{:<8}{:<12}{:>10}\n'
    with open(path_score, 'w') as f:
        f.write(tqln.format('protein', 'ligand', 'affinity'))
        for i in everything:
            f.write(tqln.format(i[0].split('_')[0], i[0].split('_')[1], i[1]))
        if failures:
            f.write('# wrong items\n')
            f.writelines(failures)


if __name__ == '__main__':
    path_root = os.getcwd()
    path_protein_pdbqt = os.path.join(path_root, 'protein_pdbqt')
    path_ligand_pdbqt = os.path.join(path_root, 'ligand_pdbqt')
    path_conf = os.path.join(path_root, 'confs')
    # 输出文件
    path_result_vina = os.path.join(path_root, 'result_vina')
    path_score = os.path.join(path_root, 'result_score.txt')
    path_log = os.path.join(path_root, 'vina.log')
    os.mkdir(path_result_vina)
    # vina对接
    print('正在运行对接分析...')
    time_start = time.time()
    prepreceptors = [i for i in os.listdir(
        path_protein_pdbqt) if i.endswith('.pdbqt')]
    prepligands = [i for i in os.listdir(
        path_ligand_pdbqt) if i.endswith('.pdbqt')]
    for rec in prepreceptors:
        receptorfile = 'protein_pdbqt/'+rec
        conffile = 'confs/'+rec.split('.')[0]+'.conf'
        for lig in prepligands:
            ligandfile = 'ligand_pdbqt/'+lig
            try:
                runVina(receptorfile, ligandfile, conffile)
            except:
                with open(path_log, 'a') as f:
                    f.write(receptorfile+ligandfile+' 异常'+'\n')
    # 提取结果
    getResult(path_result_vina, path_score)
    time_end = time.time()
    with open(path_log, 'a') as f:
        f.write('耗时:'+str((time_end-time_start)//60))
    print('对接分析完成！')
