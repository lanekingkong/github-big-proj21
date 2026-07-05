# CogniForge 跨工具同步桥接
#解决Claude Code/Cursor/Copilot等多AI工具间的知识孤岛

import os, json, shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

class tongbqiaojie:
    """跨AI工具知识同步引擎
    
    支持同步到：
    - Claude Code (.claude/skills/)
    - Cursor (.cursor/rules/)
    - GitHub Copilot (.github/copilot-instructions.md)
    - 通用MCP协议
    """
    
    def __init__(self, xiangmu_lujing: str, cunchujing_lujing: Optional[str]=None):
        self.xiangmu_lujing=Path(xiangmu_lujing).resolve()
        
        if cunchujing_lujing:
            self.cunchu=Path(cunchujing_lujing)
        else:
            self.cunchu=self.xiangmu_lujing/'.cogniforge'
        
        self.zhichi_gongju={
            'claude':{'lujing':'.claude/skills/cogniforge','geshi':'md'},
            'cursor':{'lujing':'.cursor/rules','geshi':'mdc'},
            'copilot':{'lujing':'.github/copilot-instructions.md','geshi':'md'}
        }
    
    def tongbu_dao_gongju(self, mubiao_gongju: str)->dict:
        """将CogniForge知识同步到指定AI工具
        
        返回：同步结果摘要
        """
        if mubiao_gongju not in self.zhichi_gongju:
            return {'error':f'不支持的工具：{mubiao_gongju}',
                    'supported':list(self.zhichi_gongju.keys())}
        
        peizhi=self.zhichi_gongju[mubiao_gongju]
        mubiao_lujing=self.xiangmu_lujing/peizhi['lujing']
        
        if mubiao_gongju=='claude':
            return self._tongbu_claude(mubiao_lujing)
        elif mubiao_gongju=='cursor':
            return self._tongbu_cursor(mubiao_lujing)
        elif mubiao_gongju=='copilot':
            return self._tongbu_copilot(mubiao_lujing)
    
    def _tongbu_claude(self, mubiao_lujing: Path)->dict:
        """同步到Claude Code Skills"""
        mubiao_lujing.mkdir(parents=True,exist_ok=True)
        
        #收集记忆
        jiyi_neirong=self._shouji_jiyi()
        tupu_neirong=self._shouji_tupu_zhaiyao()
        
        #生成Claude Skill文件
        skill_neirong=self._shengcheng_claude_skill(jiyi_neirong, tupu_neirong)
        
        skill_wenjian=mubiao_lujing/'cogniforge-memory.md'
        with open(skill_wenjian,'w',encoding='utf-8')as f:
            f.write(skill_neirong)
        
        return {'tool':'claude','file':str(skill_wenjian),
                'memories':len(jiyi_neirong),'graph_nodes':tupu_neirong.get('total_nodes',0)}
    
    def _tongbu_cursor(self, mubiao_lujing: Path)->dict:
        """同步到Cursor Rules"""
        mubiao_lujing.mkdir(parents=True,exist_ok=True)
        
        jiyi_neirong=self._shouji_jiyi()
        tupu_neirong=self._shouji_tupu_zhaiyao()
        
        #生成Cursor Rule
        guize_neirong=self._shengcheng_cursor_rule(jiyi_neirong, tupu_neirong)
        
        guize_wenjian=mubiao_lujing/'cogniforge-context.mdc'
        with open(guize_wenjian,'w',encoding='utf-8')as f:
            f.write(guize_neirong)
        
        return {'tool':'cursor','file':str(guize_wenjian),
                'memories':len(jiyi_neirong),'graph_nodes':tupu_neirong.get('total_nodes',0)}
    
    def _tongbu_copilot(self, mubiao_lujing: Path)->dict:
        """同步到GitHub Copilot"""
        mubiao_lujing.parent.mkdir(parents=True,exist_ok=True)
        
        jiyi_neirong=self._shouji_jiyi()
        tupu_neirong=self._shouji_tupu_zhaiyao()
        
        #生成Copilot指令
        zhiling_neirong=self._shengcheng_copilot_zhiling(jiyi_neirong, tupu_neirong)
        
        #如果文件已存在，追加而非覆盖
        xianyou=''
        if mubiao_lujing.exists():
            with open(mubiao_lujing,'r',encoding='utf-8')as f:
                xianyou=f.read()
        
        #查找CogniForge段并替换
        biaoji_kaishi='<!-- COGNIFORGE_CONTEXT_START -->'
        biaoji_jieshu='<!-- COGNIFORGE_CONTEXT_END -->'
        
        if biaoji_kaishi in xianyou:
            kaishi_idx=xianyou.index(biaoji_kaishi)
            jieshu_idx=xianyou.index(biaoji_jieshu)+len(biaoji_jieshu)
            xin_neirong=xianyou[:kaishi_idx]+zhiling_neirong+xianyou[jieshu_idx:]
        else:
            xin_neirong=xianyou+'\n'+zhiling_neirong if xianyou else zhiling_neirong
        
        with open(mubiao_lujing,'w',encoding='utf-8')as f:
            f.write(xin_neirong)
        
        return {'tool':'copilot','file':str(mubiao_lujing),
                'memories':len(jiyi_neirong),'graph_nodes':tupu_neirong.get('total_nodes',0)}
    
    def tongbu_suoyou(self)->list:
        """同步到所有支持的AI工具"""
        jieguo=[]
        for gongju in self.zhichi_gongju:
            jieguo.append(self.tongbu_dao_gongju(gongju))
        return jieguo
    
    def _shouji_jiyi(self)->list:
        """从记忆宫殿收集记忆"""
        jiyi_wenjian=self.cunchu/'memory_palace.json'
        if not jiyi_wenjian.exists():
            return []
        
        with open(jiyi_wenjian,'r',encoding='utf-8')as f:
            gongdian=json.load(f)
        
        suoyou_jiyi=[]
        for yi_id, yi in gongdian.get('wings',{}).items():
            for zl_id, zoulang in yi.get('halls',{}).items():
                for fj_id, fangjian in zoulang.get('rooms',{}).items():
                    for jiyi in fangjian.get('memories',[]):
                        suoyou_jiyi.append({
                            'content':jiyi['content'],
                            'type':zoulang['name'],
                            'topic':fangjian['name'],
                            'tags':jiyi.get('tags',[]),
                            'timestamp':jiyi['timestamp'],
                            'access_count':jiyi.get('access_count',0)
                        })
        
        #按访问次数排序，取最重要的50条
        suoyou_jiyi.sort(key=lambda x:x['access_count'],reverse=True)
        return suoyou_jiyi[:50]
    
    def _shouji_tupu_zhaiyao(self)->dict:
        """从知识图谱收集摘要"""
        tupu_wenjian=self.cunchu/'knowledge_graph.json'
        if not tupu_wenjian.exists():
            return {'total_nodes':0,'key_classes':[],'key_functions':[]}
        
        with open(tupu_wenjian,'r',encoding='utf-8')as f:
            tupu=json.load(f)
        
        #提取关键类和函数
        lei=[]
        hanshu=[]
        for jiedian_id, shuju in tupu.get('nodes',{}).items():
            if shuju.get('type')=='class':
                lei.append({'name':shuju['name'],'file':shuju['file'],
                           'doc':shuju.get('docstring','')[:80]})
            elif shuju.get('type')=='function':
                hanshu.append({'name':shuju['name'],'file':shuju['file'],
                              'doc':shuju.get('docstring','')[:80]})
        
        return {
            'total_nodes':len(tupu.get('nodes',{})),
            'key_classes':lei[:20],
            'key_functions':hanshu[:30]
        }
    
    def _shengcheng_claude_skill(self, jiyi: list, tupu: dict)->str:
        """生成Claude Code Skill格式"""
        neirong=['# CogniForge Memory Context\n']
        neirong.append(f'> 自动同步于 {datetime.now().isoformat()}\n')
        neirong.append(f'> 项目：{self.xiangmu_lujing.name}\n\n')
        
        neirong.append('## 项目关键决策与知识\n')
        for j in jiyi[:15]:
            neirong.append(f'- [{j["type"]}/{j["topic"]}] {j["content"][:150]}\n')
        
        if tupu.get('key_classes'):
            neirong.append('\n## 核心类\n')
            for lei in tupu['key_classes'][:10]:
                neirong.append(f'- `{lei["name"]}` → {lei["file"]}\n')
                if lei.get('doc'):
                    neirong.append(f'  {lei["doc"]}\n')
        
        if tupu.get('key_functions'):
            neirong.append('\n## 关键函数\n')
            for hs in tupu['key_functions'][:10]:
                neirong.append(f'- `{hs["name"]}()` → {hs["file"]}\n')
        
        neirong.append('\n> 运行 `cogniforge sync` 更新此文件\n')
        return ''.join(neirong)
    
    def _shengcheng_cursor_rule(self, jiyi: list, tupu: dict)->str:
        """生成Cursor Rule格式"""
        neirong=['---\ndescription: CogniForge项目上下文（自动生成）\nglobs: "**/*.py"\nalwaysApply: true\n---\n\n']
        neirong.append(f'# 项目上下文（CogniForge 同步于 {datetime.now().strftime("%Y-%m-%d %H:%M")}）\n\n')
        
        neirong.append('## 架构决策\n')
        juece_jiyi=[j for j in jiyi if j['type']=='架构决策']
        for j in juece_jiyi[:10]:
            neirong.append(f'- {j["content"][:200]}\n')
        
        neirong.append('\n## 代码规范与模式\n')
        moshi_jiyi=[j for j in jiyi if j['type']=='代码模式']
        for j in moshi_jiyi[:10]:
            neirong.append(f'- {j["content"][:200]}\n')
        
        if tupu.get('key_classes'):
            neirong.append('\n## 项目结构\n')
            for lei in tupu['key_classes'][:8]:
                neirong.append(f'- `{lei["name"]}` @ {lei["file"]}\n')
        
        return ''.join(neirong)
    
    def _shengcheng_copilot_zhiling(self, jiyi: list, tupu: dict)->str:
        """生成GitHub Copilot指令格式"""
        neirong=['\n<!-- COGNIFORGE_CONTEXT_START -->\n']
        neirong.append(f'<!-- CogniForge Auto-Sync: {datetime.now().isoformat()} -->\n\n')
        neirong.append('## Project Context (from CogniForge)\n\n')
        
        neirong.append('### Architecture Decisions\n')
        juece=[j for j in jiyi if j['type'] in('架构决策','architecture')]
        for j in juece[:8]:
            neirong.append(f'- {j["content"][:200]}\n')
        
        neirong.append('\n### Code Patterns\n')
        moshi=[j for j in jiyi if j['type'] in('代码模式','patterns')]
        for j in moshi[:8]:
            neirong.append(f'- {j["content"][:200]}\n')
        
        neirong.append('\n### Key Components\n')
        for lei in tupu.get('key_classes',[])[:10]:
            neirong.append(f'- `{lei["name"]}` ({lei["file"]})\n')
        
        neirong.append('\n<!-- COGNIFORGE_CONTEXT_END -->\n')
        return ''.join(neirong)
    
    def shengcheng_mcp_fuwu(self, duankou: int=8765):
        """启动MCP服务（简化版）"""
        from .core.memory_engine import jiyigongdian
        from .core.knowledge_graph import zhishitupu
        from .core.context_compressor import shangxiawen_yasuo
        
        jiyi=jiyigongdian(str(self.xiangmu_lujing))
        tupu=zhishitupu(str(self.xiangmu_lujing))
        yasuo=shangxiawen_yasuo(str(self.xiangmu_lujing))
        
        #构建MCP工具描述
        gongju_miaoshu={
            'cogniforge_remember':{
                'description':'记录一条新的项目记忆',
                'inputSchema':{
                    'type':'object',
                    'properties':{
                        'content':{'type':'string','description':'记忆内容'},
                        'topic':{'type':'string','description':'主题'},
                        'hall_type':{'type':'string','description':'类型：decisions/patterns/knowledge/fixes/context'}
                    }
                }
            },
            'cogniforge_recall':{
                'description':'搜索召回相关记忆',
                'inputSchema':{
                    'type':'object',
                    'properties':{
                        'query':{'type':'string','description':'搜索关键词'},
                        'limit':{'type':'integer','description':'最大返回数'}
                    }
                }
            },
            'cogniforge_context':{
                'description':'获取项目压缩上下文',
                'inputSchema':{
                    'type':'object',
                    'properties':{
                        'level':{'type':'integer','description':'1=摘要 2=结构 3=细节'},
                        'focus_files':{'type':'array','items':{'type':'string'}}
                    }
                }
            },
            'cogniforge_search_code':{
                'description':'搜索代码库中的函数/类/模块',
                'inputSchema':{
                    'type':'object',
                    'properties':{
                        'query':{'type':'string','description':'搜索关键词'}
                    }
                }
            }
        }
        
        return {'port':duankou,'tools':gongju_miaoshu,'status':'ready'}
