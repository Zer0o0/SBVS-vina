# 2020/9/16
#Author: pengyonglin
#
import os
import shutil


def delDir(path):  # 删除目录
    if os.path.exists(path):
        shutil.rmtree(path)
    else:
        pass


if __name__ == '__main__':
    path_root = os.getcwd()
    path_protein_pdb = os.path.join(path_root, 'protein\\protein_pdb')
    path_ligand_pdb = os.path.join(path_root, 'ligand\\ligand_pdb')
    path_pocasa = os.path.join(path_root, 'protein\\pocasa')
    path_screen_protein = os.path.join(path_root, 'screen\\protein_pdb')
    path_screen_ligand = os.path.join(path_root, 'screen\\ligand_pdb')
    path_screen_conf = os.path.join(path_root, 'screen\\confs')
    delDir(path_screen_ligand)
    shutil.copytree(path_ligand_pdb, path_screen_ligand)  #复制目录，迁移配体文件
    delDir(path_screen_conf)
    os.mkdir(path_screen_conf)
    delDir(path_screen_protein)
    os.mkdir(path_screen_protein)
    for i in os.listdir(path_pocasa):
        if i.endswith('.conf'):
            pro=i.split('.')[0]+'.pdb'
            conf_from = os.path.join(path_pocasa, i)  #迁移conf文件
            conf_to = os.path.join(path_screen_conf, i)
            pro_from=os.path.join(path_protein_pdb, pro)
            pro_to=os.path.join(path_screen_protein,pro)
            shutil.copyfile(conf_from, conf_to)
            shutil.copyfile(pro_from, pro_to)
    print('迁移数据完成！')
