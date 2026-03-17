# Emplyment

`Emplyment/` 是一个和主项目解耦的最小就业分析工具。

它刻意不复用 BettaFish 那套较重的前后端、任务流、SSE、报告引擎，只保留一个最短闭环：

- 输入一个就业问题
- 可选输入用户画像
- 先做信息检索
- 再走轻量三角色协作
- 最后生成一份 Markdown 报告
- 默认保存到 `Emplyment/reports/`

## 当前内部流程

这个版本已经不是单个 LLM 直接输出，而是一个轻量的多角色流程：

1. `Researcher`
   负责信息检索和证据整理
2. `Analyst`
   负责把检索结果转成结构化判断
3. `Advisor`
   负责给出最终就业分析和行动建议

检索层参考了原项目 `QueryEngine/tools/search.py` 的思路：

- 把搜索封装成轻量工具层
- 先生成多条查询词
- 聚合搜索结果
- 把检索证据传给后续角色

如果配置了 `TAVILY_API_KEY` 或 `EMPLOYMENT_SEARCH_API_KEY`，会优先使用真实搜索。
如果搜索不可用，会自动退回本地证据模式，保证整体流程仍然可跑。

## 适合的场景

- 就业行情分析
- 岗位方向判断
- 城市机会对比
- 初步求职指导
- 转行准备建议

## 快速使用

在项目根目录运行：

```bash
python -m Emplyment.cli "2026 年杭州算法岗就业行情如何"
```

求职指导示例：

```bash
python -m Emplyment.cli "我是统计学本科，想去深圳找数据分析工作，应该怎么准备" --mode guidance
```

带用户画像：

```bash
python -m Emplyment.cli "我适合投什么数据岗位" \
  --mode guidance \
  --profile-json '{"education":"统计学本科","internship":"电商运营实习","skills":["Python","SQL","Tableau"]}'
```

## 配置方式

会自动读取项目根目录 `.env`。

优先读取这些变量：

- `EMPLOYMENT_API_KEY`
- `EMPLOYMENT_BASE_URL`
- `EMPLOYMENT_MODEL_NAME`

如果没配，会自动回退到：

- `REPORT_ENGINE_API_KEY`
- `REPORT_ENGINE_BASE_URL`
- `REPORT_ENGINE_MODEL_NAME`

再回退到：

- `QUERY_ENGINE_API_KEY`
- `QUERY_ENGINE_BASE_URL`
- `QUERY_ENGINE_MODEL_NAME`

搜索优先读取：

- `EMPLOYMENT_SEARCH_API_KEY`
- `TAVILY_API_KEY`

可选配置：

- `EMPLOYMENT_SEARCH_PROVIDER`
- `EMPLOYMENT_MAX_SEARCH_RESULTS`
- `EMPLOYMENT_SEARCH_TIMEOUT_SECONDS`

## 没有 API 也能运行吗

可以。

如果没有可用的 LLM 配置，或外部网络暂时不可用，工具会自动退回本地规则模式。

此时依然会执行：

- 查询词规划
- 轻量检索证据生成
- 三角色协作
- Markdown 报告输出

## 当前设计原则

- 小而独立
- 不绑定主站
- 不启动 Flask / Streamlit
- 不依赖复杂任务编排
- 先解决“够用”，再考虑“完备”
