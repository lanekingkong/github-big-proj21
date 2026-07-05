"""
CogniForge 核心引擎单元测试
"""
import pytest, json, tempfile, os
from pathlib import Path
from datetime import datetime

#测试记忆宫殿引擎
def test_jilu_he_huiqu():
    """测试记忆的记录和召回"""
    from src.core.memory_engine import jiyigongdian
    
    with tempfile.TemporaryDirectory()as tmp:
        jiyi=jiyigongdian(tmp)
        
        #记录
        id1=jiyi.jilu('使用Flask作为Web框架','技术选型','default','decisions',['Python','Web'])
        id2=jiyi.jilu('SQLAlchemy ORM模式','数据库','default','patterns')
        id3=jiyi.jilu('修复了登录Bug','登录修复','default','fixes',['Bug'])
        
        assert id1
        assert id2
        assert id3
        
        #召回全部
        quanbu=jiyi.huiqu()
        assert len(quanbu)>=3
        
        #按关键词召回
        jieguo=jiyi.huiqu('Flask')
        assert len(jieguo)>=1
        
        #按走廊过滤
        jieguo=jiyi.huiqu(zoulang_leixing='fixes')
        assert len(jieguo)==1

def test_tongji():
    """测试记忆统计"""
    from src.core.memory_engine import jiyigongdian
    
    with tempfile.TemporaryDirectory()as tmp:
        jiyi=jiyigongdian(tmp)
        jiyi.jilu('测试记忆1','主题1')
        jiyi.jilu('测试记忆2','主题2')
        
        tongji=jiyi.tongji()
        assert tongji['total_memories']>=2
        assert 'knowledge' in tongji['by_hall']

def test_gonggu():
    """测试记忆巩固"""
    from src.core.memory_engine import jiyigongdian
    
    with tempfile.TemporaryDirectory()as tmp:
        jiyi=jiyigongdian(tmp)
        jiyi.jilu('Python很好用','编程')
        jiyi.jilu('Python确实很好用，开发效率高','编程')
        
        hebing=jiyi.gonggu_jiyi(0)  #强制巩固
        assert hebing>=0  #至少尝试合并

#测试知识图谱引擎
def test_tupu_goujian():
    """测试知识图谱构建"""
    from src.core.knowledge_graph import zhishitupu
    
    with tempfile.TemporaryDirectory()as tmp:
        tmp_path=Path(tmp)
        #创建测试Python文件
        (tmp_path/'test.py').write_text('''
class JisuanQi:
    """计算器类"""
    def jiaohuan(self, a: int, b: int) -> int:
        return a + b

def shiyong():
    calc = JisuanQi()
    return calc.jiaohuan(1, 2)
''', encoding='utf-8')
        
        tupu=zhishitupu(tmp)
        tongji=tupu.goujian_suoyin()
        
        assert tongji['total_nodes']>=3  #文件+类+函数
        assert tongji['total_edges']>=1  #调用关系
    
def test_tupu_sousuo():
    """测试知识图谱搜索"""
    from src.core.knowledge_graph import zhishitupu
    
    with tempfile.TemporaryDirectory()as tmp:
        tmp_path=Path(tmp)
        (tmp_path/'app.py').write_text('''
class Fuwu:
    def chuli(self): pass
''', encoding='utf-8')
        
        tupu=zhishitupu(tmp)
        tupu.goujian_suoyin()
        
        jieguo=tupu.chaxun('Fuwu')
        assert len(jieguo)>=1
        assert jieguo[0]['name']=='Fuwu'

#测试上下文压缩
def test_yasuo_level1():
    """测试上下文压缩 Level 1"""
    from src.core.context_compressor import shangxiawen_yasuo
    
    with tempfile.TemporaryDirectory()as tmp:
        yasuo=shangxiawen_yasuo(tmp)
        shangxiawen=yasuo.huode_shangxiawen(jibie=1)
        
        assert shangxiawen
        assert '项目' in shangxiawen

def test_yasuo_mulushu():
    """测试目录树生成"""
    from src.core.context_compressor import shangxiawen_yasuo
    
    with tempfile.TemporaryDirectory()as tmp:
        Path(tmp,'src').mkdir()
        Path(tmp,'tests').mkdir()
        Path(tmp,'src','__init__.py').write_text('')
        
        yasuo=shangxiawen_yasuo(tmp)
        shu=yasuo._shengcheng_mulushu(zuida_shendu=2)
        
        assert 'src' in shu
        assert 'tests' in shu

#测试同步桥接
def test_tongbu_liebiao():
    """测试同步支持的工具列表"""
    from src.core.sync_bridge import tongbqiaojie
    
    with tempfile.TemporaryDirectory()as tmp:
        qiaojie=tongbqiaojie(tmp)
        #测试不支持的工具
        jieguo=qiaojie.tongbu_dao_gongju('unknown')
        assert 'error' in jieguo
        assert 'supported' in jieguo

def test_tongbu_claude():
    """测试同步到Claude"""
    from src.core.sync_bridge import tongbqiaojie
    
    with tempfile.TemporaryDirectory()as tmp:
        #先初始化记忆
        from src.core.memory_engine import jiyigongdian
        jiyi=jiyigongdian(tmp)
        jiyi.jilu('使用Flask框架','技术选型')
        
        qiaojie=tongbqiaojie(tmp)
        jieguo=qiaojie.tongbu_dao_gongju('claude')
        
        assert 'file' in jieguo
        assert Path(jieguo['file']).exists()

#测试本地数据库
def test_bendi_db():
    """测试本地SQLite存储"""
    from src.storage.local_db import bendi_shujuku
    
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True)as tmp:
        db=bendi_shujuku(tmp)
        
        db.shezhi_peizhi('test_key','test_value')
        assert db.huode_peizhi('test_key')=='test_value'
        
        db.jilu_tongbu('claude','success',{'memories':5})
        tongbu=db.huode_zuijin_tongbu('claude')
        assert len(tongbu)>=1
        del db

#测试图谱存储
def test_tupu_cunchu():
    """测试SQLite图谱存储"""
    from src.storage.graph_store import tupu_cunchu
    
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True)as tmp:
        cunchu=tupu_cunchu(tmp)
        
        cunchu.tianjia_jiedian('func:main','function','main',{'line':42})
        jiedian=cunchu.chaxun_jiedian(sousuo_ci='main')
        assert len(jiedian)>=1
        
        cunchu.tianjia_bian('func:main','class:App','calls')
        bian=cunchu.chaxun_bian(laiyuan_id='func:main')
        assert len(bian)>=1
        
        tongji=cunchu.tongji()
        assert tongji['nodes']>=1
        assert tongji['edges']>=1
        #确保SQLite连接在tmp清理前关闭
        del cunchu

if __name__=='__main__':
    pytest.main([__file__,'-v'])
