# CogniForge 代码知识图谱引擎
#借鉴codegraph：预建索引 + Understand-Anything：交互式知识图谱

import ast, os, json, re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Optional

class zhishitupu:
    """代码知识图谱引擎 - 零LLM调用自动构建代码结构索引"""
    
    def __init__(self, xiangmu_lujing: str, cunchujing_lujing: Optional[str]=None):
        self.xiangmu_lujing=Path(xiangmu_lujing).resolve()
        
        if cunchujing_lujing:
            self.cunchu=Path(cunchujing_lujing)
        else:
            self.cunchu=self.xiangmu_lujing/'.cogniforge'
        self.cunchu.mkdir(parents=True,exist_ok=True)
        
        self.tupu_wenjian=self.cunchu/'knowledge_graph.json'
        self.tupu={
            'meta':{'project':str(self.xiangmu_lujing),'updated':''},
            'nodes':{},      #实体节点
            'edges':[],      #关系边
            'file_index':{}  #文件→节点映射
        }
    
    def goujian_suoyin(self, paichu: list=None)->dict:
        """构建代码知识图谱索引
        
        扫描项目代码，提取：
        - 函数/类/模块定义
        - 导入关系
        - 函数调用链
        - 继承关系
        """
        if paichu is None:
            paichu=['.git','__pycache__','node_modules','venv','.venv',
                    '.cogniforge','dist','build','.tox','.eggs']
        
        wenjian_liebiao=[]
        for gen in self.xiangmu_lujing.rglob('*.py'):
            lujing_str=str(gen)
            if not any(p in lujing_str for p in paichu):
                wenjian_liebiao.append(gen)
        
        self.tupu['nodes']={}
        self.tupu['edges']=[]
        self.tupu['file_index']={}
        
        for wenjian in wenjian_liebiao:
            try:
                with open(wenjian,'r',encoding='utf-8',errors='ignore')as f:
                    yuandaima=f.read()
                self._jiexi_wenjian(wenjian, yuandaima)
            except (SyntaxError,UnicodeDecodeError):
                continue
        
        self.tupu['meta']['updated']=datetime.now().isoformat()
        self._baocun()
        return self.tongji()
    
    def _jiexi_wenjian(self, wenjian: Path, yuandaima: str):
        """解析单个文件的代码结构"""
        xiangdui_lujing=str(wenjian.relative_to(self.xiangmu_lujing))
        
        #文件节点
        wenjian_jiedian=f'file:{xiangdui_lujing}'
        self.tupu['nodes'][wenjian_jiedian]={
            'type':'file',
            'path':xiangdui_lujing,
            'name':wenjian.name,
            'size':len(yuandaima)
        }
        self.tupu['file_index'][xiangdui_lujing]=[]
        
        try:
            shu=ast.parse(yuandaima)
        except SyntaxError:
            return
        
        #析取导入关系
        for jiedian in ast.walk(shu):
            if isinstance(jiedian, ast.Import):
                for bieming in jiedian.names:
                    self._tianjia_bian(shi_ti_id=wenjian_jiedian,
                                      mubiao_ming=bieming.name,
                                      leixing='imports',
                                      wenjian_lujing=xiangdui_lujing)
            elif isinstance(jiedian, ast.ImportFrom):
                mo_kuai=jiedian.module or ''
                for bieming in jiedian.names:
                    quan_ming=f'{mo_kuai}.{bieming.name}' if mo_kuai else bieming.name
                    self._tianjia_bian(shi_ti_id=wenjian_jiedian,
                                      mubiao_ming=quan_ming,
                                      leixing='imports_from',
                                      wenjian_lujing=xiangdui_lujing)
        
        #析取类定义
        for jiedian in ast.walk(shu):
            if isinstance(jiedian, ast.ClassDef):
                lei_id=f'class:{xiangdui_lujing}:{jiedian.name}'
                jichu_liebiao=[self._huoqu_ming(jc)for jc in jiedian.bases]
                
                self.tupu['nodes'][lei_id]={
                    'type':'class',
                    'name':jiedian.name,
                    'file':xiangdui_lujing,
                    'line':jiedian.lineno,
                    'bases':jichu_liebiao,
                    'docstring':ast.get_docstring(jiedian)or''
                }
                self.tupu['file_index'][xiangdui_lujing].append(lei_id)
                
                #继承关系
                for jc in jichu_liebiao:
                    self._tianjia_bian(shi_ti_id=lei_id, mubiao_ming=jc,
                                      leixing='inherits', wenjian_lujing=xiangdui_lujing)
                
                #类方法
                for zidongxi in jiedian.body:
                    if isinstance(zidongxi, ast.FunctionDef):
                        self._jiexi_hanshu(zidongxi, xiangdui_lujing, suoshu_lei=jiedian.name)
        
        #析取顶层函数
        for jiedian in shu.body:
            if isinstance(jiedian, ast.FunctionDef):
                self._jiexi_hanshu(jiedian, xiangdui_lujing)
    
    def _jiexi_hanshu(self, jiedian: ast.FunctionDef, wenjian_lujing: str, suoshu_lei: str=''):
        """解析函数定义"""
        qianzhui=f'{suoshu_lei}.' if suoshu_lei else ''
        hanshu_id=f'function:{wenjian_lujing}:{qianzhui}{jiedian.name}'
        
        #提取函数签名
        canshu=[arg.arg for arg in jiedian.args.args]
        zhuangshiqi=[self._huoqu_ming(d)for d in jiedian.decorator_list]
        
        self.tupu['nodes'][hanshu_id]={
            'type':'function',
            'name':jiedian.name,
            'class':suoshu_lei,
            'file':wenjian_lujing,
            'line':jiedian.lineno,
            'params':canshu,
            'decorators':zhuangshiqi,
            'docstring':ast.get_docstring(jiedian)or''
        }
        self.tupu['file_index'][wenjian_lujing].append(hanshu_id)
        
        #析取函数调用
        for zi_jiedian in ast.walk(jiedian):
            if isinstance(zi_jiedian, ast.Call):
                diaoyong_ming=self._huoqu_ming(zi_jiedian.func)
                self._tianjia_bian(shi_ti_id=hanshu_id, mubiao_ming=diaoyong_ming,
                                  leixing='calls', wenjian_lujing=wenjian_lujing)
    
    def _huoqu_ming(self, jiedian)->str:
        """从AST节点获取完整名称"""
        if isinstance(jiedian, ast.Name):
            return jiedian.id
        elif isinstance(jiedian, ast.Attribute):
            return f'{self._huoqu_ming(jiedian.value)}.{jiedian.attr}'
        elif isinstance(jiedian, ast.Subscript):
            return self._huoqu_ming(jiedian.value)
        elif isinstance(jiedian, ast.Call):
            return self._huoqu_ming(jiedian.func)
        elif isinstance(jiedian, ast.Constant):
            return str(jiedian.value)
        return 'unknown'
    
    def _tianjia_bian(self, shi_ti_id: str, mubiao_ming: str, leixing: str, wenjian_lujing: str):
        """添加关系边"""
        self.tupu['edges'].append({
            'source':shi_ti_id,
            'target':mubiao_ming,
            'type':leixing,
            'file':wenjian_lujing
        })
    
    def chaxun(self, sousuo_ci: str, leixing: str='')->list:
        """搜索知识图谱中的实体
        
        参数：
            sousuo_ci: 搜索关键词（函数名/类名/文件名）
            leixing: 过滤类型（file/class/function）
        """
        jieguo=[]
        for jiedian_id, jiedian_shuju in self.tupu['nodes'].items():
            if leixing and jiedian_shuju.get('type')!=leixing:
                continue
            
            pipei=False
            mingcheng=jiedian_shuju.get('name','')
            if sousuo_ci.lower() in mingcheng.lower():
                pipei=True
            elif sousuo_ci.lower() in jiedian_shuju.get('docstring','').lower():
                pipei=True
            
            if pipei:
                jieguo.append({'id':jiedian_id,**jiedian_shuju})
        
        return jieguo
    
    def huode_xiangguan(self, jiedian_id: str, jvli: int=1)->dict:
        """获取节点的关联实体（1跳邻居）"""
        xiangguan={'incoming':[],'outgoing':[]}
        
        for bian in self.tupu['edges']:
            if bian['source']==jiedian_id:
                mubiao=bian['target']
                if mubiao in self.tupu['nodes']:
                    xiangguan['outgoing'].append({
                        'target':mubiao,
                        'type':bian['type'],
                        'node':self.tupu['nodes'][mubiao]
                    })
            if bian['target']==jiedian_id or bian['target'] in jiedian_id:
                xiangguan['incoming'].append({
                    'source':bian['source'],
                    'type':bian['type'],
                    'node':self.tupu['nodes'].get(bian['source'],{})
                })
        
        return xiangguan
    
    def shengcheng_wendang(self, geshi: str='markdown')->str:
        """生成知识图谱文档"""
        if geshi=='markdown':
            return self._shengcheng_markdown()
        elif geshi=='json':
            return json.dumps(self.tupu,indent=2,ensure_ascii=False)
        return ''
    
    def _shengcheng_markdown(self)->str:
        """生成Markdown格式的代码地图"""
        hang=['# 代码知识图谱\n']
        hang.append(f'项目：{self.tupu["meta"]["project"]}\n')
        hang.append(f'更新时间：{self.tupu["meta"]["updated"]}\n\n')
        
        #按文件组织
        an_wenjian=defaultdict(list)
        for jiedian_id, shuju in self.tupu['nodes'].items():
            if shuju.get('type')in('class','function'):
                an_wenjian[shuju.get('file','unknown')].append(shuju)
        
        for wenjian, shitiliebiao in sorted(an_wenjian.items()):
            hang.append(f'## {wenjian}\n')
            for shiti in shitiliebiao:
                leixing_biaoji='🔷' if shiti['type']=='class' else '🔹'
                hang.append(f'- {leixing_biaoji} **{shiti["name"]}** (行{shiti.get("line","?")})')
                if shiti.get('docstring'):
                    hang.append(f'  - {shiti["docstring"][:100]}')
                hang.append('')
        
        #边统计
        leixing_tongji=defaultdict(int)
        for bian in self.tupu['edges']:
            leixing_tongji[bian['type']]+=1
        
        hang.append('\n## 关系统计\n')
        for lx, sl in leixing_tongji.items():
            hang.append(f'- {lx}: {sl}条\n')
        
        return ''.join(hang)
    
    def _baocun(self):
        """持久化知识图谱"""
        with open(self.tupu_wenjian,'w',encoding='utf-8')as f:
            json.dump(self.tupu,f,indent=2,ensure_ascii=False)
    
    def jiazai(self)->dict:
        """从磁盘加载知识图谱"""
        if self.tupu_wenjian.exists():
            with open(self.tupu_wenjian,'r',encoding='utf-8')as f:
                self.tupu=json.load(f)
        return self.tupu
    
    def tongji(self)->dict:
        """获取图谱统计"""
        return {
            'total_nodes':len(self.tupu['nodes']),
            'total_edges':len(self.tupu['edges']),
            'files_indexed':len(self.tupu['file_index']),
            'node_types':{
                'function':sum(1 for n in self.tupu['nodes'].values()if n['type']=='function'),
                'class':sum(1 for n in self.tupu['nodes'].values()if n['type']=='class'),
                'file':sum(1 for n in self.tupu['nodes'].values()if n['type']=='file')
            }
        }
