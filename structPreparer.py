# 2020/8/18
#Author: pengyonglin
#
import os
import sys

import multiprocessing as mp
from threading import Timer
import eventlet
from optparse import OptionParser

from ini import MGL_ROOT

usage = 'usage: %prog [options] -h<--help> -s<--structure>'
optParser = OptionParser(usage=usage)
optParser.add_option('-s', '--structure', action='store', type='string', dest='STRUCT',
                     help='待处理的结构（protein/molecule）')
(options, args) = optParser.parse_args()
target = options.STRUCT
ADT_ROOT = MGL_ROOT+r'\Lib\site-packages\AutoDockTools'

def timeLimit(interval):
    def wraps(func):
        def time_out():
            raise RuntimeError()

        def deco(*args, **kwargs):
            timer = Timer(interval, time_out)
            timer.start()
            res = func(*args, **kwargs)
            timer.cancel()
            return res
        return deco
    return wraps


def prepareReceptor(receptorfile, frompath='protein_pdb', topath='protein_pdbqt'):
    # AutoDockTools 1.5.4, MGLtools 1.5.6
    # (win)command: %MGL_ROOT%\python %MGL_ROOT%\Lib\site-packages\AutoDockTools\Utilities24\prepare_receptor4.py
    #               -r receptor.pdb -o receptor.pdbqt -A 'bonds_hydrogens'
    name = receptorfile.split('.')[0]
    pdbqtfile = name+'.pdbqt'
    print('准备蛋白：', name)
    cmd = r"%s\python %s\Utilities24\prepare_receptor4.py -r %s\%s -o %s\%s -A 'bonds_hydrogens'" % (
        MGL_ROOT, ADT_ROOT, frompath, receptorfile, topath, pdbqtfile)
    os.system(cmd)


# @time_limit(15)
def prepareLigand(ligandfile, frompath='ligand_pdb', topath='ligand_pdbqt'):
    # AutoDockTools 1.5.4, MGLtools 1.5.6
    # (win)command: %MGL_ROOT%\python %MGL_ROOT%\Lib\site-packages\AutoDockTools\Utilities24\prepare_ligand4.py
    #               -l ligand.pdb -o ligand.pdbqt -A 'hydrogens_bonds' -F
    # -l 配体文件
    # -o 输出文件
    # -A 加氢和键
    # -C 不加局部场电位
    # -F 选取最大片段
    name = ligandfile.split('.')[0]
    pdbqtfile = name+'.pdbqt'
    print('准备配体：', name)
    cmd = r"%s\python %s\Utilities24\prepare_ligand4.py -l %s\%s -o %s\%s -A 'hydrogens_bonds' -F" % (
        MGL_ROOT, ADT_ROOT, frompath, ligandfile, topath, pdbqtfile)
    os.system(cmd)
    # eventlet.monkey_patch()
    # with eventlet.Timeout(10, True):  # 限制函数运行时长
    #     os.system(cmd)


if __name__ == '__main__':
    path_root = os.getcwd()
    path_protein = os.path.join(path_root, 'protein_pdb')
    path_ligand = os.path.join(path_root, 'ligand_pdb')
    path_protein_pdbqt = os.path.join(path_root, 'protein_pdbqt')
    path_ligand_pdbqt = os.path.join(path_root, 'ligand_pdbqt')
    # 准备受体
    if target == 'protein':
        print('正在准备蛋白质结构...')
        proteins = [i for i in os.listdir(
            path_protein) if i.endswith('.pdb')]
        pool = mp.Pool()
        for pro in proteins:
            pool.apply_async(prepareReceptor, args=(pro,))
        pool.close()
        pool.join()
        print('蛋白质结构准备完成!')
    elif target == 'molecule':
        # 准备配体
        print('正在准备配体结构...')
        ligands = [i for i in os.listdir(path_ligand) if i.endswith('.pdb')]
        pool = mp.Pool()
        for lig in ligands:
            pool.apply_async(prepareLigand, args=(lig,))
        pool.close()
        pool.join()
        print('配体结构准备完成!')
    else:
        print('请输入正确参数（protein/structure）!')
        sys.exit(1)
