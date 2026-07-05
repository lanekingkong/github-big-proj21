# CogniForge 本地SQLite元数据存储

import sqlite3, json
from pathlib import Path
from datetime import datetime

class bendi_shujuku:
    """轻量级本地数据库
    
    存储项目元数据、配置、同步状态等
    """
    
    def __init__(self, cunchujing_lujing: str):
        self.cunchu=Path(cunchujing_lujing)
        self.cunchu.mkdir(parents=True,exist_ok=True)
        self.db_lujing=self.cunchu/'cogniforge.db'
        self._chushihua()
    
    def _chushihua(self):
        """初始化表结构"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS config(
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS sync_log(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    synced_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS version_history(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL,
                    description TEXT,
                    file_changes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS usage_stats(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                                    args TEXT,
                    duration_ms REAL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            conn.commit()
    
    def shezhi_peizhi(self, jian: str, zhi: str):
        """设置配置项"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            conn.execute('''
                INSERT OR REPLACE INTO config(key,value,updated_at)
                VALUES(?,?,?)
            ''',(jian,zhi,datetime.now().isoformat()))
            conn.commit()
    
    def huode_peizhi(self, jian: str, moren: str='')->str:
        """获取配置项"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            jieguo=conn.execute(
                'SELECT value FROM config WHERE key=?',(jian,)
            ).fetchone()
            return jieguo[0] if jieguo else moren
    
    def jilu_tongbu(self, gongju: str, zhuangtai: str, xiangqing: dict=None):
        """记录同步日志"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            conn.execute('''
                INSERT INTO sync_log(tool,status,details)
                VALUES(?,?,?)
            ''',(gongju,zhuangtai,json.dumps(xiangqing or {},ensure_ascii=False)))
            conn.commit()
    
    def huode_zuijin_tongbu(self, gongju: str='')->list:
        """获取最近的同步记录"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            if gongju:
                rows=conn.execute(
                    'SELECT tool,status,details,synced_at FROM sync_log WHERE tool=? ORDER BY synced_at DESC LIMIT 10',
                    (gongju,)
                ).fetchall()
            else:
                rows=conn.execute(
                    'SELECT tool,status,details,synced_at FROM sync_log ORDER BY synced_at DESC LIMIT 20'
                ).fetchall()
            return [{'tool':r[0],'status':r[1],
                     'details':json.loads(r[2]),'time':r[3]}for r in rows]
    
    def jilu_shiyong(self, mingling: str, canshu: str='', haoshi_ms: float=0):
        """记录使用统计"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            conn.execute('''
                INSERT INTO usage_stats(command,args,duration_ms)
                VALUES(?,?,?)
            ''',(mingling,canshu,haoshi_ms))
            conn.commit()
    
    def tianjia_banben(self, banben: str, miaoshu: str, wenjian_bianhua: dict=None):
        """记录版本历史"""
        with sqlite3.connect(str(self.db_lujing))as conn:
            conn.execute('''
                INSERT INTO version_history(version,description,file_changes)
                VALUES(?,?,?)
            ''',(banben,miaoshu,json.dumps(wenjian_bianhua or {},ensure_ascii=False)))
            conn.commit()
