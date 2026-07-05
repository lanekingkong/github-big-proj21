# Contributing to CogniForge

欢迎贡献！以下是参与 CogniForge 项目开发的指南。

## 开发环境搭建

```bash
git clone https://github.com/lanekingkong/cogniforge.git
cd cogniforge
pip install -e ".[dev]"
```

## 代码风格

- 遵循项目既有的拼音命名风格（`jiyigongdian`、`zhishitupu` 等）
- 类名用小写拼音，函数/方法名也用拼音下划线
- 赋值运算符 `=` 两边不加空格
- `#` 注释后不加空格，用口语化中文注释

## 提交 PR 流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 添加测试覆盖新功能
4. 确保所有测试通过 (`pytest tests/`)
5. 提交变更 (`git commit -m 'Add amazing feature'`)
6. 推送到分支 (`git push origin feature/amazing-feature`)
7. 创建 Pull Request

## 项目结构约定

- `src/core/` — 核心引擎，不依赖外部服务
- `src/storage/` — 数据持久化层
- `src/cli/` — 命令行接口
- `src/adapters/` — 外部适配器（预留）
- `skills_builtin/` — 内置 AI 技能（YAML 格式）

## 运行测试

```bash
# 运行全部测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_core.py -v
```

## 版本发布

遵循语义化版本 (SemVer)：MAJOR.MINOR.PATCH
- MAJOR: 不兼容的 API 变更
- MINOR: 向后兼容的新功能
- PATCH: 向后兼容的问题修复

## 许可证

MIT License - 贡献即表示你同意你的代码在同一许可证下发布。
