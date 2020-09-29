# 2020/9/17
#Author: pengyonglin
#
import os
import sys
import time
import csv
import multiprocessing as mp

from ini import OB_ROOT

OBMI = os.path.join(OB_ROOT, 'obminimize')
OBPR = os.path.join(OB_ROOT, 'obprop')


def optimizeMole(molefile, topath='ligand_pdb'):
    # OpenBabel 3.1.1 --obminimize
    # command: obminimize -ff MMFF94 ligand.pdb > ligand.pdb
    # -ff 力场
    name = os.path.basename(molefile).split('.')[0]
    optifile = name+'.pdb'
    poptfile = os.path.join(topath, optifile)
    print('### Optimizing ligand:', name)
    cmd = r'%s -ff MMFF94 %s > %s' % (
        OBMI, molefile, poptfile)    # ???? 优化力场和局部场电位
    os.system(cmd)


def calculateProp(molefile, topath='ligand_prop'):
    # OpenBabel 3.1.1 --obprop
    # command: obprop mole.pdb
    name = os.path.basename(molefile).split('.')[0]
    propfile = name+'_prop.txt'
    ppropfile = os.path.join(topath, propfile)
    cmd = r'%s %s > %s' % (OBPR, molefile, ppropfile)
    print(cmd)
    os.system(cmd)


def extract_prop(file):
    # prop={}
    with open(file, 'r') as f:
        tex = f.readlines()
    ltex = tex[0:-1]
    dtex = {i.split()[0]: i.strip().split()[1] for i in ltex if i.strip()}
    return dtex


if __name__ == '__main__':
    # 进入ligand目录
    path_ligand = os.getcwd()
    path_ligand_raw = os.path.join(path_ligand, 'ligand_raw')
    path_ligand_pdb = os.path.join(path_ligand, 'ligand_pdb')
    path_ligand_prop = os.path.join(path_ligand, 'ligand_prop')
    # # 优化小分子
    ligand_raw = [i for i in os.listdir(path_ligand_raw) if i.endswith('.pdb')]
    # for m in ligand_raw:
    #     pm = os.path.join('ligand_raw', m)
    #     optimizeMole(pm)
    # 计算小分子属性
    pool = mp.Pool()
    for m in ligand_raw:
        pm = os.path.join('ligand_raw', m)
        pool.apply_async(calculateProp, args=(pm,))
    pool.close()
    pool.join()
    # 整合
    lprop = []
    path_prop = os.path.join(path_ligand_prop, 'props_of_ligands.csv')
    props = [f for f in os.listdir(
        path_ligand_prop) if f.endswith('_prop.txt')]
    for i in props:
        fp = os.path.join(path_ligand_prop, i)
        lprop.append(extract_prop(fp))
    with open(path_prop, 'w', newline="") as f:
        fileheader = ['name', 'formula', 'mol_weight', 'exact_mass', 'canonical_SMILES',
                      'InChI', 'num_atoms', 'num_bonds', 'num_residues', 'num_rotors', 'sequence',
                      'num_rings', 'logP', 'PSA', 'MR']
        dict_writer = csv.DictWriter(f, fileheader)
        dict_writer.writeheader()
        dict_writer.writerows(lprop)
    print('处理小分子结构完成！')
