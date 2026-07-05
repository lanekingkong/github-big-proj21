# CogniForge 记忆宫殿引擎
#借鉴MemPalace/mem0/GBrain架构：空间记忆模型 + 分层存储 + 记忆巩固

import json, os, hashlib, time
from pathlib import Path
from datetime import datetime
from typing import Optional
from collections import defaultdict

class jiyigongdian:  #记忆宫殿核心类
    """分层空间记忆引擎，借鉴记忆宫殿法(Method of Loci)
    
    Palace（宫殿）
      ├── Wing（翼：按项目/人物分区）
      │   ├── Hall（走廊：按记忆类型分类）
      │   │   ├── Room（房间：具体主题）
      │   │   │   ├── Memory（记忆条目）
    """
    
    def __init__(self, xiangmu_lujing: str, cunchujing_lujing: Optional[str]=None):
        self.xiangmu_lujing=Path(xiangmu_lujing).resolve()
        self.xiangmu_ming=xiangmu_lujing.name if hasattr(xiangmu_lujing,'name') else 'unnamed'
        
        if cunchujing_lujing:
            self.cunchu=Path(cunchujing_lujing)
        else:
            self.cunchu=self.xiangmu_lujing/'.cogniforge'
        self.cunchu.mkdir(parents=True,exist_ok=True)
        
        self.jiyi_wenjian=self.cunchu/'memory_palace.json'
        self._jiazai_gongdian()
    
    def _jiazai_gongdian(self):
        """加载或初始化记忆宫殿结构"""
        if self.jiyi_wenjian.exists():
            with open(self.jiyi_wenjian,'r',encoding='utf-8')as f:
                self.gongdian=json.load(f)
        else:
            self.gongdian={
                'meta':{
                    'project':str(self.xiangmu_lujing),
                    'created':datetime.now().isoformat(),
                    'version':'0.1.0',
                    'total_memories':0
                },
                'wings':{}
            }
            self._baocun()
    
    def _baocun(self):
        """持久化宫殿结构"""
        self.gongdian['meta']['total_memories']=self._tongji_jiyi()
        self.gongdian['meta']['updated']=datetime.now().isoformat()
        with open(self.jiyi_wenjian,'w',encoding='utf-8')as f:
            json.dump(self.gongdian,f,indent=2,ensure_ascii=False)
    
    def _tongji_jiyi(self)->int:
        """统计总记忆数"""
        zongshu=0
        for yi in self.gongdian.get('wings',{}).values():
            for zoulang in yi.get('halls',{}).values():
                for fangjian in zoulang.get('rooms',{}).values():
                    zongshu+=len(fangjian.get('memories',[]))
        return zongshu
    
    def chuangjian_yi(self, yi_ming: str, miaoshu: str=''):
        """创建新的翼（Wing），按项目/人物分区"""
        yi_id=self._shengcheng_id(yi_ming)
        if yi_id not in self.gongdian['wings']:
            self.gongdian['wings'][yi_id]={
                'name':yi_ming,
                'description':miaoshu,
                'created':datetime.now().isoformat(),
                'halls':self._moren_zoulang()
            }
            self._baocun()
        return yi_id
    
    def _moren_zoulang(self):
        """默认的记忆分类走廊"""
        return {
            'decisions':{'name':'架构决策','description':'技术选型、架构设计等决策','rooms':{}},
            'patterns':{'name':'代码模式','description':'复用的代码模式和最佳实践','rooms':{}},
            'knowledge':{'name':'领域知识','description':'业务逻辑、专业领域知识','rooms':{}},
            'fixes':{'name':'问题修复','description':'Bug修复记录和解决方案','rooms':{}},
            'context':{'name':'项目上下文','description':'项目结构、配置、环境信息','rooms':{}}
        }
    
    def jilu(self, neirong: str, zhuti: str='', yi_ming: str='default',
             zoulang_leixing: str='knowledge', biaoqian: list=None)->str:
        """记录一条新记忆
        
        参数：
            neirong: 记忆内容
            zhuti: 主题（作为Room名称）
            yi_ming: 所属翼（Wing）
            zoulang_leixing: 走廊类型（decisions/patterns/knowledge/fixes/context）
            biaoqian: 标签列表
        
        返回：记忆ID
        """
        #确保翼存在
        yi_id=self._shengcheng_id(yi_ming)
        if yi_id not in self.gongdian['wings']:
            self.chuangjian_yi(yi_ming)
        
        yi=self.gongdian['wings'][yi_id]
        
        #确保走廊类型存在
        if zoulang_leixing not in yi['halls']:
            yi['halls'][zoulang_leixing]={
                'name':zoulang_leixing,
                'description':'',
                'rooms':{}
            }
        
        zoulang=yi['halls'][zoulang_leixing]
        
        #确保房间存在
        fangjian_ming=zhuti if zhuti else 'general'
        fangjian_id=self._shengcheng_id(fangjian_ming)
        if fangjian_id not in zoulang['rooms']:
            zoulang['rooms'][fangjian_id]={
                'name':fangjian_ming,
                'memories':[]
            }
        
        #创建记忆条目
        jiyi_id=self._shengcheng_id(neirong[:50])
        jiyi_tiaomu={
            'id':jiyi_id,
            'content':neirong,
            'timestamp':datetime.now().isoformat(),
            'tags':biaoqian or [],
            'source':'manual',
            'access_count':0
        }
        
        zoulang['rooms'][fangjian_id]['memories'].append(jiyi_tiaomu)
        self._baocun()
        return jiyi_id
    
    def huiqu(self, chaxun: str='', yi_ming: str='', zoulang_leixing: str='',
              xianzhi: int=10)->list:
        """召回记忆
        
        支持按：查询文本模糊匹配、翼名过滤、走廊类型过滤
        返回按时间排序的记忆列表
        """
        jieguo=[]
        
        for yi_id, yi in self.gongdian.get('wings',{}).items():
            #过滤翼
            if yi_ming and yi_ming.lower() not in yi['name'].lower():
                continue
            
            for zl_id, zoulang in yi.get('halls',{}).items():
                #过滤走廊类型
                if zoulang_leixing and zoulang_leixing!=zl_id:
                    continue
                
                for fj_id, fangjian in zoulang.get('rooms',{}).items():
                    for jiyi in fangjian.get('memories',[]):
                        #文本模糊匹配
                        if chaxun:
                            if chaxun.lower() in jiyi['content'].lower():
                                jiyi['access_count']+=1
                                jieguo.append({
                                    'wing':yi['name'],
                                    'hall':zoulang['name'],
                                    'room':fangjian['name'],
                                    **jiyi
                                })
                        else:
                            jiyi['access_count']+=1
                            jieguo.append({
                                'wing':yi['name'],
                                'hall':zoulang['name'],
                                'room':fangjian['name'],
                                **jiyi
                            })
        
        #按时间排序
        jieguo.sort(key=lambda x:x['timestamp'],reverse=True)
        self._baocun()  #保存access_count更新
        return jieguo[:xianzhi]
    
    def sousuo_yujing(self, chaxun: str, top_k: int=5)->list:
        """语义搜索记忆（使用向量存储后端）"""
        #这里依赖vector_store进行真正的语义搜索
        from .storage.vector_store import VectorStore
        try:
            vs=VectorStore(str(self.cunchu))
            return vs.search(chaxun, top_k)
        except ImportError:
            #降级为关键词搜索
            return self.huiqu(chaxun, xianzhi=top_k)
    
    def gonggu_jiyi(self, jiange_xiaoshi: float=24.0):
        """记忆巩固：整理碎片化记忆，合并重复，升级重要记忆
        
        借鉴GBrain的Dream Cycle概念——夜间自动运行
        距离上次巩固超过间隔才执行
        """
        zuihou_gonggu=self.gongdian['meta'].get('last_consolidation','')
        if zuihou_gonggu:
            shijiancha=(datetime.now()-datetime.fromisoformat(zuihou_gonggu)).total_seconds()/3600
            if shijiancha<jiange_xiaoshi:
                return 0  #不需要巩固
        
        hebing_shu=0
        
        for yi in self.gongdian.get('wings',{}).values():
            for zoulang in yi.get('halls',{}).values():
                for fangjian in zoulang.get('rooms',{}).values():
                    jiyi_liebiao=fangjian.get('memories',[])
                    if len(jiyi_liebiao)<=1:
                        continue
                    
                    #简单合并：内容相似度>80%的记忆
                    xin_jiyi=[]
                    yichuli=set()
                    for i, j1 in enumerate(jiyi_liebiao):
                        if i in yichuli:
                            continue
                        hebing_neirong=j1['content']
                        hebing_biaoqian=j1['tags'].copy()
                        for j, j2 in enumerate(jiyi_liebiao):
                            if j<=i or j in yichuli:
                                continue
                            #简单相似度判断
                            if self._xiangsidu(j1['content'],j2['content'])>0.7:
                                hebing_neirong+=' | '+j2['content']
                                hebing_biaoqian.extend(j2['tags'])
                                yichuli.add(j)
                                hebing_shu+=1
                        
                        xin_jiyi.append({
                            'id':j1['id'],
                            'content':hebing_neirong,
                            'timestamp':datetime.now().isoformat(),
                            'tags':list(set(hebing_biaoqian)),
                            'source':'consolidated',
                            'access_count':j1['access_count']
                        })
                    
                    fangjian['memories']=xin_jiyi
        
        self.gongdian['meta']['last_consolidation']=datetime.now().isoformat()
        self._baocun()
        return hebing_shu
    
    def _xiangsidu(self, wenben1: str, wenben2: str)->float:
        """简单的Jaccard相似度"""
        jihe1=set(wenben1.lower().split())
        jihe2=set(wenben2.lower().split())
        if not jihe1 or not jihe2:
            return 0.0
        return len(jihe1&jihe2)/len(jihe1|jihe2)
    
    def _shengcheng_id(self, yuan: str)->str:
        """生成短ID"""
        return hashlib.md5(yuan.encode()).hexdigest()[:12]
    
    def daochu_mcp(self)->dict:
        """导出为MCP可用的记忆上下文"""
        shangxiawen=[]
        for yi_id, yi in self.gongdian.get('wings',{}).items():
            for zoulang in yi.get('halls',{}).values():
                for fangjian in zoulang.get('rooms',{}).values():
                    for jiyi in fangjian.get('memories',[]):
                        shangxiawen.append({
                            'type':zoulang['name'],
                            'wing':yi['name'],
                            'topic':fangjian['name'],
                            'content':jiyi['content'],
                            'tags':jiyi['tags']
                        })
        return {'project':self.xiangmu_ming,'memories':shangxiawen}
    
    def tongji(self)->dict:
        """获取记忆统计信息"""
        tongji_data={
            'total_memories':self._tongji_jiyi(),
            'wings_count':len(self.gongdian.get('wings',{})),
            'by_hall':{}
        }
        for yi in self.gongdian.get('wings',{}).values():
            for zl_id, zoulang in yi.get('halls',{}).items():
                shu=sum(len(f.get('memories',[]))for f in zoulang.get('rooms',{}).values())
                tongji_data['by_hall'][zl_id]=tongji_data['by_hall'].get(zl_id,0)+shu
        return tongji_data
