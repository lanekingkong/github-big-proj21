# CogniForge CLI - 命令行入口
#借鉴Typer+Rich，支持丰富的终端交互

import typer, json, sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich import print as rprint

app=typer.Typer(
    name='cogniforge',
    help='AI时代开发者认知增强引擎 - 记忆宫殿 · 知识图谱 · 上下文压缩 · 跨工具同步',
    no_args_is_help=True
)

kz=Console()

#子命令组
jiyi_app=typer.Typer(help='记忆宫殿操作')
app.add_typer(jiyi_app,name='memory')

tupu_app=typer.Typer(help='知识图谱操作')
app.add_typer(tupu_app,name='graph')

tongbu_app=typer.Typer(help='跨工具同步操作')
app.add_typer(tongbu_app,name='sync')

suoyin_app=typer.Typer(help='索引与上下文')
app.add_typer(suoyin_app,name='index')

def _huode_xiangmu_lujing(mulu: str='.')->Path:
    """获取项目根路径"""
    return Path(mulu).resolve()

#记忆命令
@jiyi_app.command('remember')
def jiyi_jilu(
    neirong: str=typer.Argument(...,help='要记录的记忆内容'),
    zhuti: str=typer.Option('general','-t','--topic',help='记忆主题'),
    yi: str=typer.Option('default','-w','--wing',help='所属翼（分区）'),
    leixing: str=typer.Option('knowledge','-H','--hall',help='记忆类型：decisions/patterns/knowledge/fixes/context'),
    biaoqian: Optional[str]=typer.Option(None,'--tags',help='标签，逗号分隔'),
    mulu: str=typer.Option('.','-d','--dir',help='项目目录')
):
    """记录一条新记忆"""
    from .core.memory_engine import jiyigongdian
    
    bq_liebiao=biaoqian.split(',')if biaoqian else[]
    jiyi=jiyigongdian(mulu)
    jiyi_id=jiyi.jilu(neirong,zhuti,yi,leixing,bq_liebiao)
    kz.print(f'[green]✓ 记忆已记录[/green] ID: {jiyi_id}')

@jiyi_app.command('recall')
def jiyi_huiqu(
    chaxun: str=typer.Argument('',help='搜索关键词（空则全部）'),
    yi: str=typer.Option('','--wing',help='过滤翼'),
    leixing: str=typer.Option('','--hall',help='过滤走廊类型'),
    xianzhi: int=typer.Option(10,'--limit','-l',help='最大结果数'),
    mulu: str=typer.Option('.','-d','--dir',help='项目目录')
):
    """召回记忆"""
    from .core.memory_engine import jiyigongdian
    
    jiyi=jiyigongdian(mulu)
    jieguo=jiyi.huiqu(chaxun,yi,leixing,xianzhi)
    
    if not jieguo:
        kz.print('[yellow]未找到相关记忆[/yellow]')
        return
    
    biao=Table(title=f'记忆召回 ({len(jieguo)}条)')
    biao.add_column('时间',style='dim')
    biao.add_column('翼/房间',style='cyan')
    biao.add_column('内容',style='white')
    biao.add_column('标签',style='yellow')
    
    for j in jieguo:
        shijian=j['timestamp'][:19]if j.get('timestamp')else''
        weizhi=f"{j['wing']}/{j['room']}"
        biao.add_row(shijian,weizhi,j['content'][:100],','.join(j.get('tags',[])))
    
    kz.print(biao)

@jiyi_app.command('stats')
def jiyi_tongji(
    mulu: str=typer.Option('.','-d','--dir',help='项目目录')
):
    """记忆统计"""
    from .core.memory_engine import jiyigongdian
    
    jiyi=jiyigongdian(mulu)
    tongji=jiyi.tongji()
    
    kz.print(Panel(f'总记忆数: {tongji["total_memories"]} | 翼数: {tongji["wings_count"]}',
                   title='记忆宫殿统计'))
    for lx, sl in tongji['by_hall'].items():
        kz.print(f'  [cyan]{lx}[/cyan]: {sl}条')

@jiyi_app.command('consolidate')
def jiyi_gonggu(
    jiange: float=typer.Option(24.0,'--interval',help='最小间隔小时'),
    mulu: str=typer.Option('.','-d','--dir',help='项目目录')
):
    """记忆巩固"""
    from .core.memory_engine import jiyigongdian
    
    jiyi=jiyigongdian(mulu)
    hebing=jiyi.gonggu_jiyi(jiange)
    kz.print(f'[green]记忆巩固完成[/green] 合并了 {hebing} 条重复记忆')

#知识图谱命令
@tupu_app.command('build')
def tupu_goujian(
    mulu: str=typer.Option('.','-d','--dir',help='项目目录'),
    paichu: Optional[str]=typer.Option(None,'--exclude',help='排除目录，逗号分隔')
):
    """构建代码知识图谱索引"""
    from .core.knowledge_graph import zhishitupu
    
    paichu_liebiao=paichu.split(',')if paichu else None
    
    with Progress()as jindu:
        jindu.add_task('构建知识图谱...',total=None)
        tupu=zhishitupu(mulu)
        tongji=tupu.goujian_suoyin(paichu_liebiao)
    
    kz.print('[green]✓ 知识图谱构建完成[/green]')
    kz.print(f'节点: {tongji["total_nodes"]} | 边: {tongji["total_edges"]} | 文件: {tongji["files_indexed"]}')
    for lx, sl in tongji['node_types'].items():
        kz.print(f'  [cyan]{lx}[/cyan]: {sl}')

@tupu_app.command('search')
def tupu_sousuo(
    chaxun: str=typer.Argument(...,help='搜索关键词'),
    leixing: str=typer.Option('','-t','--type',help='过滤类型：file/class/function'),
    mulu: str=typer.Option('.','-d','--dir',help='项目目录')
):
    """搜索知识图谱"""
    from .core.knowledge_graph import zhishitupu
    
    tupu=zhishitupu(mulu)
    tupu.jiazai()
    jieguo=tupu.chaxun(chaxun,leixing)
    
    if not jieguo:
        kz.print('[yellow]未找到匹配实体[/yellow]')
        return
    
    for j in jieguo:
        biaoji={'class':'[cyan]class[/cyan]','function':'[green]def[/green]',
                'file':'[yellow]file[/yellow]'}.get(j['type'],j['type'])
        kz.print(f'{biaoji} [bold]{j["name"]}[/bold] @ {j.get("file","?")}:{j.get("line","?")}')
        if j.get('docstring'):
            kz.print(f'  {j["docstring"][:120]}',style='dim')

@tupu_app.command('related')
def tupu_xiangguan(
    jiedian_id: str=typer.Argument(...,help='节点ID'),
    mulu: str=typer.Option('.','-d','--dir',help='项目目录')
):
    """查看节点关联实体"""
    from .core.knowledge_graph import zhishitupu
    
    tupu=zhishitupu(mulu)
    tupu.jiazai()
    xiangguan=tupu.huode_xiangguan(jiedian_id)
    
    kz.print(f'[bold]节点: {jiedian_id}[/bold]')
    kz.print(f'\n[cyan]出边 ({len(xiangguan["outgoing"])}):[/cyan]')
    for x in xiangguan['outgoing'][:20]:
        kz.print(f'  → {x["target"]} ({x["type"]})')
    
    kz.print(f'\n[cyan]入边 ({len(xiangguan["incoming"])}):[/cyan]')
    for x in xiangguan['incoming'][:20]:
        kz.print(f'  ← {x["source"]} ({x["type"]})')

#同步命令
@tongbu_app.command('to')
def tongbu_dao(
    gongju: str=typer.Argument(...,help='目标工具：claude/cursor/copilot'),
    mulu: str=typer.Option('.','-d','--dir',help='项目目录')
):
    """同步到指定AI工具"""
    from .core.sync_bridge import tongbqiaojie
    
    qiaojie=tongbqiaojie(mulu)
    jieguo=qiaojie.tongbu_dao_gongju(gongju)
    
    if'error'in jieguo:
        kz.print(f'[red]错误: {jieguo["error"]}[/red]')
        kz.print(f'支持的工具: {", ".join(jieguo["supported"])}')
        return
    
    kz.print(f'[green]✓ 已同步到 {gongju}[/green]')
    kz.print(f'文件: {jieguo["file"]}')
    kz.print(f'记忆: {jieguo.get("memories",0)}条 | 图谱节点: {jieguo.get("graph_nodes",0)}')

@tongbu_app.command('all')
def tongbu_suoyou(
    mulu: str=typer.Option('.','-d','--dir',help='项目目录')
):
    """同步到所有支持的AI工具"""
    from .core.sync_bridge import tongbqiaojie
    
    qiaojie=tongbqiaojie(mulu)
    jieguo=qiaojie.tongbu_suoyou()
    
    biao=Table(title='同步结果')
    biao.add_column('工具',style='cyan')
    biao.add_column('状态',style='green')
    biao.add_column('记忆数')
    biao.add_column('文件')
    
    for j in jieguo:
        zhuangtai='✓' if'error'not in j else'✗'
        biao.add_row(j.get('tool','?'),zhuangtai,
                     str(j.get('memories',0)),
                     str(j.get('file','')))
    
    kz.print(biao)

#索引与上下文命令
@suoyin_app.command('context')
def huode_shangxiawen(
    jibie: int=typer.Option(2,'-l','--level',help='1=摘要 2=结构 3=细节'),
    jiaodian: Optional[str]=typer.Option(None,'-f','--focus',help='焦点文件，逗号分隔'),
    mulu: str=typer.Option('.','-d','--dir',help='项目目录')
):
    """获取压缩上下文"""
    from .core.context_compressor import shangxiawen_yasuo
    
    jiaodian_liebiao=jiaodian.split(',')if jiaodian else None
    yasuo=shangxiawen_yasuo(mulu)
    shangxiawen=yasuo.huode_shangxiawen(jibie,jiaodian_liebiao)
    
    kz.print(shangxiawen)

@suoyin_app.command('tree')
def xianshi_mulushu(
    shendu: int=typer.Option(3,'-d','--depth',help='最大深度'),
    mulu: str=typer.Option('.','--dir',help='项目目录')
):
    """显示项目目录树"""
    from .core.context_compressor import shangxiawen_yasuo
    
    yasuo=shangxiawen_yasuo(mulu)
    kz.print(yasuo._shengcheng_mulushu(zuida_shendu=shendu))

@app.command('version')
def banben():
    """显示版本"""
    kz.print('[bold cyan]CogniForge[/bold cyan] v0.1.0')
    kz.print('AI时代开发者认知增强引擎')

@app.command('init')
def chushihua(
    mulu: str=typer.Argument('.',help='项目目录'),
    qiangzhi: bool=typer.Option(False,'--force','-f',help='强制重新初始化')
):
    """初始化项目CogniForge配置"""
    xiangmu_lujing=Path(mulu).resolve()
    cunchujing=xiangmu_lujing/'.cogniforge'
    
    if cunchujing.exists() and not qiangzhi:
        kz.print(f'[yellow]项目已初始化 (.cogniforge 已存在)[/yellow]')
        kz.print(f'使用 --force 强制重新初始化')
        return
    
    cunchujing.mkdir(parents=True,exist_ok=True)
    
    #创建初始配置
    chushi_peizhi={
        'version':'0.1.0',
        'created':datetime.now().isoformat(),
        'project':str(xiangmu_lujing),
        'auto_sync':False,
        'sync_interval_hours':24,
        'context_level':2
    }
    
    with open(cunchujing/'config.json','w',encoding='utf-8')as f:
        json.dump(chushi_peizhi,f,indent=2,ensure_ascii=False)
    
    kz.print(f'[green]✓ CogniForge 初始化完成[/green]')
    kz.print(f'存储目录: {cunchujing}')
    kz.print(f'接下来运行: cogniforge memory remember "项目架构选型为..."')

def main():
    app()

if __name__=='__main__':
    main()
