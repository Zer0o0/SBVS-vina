# 2020/8/24
# Author: pengyonglin
#
import os
import re
import copy


class pdbError(Exception):
    pass


class pdbBase:
    # pdb标签
    def __init__(self):
        self.sections = {'Title': ['HEADER', 'SOURCE', 'AUTHOR', 'OBSLTE', 'KEYWDS', 'REVDAT',
                                   'TITLE', 'EXPDTA', 'SPRSDE', 'SPLT', 'NUMMDL', 'JRNL',
                                   'CAVEAT', 'MDLTYP', 'REMARKS', 'COMPND'],
                         'Primary_structure': ['DBREF', 'SEQADV', 'MODRES', 'DBREF1/DBREF2', 'SEQRES'],
                         'Heterogen': ['HET', 'HETNAM', 'HETSYN', 'FORMUL'],
                         'Secondary_structure': ['HELIX', 'SHEET'],
                         'Connectivity_annotation': ['SSBOND', 'LINK', 'CISPEP'],
                         'Miscellaneous_features': ['SITE'],
                         'Crystallographic_and_coordinate_transformation': ['CRYST1', 'ORIGXn', 'SCALEn', 'MTRIXn'],
                         'coordinate': ['MODEL', 'ANISOU', 'HETATM', 'ATOM', 'TER', 'ENDMDL'],
                         'Connectivity': ['CONECT'],
                         'Bookkeeping': ['MASTER', 'END']
                         }
        self.amino_acids = ['ALA', 'CYS', 'ASP', 'GLU', 'PHE', 'GLY', 'HIS', 'ILE', 'LYS',
                            'LEU', 'MET', 'ASN', 'PRO', 'GLN', 'ARG', 'SER', 'THR', 'VAL', 'TRP', 'TYR']
        self.deoxyribonucleotides = ['DA', 'DC', 'DG', 'DT', 'DI']
        self.ribonucleotides = ['A', 'C', 'G', 'U', 'I']
        self.version = 'Version 3.3'


class pdbParser(pdbBase):
    def __init__(self, pdbifh):
        super().__init__()
        self.__containerList = []  # pdb标签
        self.__containerDetail = {}  # pdb完整内容
        self.__coorAtom = {}
        self.__coorTer = {}
        self.__coorHetatm = {}
        self.__reader(pdbifh)
        self.__splitAtom()
        self.__splitTer()

        self.pdbID = ''
        self.title = ''
        self.molecules = []
        # self.chains = []
        self.chains = list(self.__coorAtom.keys())
        self.gene = ''
        self.sequence = {}

    def __reader(self, pdbifh):
        for line in pdbifh.readlines():
            tag = line[0:6].strip()
            if tag in self.__containerDetail:
                self.__containerDetail[tag].append(line)
            else:
                self.__containerDetail[tag] = [line]
                self.__containerList.append(tag)

    def __splitAtom(self):
        # 按照链ID分开
        # 22位置为链ID
        for i in self.__containerDetail['ATOM']:
            chaid = i[21]
            if chaid in self.__coorAtom:
                self.__coorAtom[chaid].append(i)
            else:
                self.__coorAtom[chaid] = [i]

    def __splitTer(self):
        # 按照链ID分开
        # 22位置为链ID
        for i in self.__containerDetail['TER']:
            chaid = i[21]
            if chaid in self.__coorTer:
                self.__coorTer[chaid].append(i)
            else:
                self.__coorTer[chaid] = [i]

    def __splitHetatm(self):
        # 按照链ID，分子名称分开
        # 22位置为链ID，18-20位置为分子名
        for i in self.__containerDetail['HETATM']:
            chaid = i[21]
            # name=i[17:20]
            if chaid in self.__coorHetatm:
                self.__coorHetatm[chaid].append(i)
            else:
                self.__coorHetatm[chaid] = [i]

    def getMolecules(self):
        # COMPND//MOLECULE
        # 11-80位置表示分子名称，链ID等
        if self.molecules:
            return self.molecules
        else:
            compnd = [i[10:80] for i in self.__containerDetail['COMPND']]
            compnd_ = ''.join(compnd)
            pat_mol = re.compile(r'MOLECULE: (.*?);', re.S)
            self.molecules = re.findall(pat_mol, compnd_)
            return self.molecules

    def getChains(self):
        # COMPND//CHAIN
        if self.chains:
            return self.chains
        else:
            compnd = [i[10:80] for i in self.__containerDetail['COMPND']]
            compnd_ = ''.join(compnd)
            # pat_cha = re.compile(r'CHAIN: (.*?);', re.S)
            pat_cha = re.compile(r'CHAIN: (.{62}?)')
            chas = re.findall(pat_cha, compnd_)
            # self.chains = list(''.join([i.replace(', ', '')
            #                             for i in chas]))  # 分开同聚物的链
            self.chains = list(''.join([i.replace(', ', '').replace(';', '').strip()
                                        for i in chas]))  # 分开同聚物的链
            return self.chains

    def getSequences(self):
        # SEQRES
        # 12位置为链ID，20-70表示残基
        if self.sequence:
            return self.sequence
        else:
            seqs = {}
            for i in self.__containerDetail['SEQRES']:
                chaid = i[11]
                if chaid in seqs:
                    seqs[chaid].append(i[19:70])
                else:
                    seqs[chaid] = [i[19:70]]
            self.sequence = {k: ' '.join(seqs[k]).strip() for k in seqs.keys()}
            return self.sequence

    def getPdbID(self):
        # HEADER
        self.pdbID = self.__containerDetail['HEADER'][0][62:66].strip()
        return self.pdbID

    def getTitle(self):
        # TITLE
        pass

    def getGene(self):
        # SOURCE
        source = ''.join(self.__containerDetail['SOURCE'])
        pat_gen = re.compile(r'GENE: (.*?);')
        self.gene = re.search(pat_gen, source).group(1)
        return self.gene

    def writer(self, pdbofh, chainid=''):
        # 默认全部蛋白链
        def merge_list2(l):
            l0 = []
            for i in l:
                for j in i:
                    l0.extend(j)
            return l0
        if chainid == '':
            chainid = self.chains
        else:
            chainid = list(chainid)
        if not set(chainid) <= set(self.chains):
            raise pdbError('需求链不在结构中！')
        keep = ['HEADER', 'TITLE', 'COMPND', 'ATOM_TER', 'MASTER', 'END']
        pdbout = copy.deepcopy(self.__containerDetail)  # 深拷贝，改写字典
        pdbout['ATOM'] = [self.__coorAtom[i] for i in chainid]
        pdbout['TER'] = [self.__coorTer[i] for i in chainid]
        pdbout['ATOM_TER'] = merge_list2(
            list(zip(pdbout['ATOM'], pdbout['TER'])))
        for i in keep:
            pdbofh.writelines(pdbout[i])
