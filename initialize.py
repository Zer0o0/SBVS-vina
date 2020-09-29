# 2020/9/16
#Author: pengyonglin
#
'''
********** 初始化对接工作目录 **********
目录设置：
protein/
    protein_raw         #PDB 数据库获取的原始结构文件，pdb格式
    protein_clean       #原始结构去除配体分子，水分子后保留的蛋白质结构文件（包含多聚体，不同物种的结构），pdb格式
    protein_pdb         #清洗完毕的蛋白质结构文件，pdb格式
    pocasa              #POCASA预测的蛋白质与配体结合口袋信息
ligand/
    ligand_raw          #配体小分子文件，pdb格式
    ligand_pdb          #处理好的配体小分子（如能量最小化），pdb格式
    ligand_prop         #配体小分子的性质
screen/
    protein_pdb         #清洗完毕的蛋白质结构文件，pdb格式
    ligand_pdb          #处理好的配体小分子，pdb格式
    protein_pdbqt       #准备好用于对接的蛋白质结构，pdbqt格式
    ligand_pdbqt        #准备好用于对接的配体分子，pdbqt格式
    confs               #vina对接使用的configure文件，与蛋白质一一对应
---
使用方法：
在工作目录（空目录）下运行 python initialize.py
'''
import os

print(__doc__)


if __name__ == '__main__':
    path_root = os.getcwd()
    dir_ini = ['protein', os.path.join('protein', 'protein_raw'), os.path.join('protein', 'protein_clean'), os.path.join('protein', 'protein_pdb'), os.path.join('protein', 'pocasa'),
               'screen', os.path.join('screen', 'protein_pdb'), os.path.join('screen', 'ligand_pdb'), os.path.join(
                   'screen', 'protein_pdbqt'), os.path.join('screen', 'ligand_pdbqt'), os.path.join('screen', 'confs'),
               'ligand', os.path.join('ligand', 'ligand_raw'), os.path.join('ligand', 'ligand_pdb'), os.path.join('ligand', 'ligand_prop')]
    dir_ini = [os.path.join(path_root, i) for i in dir_ini]
    try:
        for i in dir_ini:
            os.mkdir(i)
        print('初始化工作目录成功！')
    except:
        print('初始化工作目录失败，检查工作目录是否为空目录！')
