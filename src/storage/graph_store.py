# CogniForge 图谱持久化存储

import json, sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

class tupu_cunchu:
    """基于SQLite的知识图谱持久化存储
    
    支持：
    - 节点CRUD
    - 边CRUD
    - 批量导入导出
    - 版本快照
    """
    
    def __init__(self, cunchujing_lujing: str):
        self.cunchu=Path(cunchujing_lujing)
        self.cunchu.mkdir(parents=True,exist_ok=True)
        self.db_lujing=self.cunchu/'graph.db'
        self._chushihua()
    
    def _chushihua(self):
        """初始化数据库表结构"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS nodes(
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    properties TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS edges(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    properties TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(source_id) REFERENCES nodes(id),
                    FOREIGN KEY(target_id) REFERENCES nodes(id)
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS snapshots(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    data TEXT NOT NULL
                )
            ''')
            #索引
            conn.execute('CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id)')
            conn.commit()
    
    def tianjia_jiedian(self, jiedian_id: str, leixing: str, mingcheng: str,
                        shuxing: dict=None)->bool:
        """添加或更新节点"""
        shuxing_json=json.dumps(shuxing or {},ensure_ascii=False)
        with sqlite3.connect(str(self.db_lujing))as conn:
            conn.execute('''
                INSERT OR REPLACE INTO nodes(id,type,name,properties,updated_at)
                VALUES(?,?,?,?,?)
            ''',(jiedian_id,leixing,mingcheng,shuxing_json,datetime.now().isoformat()))
            conn.commit()
        return True
    
    def tianjia_bian(self, laiyuan_id: str, mubiao_id: str,
                     leixing: str, shuxing: dict=None)->int:
        """添加关系边，返回边ID"""
        shuxing_json=json.dumps(shuxing or {},ensure_ascii=False)
        with sqlite3.connect(str(self.db_lujing))as conn:
            youbiao=conn.execute('''
                INSERT INTO edges(source_id,target_id,type,properties)
                VALUES(?,?,?,?)
            ''',(laiyuan_id,mubiao_id,leixing,shuxing_json))
            conn.commit()
            return youbiao.lastrowid
    
    def chaxun_jiedian(self, leixing: str='', sousuo_ci: str='')->list:
        """查询节点"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            tiaojian=[]
            canshu=[]
            if leixing:
                tiaojian.append('type=?')
                canshu.append(leixing)
            if sousuo_ci:
                tiaojian.append('name LIKE ?')
                canshu.append(f'%{sousuo_ci}%')
            
            sql='SELECT id,type,name,properties,created_at FROM nodes'
            if tiaojian:
                sql+=' WHERE '+' AND '.join(tiaojian)
            
            jieguo=conn.execute(sql, canshu).fetchall()
            return [{'id':r[0],'type':r[1],'name':r[2],
                     'properties':json.loads(r[3]),'created_at':r[4]}for r in jieguo]
    
    def chaxun_bian(self, laiyuan_id: str='', mubiao_id: str='', leixing: str='')->list:
        """查询关系边"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            tiaojian=[]
            canshu=[]
            if laiyuan_id:
                tiaojian.append('source_id=?')
                canshu.append(laiyuan_id)
            if mubiao_id:
                tiaojian.append('target_id=?')
                canshu.append(mubiao_id)
            if leixing:
                tiaojian.append('type=?')
                canshu.append(leixing)
            
            sql='SELECT id,source_id,target_id,type,properties FROM edges'
            if tiaojian:
                sql+=' WHERE '+' AND '.join(tiaojian)
            
            jieguo=conn.execute(sql, canshu).fetchall()
            return [{'id':r[0],'source':r[1],'target':r[2],
                     'type':r[3],'properties':json.loads(r[4])}for r in jieguo]
    
    def kuaizhao(self, miaoshu: str='')->int:
        """创建当前状态的完整快照"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            jiedian=conn.execute('SELECT * FROM nodes').fetchall()
            bian=conn.execute('SELECT * FROM edges').fetchall()
            
            shuju={
                'nodes':[{'id':n[0],'type':n[1],'name':n[2],
                         'properties':json.loads(n[3]),'created_at':n[4],
                         'updated_at':n[5]}for n in jiedian],
                'edges':[{'id':e[0],'source':e[1],'target':e[2],
                         'type':e[3],'properties':json.loads(e[4]),
                         'created_at':e[5]}for e in bian]
            }
            
            jieguo=conn.execute('''
                INSERT INTO snapshots(description,data) VALUES(?,?)
            ''',(miaoshu,json.dumps(shuju,ensure_ascii=False)))
            conn.commit()
            return jieguo.lastrowid
    
    def huifu_kuaizhao(self, kuaizhao_id: int)->bool:
        """从快照恢复"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            kuaizhao=conn.execute(
                'SELECT data FROM snapshots WHERE id=?',(kuaizhao_id,)
            ).fetchone()
            if not kuaizhao:
                return False
            
            shuju=json.loads(kuaizhao[0])
            
            #清空现有数据
            conn.execute('DELETE FROM edges')
            conn.execute('DELETE FROM nodes')
            
            #恢复节点
            for jiedian in shuju['nodes']:
                conn.execute('''
                    INSERT INTO nodes(id,type,name,properties,created_at,updated_at)
                    VALUES(?,?,?,?,?,?)
                ''',(jiedian['id'],jiedian['type'],jiedian['name'],
                     json.dumps(jiedian['properties'],ensure_ascii=False),
                     jiedian['created_at'],jiedian.get('updated_at','')))
            
            #恢复边
            for bian in shuju['edges']:
                conn.execute('''
                    INSERT INTO edges(source_id,target_id,type,properties,created_at)
                    VALUES(?,?,?,?,?)
                ''',(bian['source'],bian['target'],bian['type'],
                     json.dumps(bian['properties'],ensure_ascii=False),
                     bian.get('created_at','')))
            
            conn.commit()
        return True
    
    def tongji(self)->dict:
        """获取存储统计"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            jiedian_shu=conn.execute('SELECT COUNT(*) FROM nodes').fetchone()[0]
            bian_shu=conn.execute('SELECT COUNT(*) FROM edges').fetchone()[0]
            kuaizhao_shu=conn.execute('SELECT COUNT(*) FROM snapshots').fetchone()[0]
        return {
            'nodes':jiedian_shu,
            'edges':bian_shu,
            'snapshots':kuaizhao_shu,
            'db_size':self.db_lujing.stat().st_size if self.db_lujing.exists() else 0
        }
