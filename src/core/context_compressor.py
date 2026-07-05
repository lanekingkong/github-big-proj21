# CogniForge 智能上下文压缩引擎
#借鉴Headroom：分层压缩策略，节省60-95% token

import os, json, hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional

class shangxiawen_yasuo:
    """分层上下文压缩引擎
    
    三层压缩策略：
    Level 1 - 摘要层：项目简介（~200 tokens）
    Level 2 - 结构层：目录树+关键接口（~500 tokens）
    Level 3 - 细节层：当前焦点文件（按需加载）
    """
    
    def __init__(self, xiangmu_lujing: str, cunchujing_lujing: Optional[str]=None):
        self.xiangmu_lujing=Path(xiangmu_lujing).resolve()
        
        if cunchujing_lujing:
            self.cunchu=Path(cunchujing_lujing)
        else:
            self.cunchu=self.xiangmu_lujing/'.cogniforge'
        self.cunchu.mkdir(parents=True,exist_ok=True)
        
        self.yasuo_wenjian=self.cunchu/'context_cache.json'
        self.huancun={}
    
    def huode_shangxiawen(self, jibie: int=2, jiaodian_wenjian: list=None,
                           zuida_token: int=2000)->str:
        """获取压缩后的项目上下文
        
        参数：
            jibie: 1=摘要, 2=结构, 3=细节
            jiaodian_wenjian: 当前关注的焦点文件列表
            zuida_token: 最大token数（估算：1 token ≈ 4字符）
        """
        if jibie==1:
            return self._jibie1_zhaiyao()
        elif jibie==2:
            return self._jibie2_jiegou(jiaodian_wenjian, zuida_token)
        elif jibie==3:
            return self._jibie3_xijie(jiaodian_wenjian, zuida_token)
        return ''
    
    def _jibie1_zhaiyao(self)->str:
        """Level 1: 项目摘要（~200 tokens）"""
        xiangmu_ming=self.xiangmu_lujing.name
        
        #尝试读取README或项目描述
        readme_lujing=None
        for kexuan in['README.md','README.rst','README.txt',
                       'README_CN.md','readme.md','Readme.md']:
            p=self.xiangmu_lujing/kexuan
            if p.exists():
                readme_lujing=p
                break
        
        zhaiyao=''
        if readme_lujing:
            try:
                with open(readme_lujing,'r',encoding='utf-8',errors='ignore')as f:
                    neirong=f.read(800)  #读前800字符
                #取第一段有意义文字
                hang=neirong.split('\n')
                for h in hang:
                    h=h.strip()
                    if h and not h.startswith('#')and len(h)>20:
                        zhaiyao=h[:200]
                        break
            except Exception:
                pass
        
        if not zhaiyao:
            zhaiyao=f'项目 {xiangmu_ming} 的Python代码库。'
        
        #目录概览
        mulu_jiegou=self._kuaijie_mulu()
        
        return f"""## 项目：{xiangmu_ming}
{zhaiyao}

### 关键目录
{mulu_jiegou}
"""
    
    def _jibie2_jiegou(self, jiaodian_wenjian: list=None, zuida_token: int=2000)->str:
        """Level 2: 结构层（~500 tokens）"""
        jieguo=[self._jibie1_zhaiyao()]
        
        #文件结构
        jieguo.append('\n## 项目结构\n')
        jieguo.append('```\n')
        jieguo.append(self._shengcheng_mulushu(zuida_shendu=3))
        jieguo.append('```\n')
        
        #关键文件索引（从知识图谱缓存中获取）
        yasuo_wenjian=self.cunchu/'knowledge_graph.json'
        if yasuo_wenjian.exists():
            try:
                with open(yasuo_wenjian,'r',encoding='utf-8')as f:
                    tupu=json.load(f)
                
                jieguo.append('\n## 关键接口\n')
                zhongyao_shiti=[]
                for jiedian_id, shuju in tupu.get('nodes',{}).items():
                    if shuju.get('type')in('class','function'):
                        zhongyao_shiti.append({
                            'name':shuju['name'],
                            'type':shuju['type'],
                            'file':shuju['file'],
                            'line':shuju.get('line',0),
                            'doc':shuju.get('docstring','')[:80]
                        })
                
                #按文件名排序取前30
                zhongyao_shiti.sort(key=lambda x:x['file'])
                for shiti in zhongyao_shiti[:30]:
                    biaoji='class' if shiti['type']=='class' else 'def'
                    jieguo.append(f"- `{shiti['name']}` ({biaoji}) @ {shiti['file']}:{shiti['line']}\n")
            except Exception:
                pass
        
        #焦点文件内容
        if jiaodian_wenjian:
            jieguo.append('\n## 焦点文件\n')
            for wenjian in jiaodian_wenjian[:3]:  #最多3个焦点文件
                wanquan_lujing=self.xiangmu_lujing/wenjian
                if wanquan_lujing.exists():
                    try:
                        with open(wanquan_lujing,'r',encoding='utf-8',errors='ignore')as f:
                            neirong=f.read(600)
                        jieguo.append(f'### {wenjian}\n```python\n{neirong}\n```\n')
                    except Exception:
                        jieguo.append(f'### {wenjian}\n(无法读取)\n')
        
        zhengwen=''.join(jieguo)
        #估算token截断
        gusuan_changdu=zuida_token*4
        if len(zhengwen)>gusuan_changdu:
            zhengwen=zhengwen[:gusuan_changdu]+'\n...(上下文已截断)'
        
        return zhengwen
    
    def _jibie3_xijie(self, jiaodian_wenjian: list=None, zuida_token: int=2000)->str:
        """Level 3: 细节层"""
        jieguo=[self._jibie2_jiegou(jiaodian_wenjian, zuida_token)]
        
        #从记忆宫殿获取相关知识
        jiyi_wenjian=self.cunchu/'memory_palace.json'
        if jiyi_wenjian.exists():
            try:
                with open(jiyi_wenjian,'r',encoding='utf-8')as f:
                    gongdian=json.load(f)
                
                jieguo.append('\n## 相关记忆\n')
                jiyishu=0
                for yi in gongdian.get('wings',{}).values():
                    for zoulang in yi.get('halls',{}).values():
                        for fangjian in zoulang.get('rooms',{}).values():
                            for jiyi in fangjian.get('memories',[]):
                                if jiyishu>=10:
                                    break
                                jieguo.append(f"- [{zoulang['name']}] {jiyi['content'][:120]}\n")
                                jiyishu+=1
            except Exception:
                pass
        
        return ''.join(jieguo)
    
    def _kuaijie_mulu(self)->str:
        """快速获取目录结构（仅顶层）"""
        hang=[]
        try:
            for xiang in sorted(self.xiangmu_lujing.iterdir()):
                if xiang.name.startswith('.')or xiang.name.startswith('__'):
                    continue
                qianzhui='📁' if xiang.is_dir() else '📄'
                hang.append(f'{qianzhui} {xiang.name}')
        except PermissionError:
            pass
        return '\n'.join(hang[:10]) or '(空目录)'
    
    def _shengcheng_mulushu(self, mulus: Path=None, qianzhui: str='',
                            zuida_shendu: int=3, dangqian_shendu: int=0)->str:
        """生成ASCII目录树"""
        if mulus is None:
            mulus=self.xiangmu_lujing
        
        if dangqian_shendu>=zuida_shendu:
            return ''
        
        hang=[]
        paichu={'.git','__pycache__','node_modules','venv','.venv',
                '.cogniforge','dist','build','.pytest_cache',
                '.tox','.eggs','.mypy_cache','.ruff_cache'}
        
        try:
            zixiang=sorted([x for x in mulus.iterdir()
                          if x.name not in paichu and not x.name.startswith('.')])
        except PermissionError:
            return ''
        
        for i, xiang in enumerate(zixiang):
            zuihou=i==len(zixiang)-1
            jiedian='└── ' if zuihou else '├── '
            hang.append(f'{qianzhui}{jiedian}{xiang.name}\n')
            
            if xiang.is_dir() and dangqian_shendu+1<zuida_shendu:
                xin_qianzhui=qianzhui+('    ' if zuihou else '│   ')
                hang.append(self._shengcheng_mulushu(
                    xiang, xin_qianzhui, zuida_shendu, dangqian_shendu+1))
        
        return ''.join(hang)
    
    def yasuo_dai_yaoqiu(self, yuanshi_shangxiawen: str, yuan_shu: str='zh')->str:
        """针对AI请求的上下文压缩
        
        智能去除不相关部分，保留核心信息，减少token浪费
        """
        #估算当前token数
        gusuan_token=len(yuanshi_shangxiawen)//4
        jieguo=yuanshi_shangxiawen
        
        #如果超过2000 token，应用压缩
        if gusuan_token>2000:
            #策略：保留项目结构+关键接口，裁剪详细内容
            hang=jieguo.split('\n')
            jingjian_hang=[]
            jiexi_biaoji=0
            
            for h in hang:
                if h.startswith('##')or h.startswith('###'):
                    jiexi_biaoji+=1
                #保留标题和前两个段落
                if jiexi_biaoji<=5 or h.startswith('-')or h.startswith('```'):
                    jingjian_hang.append(h)
            
            jieguo='\n'.join(jingjian_hang)
        
        #添加压缩提示
        jieguo+=f'\n\n> 上下文已压缩 | 原始约{gusuan_token}tokens | 压缩后约{len(jieguo)//4}tokens'
        return jieguo
    
    def quxiao_huancun(self):
        """清除压缩缓存"""
        if self.yasuo_wenjian.exists():
            self.yasuo_wenjian.unlink()
        self.huancun={}
