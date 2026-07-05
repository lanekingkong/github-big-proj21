# CogniForge 向量存储（基于LanceDB）
#支持语义搜索记忆

import os, json
from pathlib import Path
from typing import Optional

class VectorStore:
    """LanceDB向量存储封装
    
    用于记忆的语义搜索，支持：
    - 自动嵌入（sentence-transformers）
    - 增量索引
    - Top-K相似度搜索
    """
    
    def __init__(self, cunchujing_lujing: str):
        self.cunchu=Path(cunchujing_lujing)
        self.cunchu.mkdir(parents=True,exist_ok=True)
        self.lancedb_lujing=self.cunchu/'vectors.lance'
        self._db=None
        self._biao=None
        self._embedder=None
    
    def _huoqu_embedder(self):
        """懒加载嵌入模型"""
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder=SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                raise ImportError('需要安装sentence-transformers: pip install sentence-transformers')
        return self._embedder
    
    def _huoqu_db(self):
        """懒加载数据库连接"""
        if self._db is None:
            try:
                import lancedb
                self._db=lancedb.connect(str(self.lancedb_lujing))
            except ImportError:
                raise ImportError('需要安装lancedb: pip install lancedb')
        return self._db
    
    def suoyin_wenben(self, wenben_liebiao: list, yuanshuju_liebiao: list=None,
                      biao_ming: str='memories')->int:
        """索引文本列表
        
        返回：已索引数量
        """
        embedder=self._huoqu_embedder()
        xiangliang=embedder.encode(wenben_liebiao,show_progress_bar=False)
        
        db=self._huoqu_db()
        
        shuju=[]
        for i, (wenben, vec)in enumerate(zip(wenben_liebiao, xiangliang)):
            tiaomu={'id':str(i),'text':wenben,'vector':vec.tolist()}
            if yuanshuju_liebiao and i<len(yuanshuju_liebiao):
                tiaomu['metadata']=json.dumps(yuanshuju_liebiao[i],ensure_ascii=False)
            shuju.append(tiaomu)
        
        #LanceDB写入
        import pyarrow as pa
        biao_jiegou=pa.schema([
            pa.field('id',pa.string()),
            pa.field('text',pa.string()),
            pa.field('vector',pa.list_(pa.float32(),384)),
            pa.field('metadata',pa.string())
        ])
        
        if biao_ming in db.table_names():
            db.drop_table(biao_ming)
        
        self._biao=db.create_table(biao_ming,shuju,schema=biao_jiegou)
        return len(shuju)
    
    def search(self, chaxun: str, top_k: int=5, biao_ming: str='memories')->list:
        """语义搜索"""
        embedder=self._huoqu_embedder()
        chaxun_vec=embedder.encode([chaxun],show_progress_bar=False)[0]
        
        db=self._huoqu_db()
        
        try:
            biao=db.open_table(biao_ming)
            jieguo=biao.search(chaxun_vec.tolist()).limit(top_k).to_list()
            
            #格式化返回
            geshihua=[]
            for r in jieguo:
                tiaomu={'text':r['text'],'_distance':r.get('_distance',0)}
                if r.get('metadata'):
                    try:
                        tiaomu.update(json.loads(r['metadata']))
                    except json.JSONDecodeError:
                        pass
                geshihua.append(tiaomu)
            return geshihua
        except Exception:
            return []  #表不存在或LanceDB不可用
    
    def shanchu_biao(self, biao_ming: str):
        """删除指定表"""
        db=self._huoqu_db()
        if biao_ming in db.table_names():
            db.drop_table(biao_ming)
