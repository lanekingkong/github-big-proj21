"""
CogniForge 使用示例

示例1: 初始化并记录项目记忆
"""
def shili_1_jiben_liucheng():
    """基本使用流程"""
    from src.core.memory_engine import jiyigongdian
    from src.core.context_compressor import shangxiawen_yasuo
    
    xiangmu='./my_project'
    
    #1. 初始化记忆宫殿
    jiyi=jiyigongdian(xiangmu)
    
    #2. 记录架构决策
    jiyi.jilu(
        '选择FastAPI作为Web框架，因为其异步支持和自动API文档',
        'Web框架选型',
        yi_ming='backend',
        zoulang_leixing='decisions',
        biaoqian=['FastAPI','架构','Python']
    )
    
    jiyi.jilu(
        '数据库采用PostgreSQL + SQLAlchemy ORM，利用迁移工具Alembic',
        '数据库选型',
        yi_ming='backend',
        zoulang_leixing='decisions',
        biaoqian=['PostgreSQL','ORM']
    )
    
    #3. 记录代码模式
    jiyi.jilu(
        'Repository模式：所有数据访问通过Repository类，业务逻辑层不直接操作ORM',
        'Repository模式',
        yi_ming='backend',
        zoulang_leixing='patterns'
    )
    
    #4. 召回记忆
    print('= 所有架构决策 =')
    for j in jiyi.huiqu(zoulang_leixing='decisions'):
        print(f"  [{j['wing']}/{j['room']}] {j['content'][:100]}")
    
    #5. 获取压缩上下文
    yasuo=shangxiawen_yasuo(xiangmu)
    print('\n= 项目摘要 =')
    print(yasuo.huode_shangxiawen(jibie=1))


"""
示例2: 构建代码知识图谱
"""
def shili_2_zhishi_tupu():
    """知识图谱示例"""
    from src.core.knowledge_graph import zhishitupu
    
    xiangmu='./my_project'
    tupu=zhishitupu(xiangmu)
    
    #构建索引
    tongji=tupu.goujian_suoyin()
    print(f'节点: {tongji["total_nodes"]}, 边: {tongji["total_edges"]}')
    
    #搜索
    jieguo=tupu.chaxun('Repository')
    for j in jieguo:
        print(f'{j["type"]}: {j["name"]} @ {j["file"]}:{j["line"]}')


"""
示例3: 跨工具同步
"""
def shili_3_kuagongju_tongbu():
    """跨工具同步示例"""
    from src.core.sync_bridge import tongbqiaojie
    
    xiangmu='./my_project'
    qiaojie=tongbqiaojie(xiangmu)
    
    #同步到Claude Code
    jieguo=qiaojie.tongbu_dao_gongju('claude')
    print(f'Claude同步: {jieguo["file"]}')
    
    #同步到Cursor
    jieguo=qiaojie.tongbu_dao_gongju('cursor')
    print(f'Cursor同步: {jieguo["file"]}')
    
    #同步到Copilot
    jieguo=qiaojie.tongbu_dao_gongju('copilot')
    print(f'Copilot同步: {jieguo["file"]}')


if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='1':
        shili_1_jiben_liucheng()
    elif len(sys.argv)>1 and sys.argv[1]=='2':
        shili_2_zhishi_tupu()
    elif len(sys.argv)>1 and sys.argv[1]=='3':
        shili_3_kuagongju_tongbu()
    else:
        print('CogniForge 示例: python examples/usage.py [1|2|3]')
