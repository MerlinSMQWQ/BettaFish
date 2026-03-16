# BettaFish 改造为“就业行情分析与就业指导系统”的分层方案

## 1. 文档目标

本文档的目标，不是直接修改 BettaFish 现有代码，而是基于当前项目结构，设计一套“新增一层”的扩展方案，把项目从“通用舆情分析系统”平滑演进为“就业行情分析与就业指导系统”。

核心原则如下：

- 尽量不破坏原有舆情分析能力。
- 优先复用已有 Agent、报告、流式任务、配置、日志等基础设施。
- 通过新增一层“就业领域编排层”来承接业务改造，而不是把现有模块硬改成只服务就业。
- 保留未来回退能力，让项目继续同时支持“泛舆情分析”和“就业场景分析”。

一句话概括：

> 最合理的做法，不是把 BettaFish 改成另一个系统，而是在 BettaFish 上面再加一个就业领域适配层，让原系统变成底座，让新层变成行业化外壳。


## 2. 为什么这个方向合理

### 2.1 就业行情本质上就是一种垂直舆情

“就业行情”并不只是招聘数量，也不只是薪资区间。它本质上是一个围绕就业市场形成的复合信息场，包含：

- 企业招聘需求
- 岗位技能要求
- 城市机会分布
- 行业景气波动
- 裁员与扩招动态
- 求职者情绪与反馈
- 企业雇主品牌口碑
- 实习、校招、社招政策变化
- 培训、转岗、考证等辅助决策信息

这些信息天然具备“舆情”属性：

- 有时效性
- 有多源异构性
- 有观点冲突
- 有噪音和误导
- 需要多角度综合判断

BettaFish 现在擅长做的事情恰好也是：

- 多源搜索
- 多 Agent 协作
- 多轮总结与反思
- 报告结构规划
- 最终生成成品报告

所以，就业场景不是偏题，而是现有系统非常自然的一种垂直落地。

### 2.2 当前项目的“通用性”已经足够强

从代码结构看，这个项目并不是把“微博舆情”写死在每个模块里，而是已经抽象出了一套较通用的流水线。

最重要的通用能力包括：

- `app.py` 负责统一启动、配置、状态管理、聚合接口。
- `QueryEngine/agent.py` 负责面向公开信息的深度搜索与总结。
- `MediaEngine/agent.py` 负责多模态搜索与理解。
- `InsightEngine/agent.py` 负责私有数据库检索、聚类抽样、情感分析。
- `ForumEngine/monitor.py` 负责多 Agent 协作日志的监控与论坛式互动。
- `ReportEngine/agent.py` 和 `ReportEngine/flask_interface.py` 负责模板选择、报告生成、任务流式推送、结果导出。

这意味着该项目真正的底座不是“某个具体舆情主题”，而是：

- 信息采集层
- 分析协作层
- 报告生产层

就业场景只需要把“分析对象”和“提示词语义”替换掉，就能借用这条链路。

### 2.3 就业指导比普通舆情更适合做多 Agent

就业问题通常不是单视角问题，而是多方博弈：

- 市场视角：哪些行业在涨，哪些在缩
- 企业视角：企业在招什么样的人
- 候选人视角：自己的背景与岗位是否匹配
- 区域视角：不同城市机会密度不同
- 风险视角：哪些岗位看似热，但实际不稳定
- 成长视角：应该补技能、转岗位还是换赛道

BettaFish 当前的多 Agent + Forum 协作机制，正适合把这些不同立场拆开分析，再在更高一层整合。


## 3. 结论先行：建议“新增一层”，不要直接改原系统

我非常赞同你提出的方向：最好另外加上一层，而不是直接改动原有代码。

这是当前最稳妥、也最工程化的路线。

### 3.1 为什么不建议直接改原有代码

如果直接在现有 `QueryEngine`、`MediaEngine`、`InsightEngine`、`ReportEngine` 内部大面积把“舆情”改成“就业”，会有几个问题：

- 原项目语义被污染，后续难以继续支持原本的舆情场景。
- Prompt、模板、工具选择逻辑会混在一起，维护成本大。
- 如果就业方向试错失败，回滚代价高。
- 测试与排障变难，因为你无法区分“底层能力退化”还是“新业务逻辑有问题”。

### 3.2 为什么加一层更好

新增一层之后，原系统继续作为底层引擎存在，而就业能力作为“业务编排层”出现。

这样做的好处：

- 原系统最小侵入。
- 新业务可以快速迭代 Prompt、模板、数据源而不动底座。
- 能做双模式运行：`generic_opinion_analysis` 与 `employment_market_analysis`。
- 后续还能继续扩展成其他垂直领域，如教育、消费、金融、文旅。

### 3.3 推荐的分层思路

建议新增一个顶层目录，例如：

```text
EmploymentLayer/
  __init__.py
  orchestrator.py
  scenario_router.py
  schemas.py
  prompts/
    market_prompts.py
    guidance_prompts.py
  tools/
    job_search_adapter.py
    company_risk_adapter.py
    resume_gap_analyzer.py
  templates/
    就业行情分析报告模板.md
    求职指导报告模板.md
    城市就业机会对比模板.md
  services/
    market_snapshot_service.py
    guidance_service.py
    signal_fusion_service.py
  adapters/
    query_agent_adapter.py
    media_agent_adapter.py
    insight_agent_adapter.py
    report_agent_adapter.py
```

这里的核心思想是：

- 原有五大引擎不动或少动。
- 新层负责把“就业问题”翻译成“底层引擎能理解的问题”。
- 新层负责把三类引擎输出重新整合成就业视角的结论。
- 新层负责选择更适合就业场景的报告模板。


## 4. 当前项目里哪些部分最值得复用

下面按模块分析哪些部分应该保留，哪些应该包一层适配。

### 4.1 `app.py`：继续作为系统级入口，但不要把就业逻辑塞满进去

文件：`app.py`

当前职责：

- 系统启动与关闭
- 配置读写
- 子应用状态聚合
- 搜索请求转发
- ReportEngine Blueprint 挂载
- SocketIO 通信

复用建议：

- 保留 `app.py` 作为总入口。
- 只在 `app.py` 增加一个新的 Blueprint 挂载点，譬如 `/api/employment`。
- 不要把就业业务逻辑直接写进现有 `/api/search` 或系统管理函数中。

推荐新增：

- `EmploymentLayer/flask_interface.py`

做法：

- 在 `app.py` 中仿照 `ReportEngine.flask_interface` 的挂载方式，挂载新的就业接口 Blueprint。
- 这样做只是在入口层增加一条新能力通道，不会污染原搜索接口。

为什么这么做：

- `app.py` 现在已经偏“大总管”，再继续堆就业逻辑会变得更难维护。
- 单独 Blueprint 能把“就业场景 API”与“通用系统 API”隔离。

影响：

- 对现有系统影响很小。
- 新增接口不会干扰现有前端和原 API。

### 4.2 `QueryEngine/agent.py`：非常适合复用，但不要直接改成“招聘 Agent”

文件：`QueryEngine/agent.py`

关键复用点：

- `DeepSearchAgent`
- `research(query: str, save_report: bool = True) -> str`
- `execute_search_tool(...)`
- `_generate_report_structure`
- `_initial_search_and_summary`
- `_reflection_loop`

为什么适合复用：

- 这个 Agent 已经是“从 query 出发做网络研究”的通用引擎。
- 它的核心不是“舆情”二字，而是“先规划报告结构，再多轮搜索与总结”。

不建议直接改的地方：

- 不要直接把 `SYSTEM_PROMPT_*` 改成就业版本。
- 不要把 `basic_search_news` 等工具语义强行替换成招聘语义。

推荐做法：

- 新增 `EmploymentLayer/adapters/query_agent_adapter.py`
- 由适配器把“就业问题”转换成一组适合 `QueryEngine` 执行的研究 query

例如：

- 用户问题：`2026 年杭州算法岗就业行情如何`
- 适配器拆解为：
  - `杭州 算法工程师 招聘 趋势`
  - `杭州 AI 公司 扩招 裁员 动态`
  - `算法工程师 岗位 技能要求 Python 机器学习 大模型`
  - `杭州 算法岗 薪资 区间 校招 社招`

这样 `QueryEngine` 继续做自己擅长的事，只是输入查询从通用舆情变成就业研究问题。

影响：

- `QueryEngine` 无需破坏式修改。
- 未来如果你想单独换一个更强的招聘搜索适配器，也不用动底层 Agent。

### 4.3 `QueryEngine/prompts/prompts.py`：建议新增一套就业版 Prompt，而不是覆盖原 Prompt

文件：`QueryEngine/prompts/prompts.py`

当前作用：

- 生成段落结构
- 生成搜索 query
- 做首次总结和反思总结

问题：

- 现有 Prompt 显著偏“新闻/事件/舆情”语义。
- 如果直接覆盖，会伤到原有功能。

推荐做法：

- 新增 `EmploymentLayer/prompts/market_prompts.py`
- 或者新增 `QueryEngine/prompts/employment_prompts.py`

更推荐第一种，因为它更符合“新加一层”的原则。

建议定义至少两套 Prompt：

- `EMPLOYMENT_MARKET_REPORT_STRUCTURE_PROMPT`
- `EMPLOYMENT_GUIDANCE_REPORT_STRUCTURE_PROMPT`

以及以下细化提示词：

- 就业市场搜索词生成 Prompt
- 岗位技能缺口分析 Prompt
- 城市机会比较 Prompt
- 企业风险信号总结 Prompt
- 求职建议生成 Prompt

原因：

- 就业分析看重“岗位供需、能力匹配、薪资分布、稳定性、成长性”。
- 舆情分析看重“事件脉络、传播声量、情感倾向、风险舆论”。
- 两套语义重合但不相同，硬合并只会让 Prompt 变得模糊。

### 4.4 `MediaEngine/agent.py`：保留，但重新定义其在就业场景中的职责

文件：`MediaEngine/agent.py`

当前能力：

- 多模态搜索
- 网页、结构化数据、多媒体信息综合
- 近期信息追踪

就业场景下建议的新职责：

- 分析短视频平台上的岗位分享、转行经验、面经、行业讨论
- 捕捉“热门岗位叙事”和“求职者真实情绪”
- 搜索结构化薪资、城市数据、企业公开信息
- 辅助识别“网红岗位”和“真实岗位需求”之间的偏差

推荐做法：

- 新增 `EmploymentLayer/adapters/media_agent_adapter.py`
- 不要直接修改 `MediaEngine` 主流程

适配器要做的事：

- 为就业问题构造更偏多模态、经验型、结构化信息型的查询词
- 对输出做筛选，把“经验分享”“岗位讨论”“企业口碑”“地区差异”抽成标准信号

建议新增信号分类：

- `candidate_sentiment`
- `skill_mentions`
- `city_mentions`
- `salary_mentions`
- `company_brand_mentions`
- `layoff_risk_mentions`

影响：

- `MediaEngine` 仍是通用多模态 Agent。
- 新层把其输出转义为就业语义即可。

### 4.5 `InsightEngine/agent.py`：这是最值得重用的“私域就业数据入口”

文件：`InsightEngine/agent.py`
相关工具文件：`InsightEngine/tools/search.py`

当前能力：

- 本地数据库检索
- 关键词优化
- 聚类采样
- 情感分析
- 平台定向搜索

为什么特别重要：

- 就业指导如果只靠公开网页，价值有限。
- 真正有壁垒的是私域数据，比如：
  - 你自己的岗位抓取库
  - 历史招聘趋势库
  - 学校就业去向库
  - 企业口碑库
  - 面试经验库
  - 简历投递与面试反馈库

也就是说，`InsightEngine` 是最有机会从“舆情数据库查询”进化成“就业知识库查询”的模块。

但依然不建议直接重写原工具。

推荐做法：

- 保留 `InsightEngine/agent.py` 的主流程不动。
- 新增一个就业侧数据库访问工具集，例如：

```text
EmploymentLayer/tools/employment_db_tools.py
```

然后新增：

```text
EmploymentLayer/adapters/insight_agent_adapter.py
```

这个适配器有两种实现路线。

#### 路线 A：完全复用 `InsightEngine`，只更换底层数据

适合早期 MVP。

方式：

- 复用 `InsightEngine` 的检索、聚类、总结能力。
- 让私有数据库里新增就业相关表，命名与查询范围扩展到：
  - `job_postings`
  - `company_hiring_events`
  - `salary_benchmarks`
  - `interview_feedback`
  - `campus_recruitment_records`
  - `candidate_profiles`

优点：

- 上手快
- 复用最多

缺点：

- 原工具函数名带有明显舆情语义，如 `search_hot_content`、`search_topic_globally`
- 概念映射会显得不够自然

#### 路线 B：保留 Agent 主流程，替换工具层

更推荐中期采用。

方式：

- 复用 `InsightEngine/agent.py` 的 `research` 主链路。
- 但新增就业工具类，例如：
  - `search_hot_jobs`
  - `search_jobs_by_city`
  - `search_jobs_by_skill`
  - `search_company_hiring_trend`
  - `get_candidate_feedback_for_role`
  - `analyze_skill_gap`

为什么推荐：

- 工具语义更准确。
- 文档、日志和调试过程更容易理解。

影响：

- 这是“有价值但相对更深”的改造点。
- 但仍然可以通过新增工具类和适配器实现，不必破坏现有 `MediaCrawlerDB`。

### 4.6 `InsightEngine/tools/search.py`：建议借鉴其模式，不建议直接硬改函数

文件：`InsightEngine/tools/search.py`

当前非常值得借鉴的设计：

- `DBResponse`
- `QueryResult`
- 一个类里封装多个意图明确的查询工具
- 对外暴露“高层工具语义”，而不是暴露 SQL 拼接细节

这是一个很好的模式，特别适合就业场景。

建议新增：

```python
class EmploymentMarketDB:
    def search_hot_jobs(...)
    def search_jobs_by_city(...)
    def search_jobs_by_role(...)
    def search_jobs_by_skill(...)
    def search_company_hiring_trend(...)
    def search_salary_distribution(...)
    def get_interview_feedback(...)
    def analyze_candidate_sentiment(...)
```

为什么不要直接改原函数：

- 原工具语义围绕“话题”“评论”“热点内容”。
- 就业领域更关心“岗位”“技能”“企业”“城市”“候选人反馈”。

如果直接改原函数名称和含义，会让旧场景和新场景都变得模糊。

### 4.7 `ReportEngine/agent.py`：高度复用，这是整个改造里最不该重写的部分

文件：`ReportEngine/agent.py`
相关接口：`ReportEngine/flask_interface.py`

这是全项目最值得保留的一个模块。

原因非常明确：

- 它已经完成了模板选择、布局设计、篇幅规划、章节生成、IR 校验、HTML 渲染等整套链路。
- 这些能力和“是不是舆情”关系不大，和“是不是要产出结构化分析报告”关系更大。

重点复用点：

- `ReportAgent.generate_report(...)`
- `FileCountBaseline`
- 输入文件检查与加载
- SSE 任务流
- 模板解析和 IR 渲染

最合理的做法不是改掉它，而是给它喂新的就业版输入和模板。

### 4.8 `ReportEngine/report_template/*.md`：新增就业模板，少碰原模板

当前目录里已经有多套模板。

这意味着模板体系已经成型，你不应该推翻，而应该扩展。

建议新增模板：

- `就业行情分析报告模板.md`
- `城市就业机会对比报告模板.md`
- `岗位技能需求分析报告模板.md`
- `求职指导与行动建议报告模板.md`
- `高校专业就业前景报告模板.md`

例如 `就业行情分析报告模板.md` 可以这样组织：

```text
1. 摘要与关键结论
2. 目标岗位/行业整体招聘景气度
3. 城市分布与机会密度
4. 核心技能要求与门槛变化
5. 薪资区间与岗位层级结构
6. 代表性企业招聘动态
7. 求职者反馈与竞争强度
8. 风险信号与不确定性
9. 求职策略建议
10. 下一步行动清单
```

原因：

- 报告模板本身就是业务产品化最直接的一层。
- 先新增模板，就能快速验证“同一底座能否产出就业版内容”。

影响：

- 几乎没有底层风险。
- 非常适合作为第一阶段改造。

### 4.9 `ReportEngine/flask_interface.py`：可复用其任务管理模式，但不要把就业任务直接塞进原 `/generate`

文件：`ReportEngine/flask_interface.py`

当前已经有很强的任务抽象：

- 任务创建
- 进度推送
- 状态查询
- SSE 流式事件
- 结果导出

推荐做法：

- 新增 `EmploymentLayer/flask_interface.py`
- 参考 `ReportEngine/flask_interface.py` 的任务模型和流式接口风格

不要做的事情：

- 不建议在原有 `/api/report/generate` 里加很多 `if scenario == "employment"` 分支。

更好的方式：

- 就业层自己维护 `/api/employment/generate`
- 内部再去调 `ReportAgent.generate_report(...)`

原因：

- 可读性更高
- 权责更清楚
- 避免原报告接口被业务场景分支侵蚀

### 4.10 `ForumEngine/monitor.py`：可以保留，但建议在就业场景中重新命名“讨论角色”

文件：`ForumEngine/monitor.py`

该模块本身无需为就业场景重写。

但是就业场景下，Agent 角色建议重新定义，例如：

- 市场观察员 Agent
- 岗位结构分析 Agent
- 候选人能力分析 Agent
- 企业风险观察 Agent
- 就业指导整合 Agent

为什么：

- 论坛机制的价值在于多视角冲突与整合。
- 就业场景非常适合“观点辩论式”综合判断。

对底层代码的影响：

- 可能只需要在新层中修改角色描述和 Prompt。
- `ForumEngine` 的日志监控、内容抽取逻辑可继续复用。


## 5. 建议的新架构：在现有 BettaFish 上方增加“就业领域编排层”

推荐架构如下：

```text
User / Frontend
    |
    v
EmploymentLayer
    |
    +-- Scenario Router
    +-- Employment Orchestrator
    +-- Agent Adapters
    +-- Signal Fusion Service
    +-- Employment Templates
    |
    +--> QueryEngine
    +--> MediaEngine
    +--> InsightEngine
    +--> ForumEngine
    +--> ReportEngine
```

### 5.1 核心新增组件

#### 5.1.1 `scenario_router.py`

职责：

- 判断当前请求是：
  - 市场行情分析
  - 岗位对比分析
  - 城市选择分析
  - 企业风险分析
  - 个人求职指导

为什么要有这个模块：

- 就业问题不是单一类型。
- 不同问题需要不同的 Agent 调用策略和模板。

示例分类：

- `market_analysis`
- `role_analysis`
- `city_comparison`
- `company_risk_review`
- `career_guidance`
- `resume_gap_analysis`

#### 5.1.2 `orchestrator.py`

职责：

- 统一编排三个分析引擎和报告引擎
- 决定哪些问题调用哪些 Agent
- 做跨 Agent 结果整合

这是新增层里最核心的文件。

建议暴露的主方法：

```python
def run_employment_analysis(request: EmploymentRequest) -> EmploymentResult
```

内部流程建议：

1. 解析用户问题
2. 路由到场景
3. 生成子任务计划
4. 调用 Query/Media/Insight 适配器
5. 聚合信号
6. 生成就业视角结构化中间结果
7. 选择模板
8. 调用 `ReportAgent.generate_report(...)`
9. 返回 HTML/Markdown/PDF 结果

#### 5.1.3 `signal_fusion_service.py`

职责：

- 把三个 Agent 的输出转成统一的就业信号

建议的统一字段：

- `market_heat`
- `demand_trend`
- `salary_band`
- `skill_requirements`
- `city_opportunity_score`
- `competition_level`
- `candidate_sentiment`
- `employer_reputation`
- `layoff_risk`
- `growth_potential`

为什么必须有这层：

- 现在各 Agent 输出更多是文本报告或段落总结。
- 就业场景需要更明确的“可比较信号”。

如果没有这一层，最后的指导建议容易变成松散文字堆叠。


## 6. 具体到“该复用哪个函数，改哪个函数，为什么改”

这一节更细，按“优先级”和“侵入程度”来写。

### 6.1 第一优先级：只新增，不改原逻辑

#### A. 复用 `QueryEngine/agent.py` 的 `research`

复用方式：

- 通过 `EmploymentLayer/adapters/query_agent_adapter.py` 实例化 `QueryEngine.create_agent()`
- 调用其 `research(query, save_report=True/False)`

为什么复用：

- 这是最低风险复用路径。
- 先把就业 query 送进去，看看输出质量，再决定是否深改。

影响：

- 无需改原函数。
- 适合 MVP。

#### B. 复用 `MediaEngine/agent.py` 的 `research`

复用方式同上。

为什么复用：

- 就业相关的多模态内容本来就重要，如“面经视频”“岗位吐槽”“转行经验”。

影响：

- 无需改原函数。

#### C. 复用 `InsightEngine/agent.py` 的 `research`

复用方式：

- 先让就业层把 query 翻译成数据库检索任务。

为什么复用：

- 即便底层数据库暂时还是舆情库，也可以先验证工作流。
- 后续只要把数据库内容换成就业数据，这条链路就能增强。

影响：

- 无需改原函数。

#### D. 复用 `ReportAgent.generate_report`

文件：`ReportEngine/agent.py`

这是必须复用的核心。

为什么复用：

- 已有完整产出链。
- 重写成本极高，而且没有必要。

影响：

- 新层只要构造好 `reports`、`forum_logs`、`custom_template` 即可。

### 6.2 第二优先级：新增同类函数，不要覆盖原函数

#### A. 在就业层新增 `build_employment_queries(...)`

原因：

- 现有 `QueryEngine` 内部虽然能自己从段落生成 query，但还缺少“就业问题拆解”这一步。

建议新增：

```python
def build_employment_queries(user_query: str, scenario: str) -> list[str]
```

作用：

- 把自然语言问题拆成更适合底层引擎处理的一组研究子问题。

#### B. 在就业层新增 `normalize_agent_outputs(...)`

原因：

- 三个 Agent 输出格式不同。
- 就业场景更强调横向比较。

建议新增：

```python
def normalize_agent_outputs(query_report: str, media_report: str, insight_report: str) -> dict
```

作用：

- 把文本输出抽取成统一结构。

#### C. 在就业层新增 `compose_employment_report_payload(...)`

作用：

- 把信号、结论、建议拼成适合 `ReportAgent` 的输入。

为什么：

- `ReportAgent` 是通用报告引擎，最好不要让它承担过多业务解释责任。

### 6.3 第三优先级：谨慎对原函数做可选参数扩展

如果后续要适度改原有底层，我建议只做“向后兼容的可选参数扩展”，而不是改原默认语义。

#### A. `research(...)` 增加 `context` 或 `scenario`

当前：

- `research(query: str, save_report: bool = True) -> str`

未来可考虑：

```python
research(
    query: str,
    save_report: bool = True,
    scenario: str | None = None,
    external_context: dict | None = None
) -> str
```

为什么想加：

- 就业场景下，同一个 query 如果知道是 `career_guidance`，搜索和总结角度应该不同。

为什么现在不建议立刻加：

- 这是轻微侵入。
- 第一版完全可以先由就业层做 query 包装，不必先动底层签名。

影响：

- 如果未来加了，要保证默认值保持旧逻辑不变。

#### B. `ReportAgent.generate_report(...)` 增加 `domain_tag`

作用：

- 让报告引擎知道当前是 `employment` 领域，可以选择日志命名、模板过滤和 UI 标签。

为什么：

- 对领域归档有帮助。

为什么不急着现在做：

- 完全可以先靠 `custom_template` 和 query 文本实现。


## 7. 建议新增的数据模型

新增一层后，建议不要再只靠“原始自由文本”驱动，而是定义更清晰的请求和响应结构。

### 7.1 `EmploymentRequest`

建议字段：

```python
class EmploymentRequest(BaseModel):
    query: str
    scenario: str | None = None
    target_role: str | None = None
    target_industry: str | None = None
    target_city: str | None = None
    target_company_types: list[str] | None = None
    candidate_background: dict | None = None
    guidance_mode: bool = False
```

用途：

- 让“行情分析”和“个性化指导”共享一个入口。

### 7.2 `EmploymentSignal`

建议字段：

```python
class EmploymentSignal(BaseModel):
    signal_type: str
    source: str
    confidence: float
    summary: str
    evidence: list[str]
    structured_value: dict | None = None
```

用途：

- 承接各 Agent 输出。

### 7.3 `EmploymentResult`

建议字段：

```python
class EmploymentResult(BaseModel):
    scenario: str
    normalized_signals: list[EmploymentSignal]
    key_findings: list[str]
    risks: list[str]
    opportunities: list[str]
    action_plan: list[str]
    report_html: str | None = None
    report_path: str | None = None
```


## 8. 就业系统可以支持的五类场景

建议先把产品能力拆成五类，而不是一上来做一个“大而全”的就业系统。

### 8.1 场景一：就业行情分析

适合问题：

- `2026 年数据分析师就业行情如何`
- `AI 产品经理是否还值得转`

调用策略：

- `QueryEngine` 强参与
- `MediaEngine` 中参与
- `InsightEngine` 弱参与或中参与
- `ReportEngine` 强参与

### 8.2 场景二：城市机会对比

适合问题：

- `上海和杭州的算法岗哪个机会更多`
- `广州和深圳互联网运营岗差异`

调用策略：

- 强化结构化比较
- 输出城市机会评分、薪资、竞争度、企业密度

### 8.3 场景三：岗位技能需求分析

适合问题：

- `后端开发岗位现在最看重哪些技能`
- `转 AI 应用开发需要补什么`

调用策略：

- 强化招聘 JD 抽取、技能词频统计、趋势分析

### 8.4 场景四：企业招聘风险与雇主口碑分析

适合问题：

- `某公司是否值得去`
- `某行业的招聘是否存在高风险信号`

调用策略：

- 强化媒体与社媒信号
- 搜索裁员、拖欠、口碑、面试评价

### 8.5 场景五：个性化求职指导

适合问题：

- `我是统计学专业，想去深圳找数据分析工作，应该怎么准备`

这是最有价值、也最需要谨慎的场景。

建议放到第二阶段再做。

原因：

- 它需要接入候选人的背景数据。
- 它涉及更强的建议性和偏差控制问题。


## 9. 第一版 MVP 最应该做什么

我建议第一版先做“就业行情分析”，暂时不要马上做强个性化就业指导。

原因：

- 市场分析比个性化建议风险更低。
- 更容易依赖公开信息完成。
- 更能验证底层 Agent 的复用性。

### 9.1 MVP 目标

实现一个新的入口：

- 输入：岗位/行业/城市/专业方向
- 输出：一份就业行情分析报告

例如：

- `2026 届计算机本科生在杭州的就业行情`
- `产品经理岗位的招聘需求变化与技能要求`
- `新能源行业算法岗就业前景`

### 9.2 MVP 只需要新增这些内容

- `EmploymentLayer/` 新目录
- 2 到 3 个适配器
- 1 个 orchestrator
- 1 个 signal fusion service
- 2 套就业模板
- 1 组就业 Prompt
- 1 个新的 Flask Blueprint

### 9.3 MVP 暂时不做

- 不改底层 Agent 核心签名
- 不改原报告接口
- 不重写 ForumEngine
- 不做简历评分
- 不做自动投递
- 不做真正意义上的“录用概率预测”


## 10. 分阶段实施方案

### 阶段 1：零侵入原型验证

目标：

- 不动底层 Agent 逻辑
- 仅新增就业层目录和模板

任务：

1. 新增 `EmploymentLayer/orchestrator.py`
2. 新增 3 个 Agent adapter
3. 新增就业 Prompt
4. 新增就业模板
5. 新增 `/api/employment/generate`

验收标准：

- 能生成一份结构完整的就业行情报告
- 原 `/api/report/generate` 不受影响

### 阶段 2：私域就业数据接入

目标：

- 提升 InsightEngine 在就业场景下的价值

任务：

1. 新增就业数据库表
2. 新增 `EmploymentMarketDB`
3. 新增招聘和技能分析工具
4. 把 `InsightEngine` 适配到就业私域库

验收标准：

- 报告不只是网页信息总结，而是能给出岗位趋势、技能热度、城市分布

### 阶段 3：个性化指导

目标：

- 从“市场分析”升级到“市场 + 个人背景”的行动建议

任务：

1. 新增候选人画像结构
2. 新增能力缺口分析
3. 新增行动计划生成器
4. 增加解释性字段和风险提示

验收标准：

- 报告能输出“你适合哪些方向、为什么、下一步怎么补”

### 阶段 4：前端产品化

目标：

- 做成独立的就业分析工作台

任务：

1. 新增就业模式首页
2. 新增行业、岗位、城市筛选器
3. 新增“市场报告”和“个人建议”双入口
4. 新增信号卡片、趋势图、企业风险清单


## 11. 具体推荐新增哪些文件

下面是一份比较务实的新增文件清单。

### 11.1 新增目录

```text
docs/
EmploymentLayer/
```

### 11.2 新增后端文件

```text
EmploymentLayer/__init__.py
EmploymentLayer/orchestrator.py
EmploymentLayer/flask_interface.py
EmploymentLayer/scenario_router.py
EmploymentLayer/schemas.py
EmploymentLayer/services/signal_fusion_service.py
EmploymentLayer/adapters/query_agent_adapter.py
EmploymentLayer/adapters/media_agent_adapter.py
EmploymentLayer/adapters/insight_agent_adapter.py
EmploymentLayer/adapters/report_agent_adapter.py
EmploymentLayer/prompts/market_prompts.py
EmploymentLayer/prompts/guidance_prompts.py
EmploymentLayer/templates/就业行情分析报告模板.md
EmploymentLayer/templates/求职指导报告模板.md
```

### 11.3 后续可选新增

```text
EmploymentLayer/tools/employment_db_tools.py
EmploymentLayer/services/resume_gap_service.py
EmploymentLayer/services/company_risk_service.py
EmploymentLayer/services/city_comparison_service.py
```


## 12. 可能需要修改的原文件，以及修改方式

这一节只列“建议允许的小改动”，并明确控制风险。

### 12.1 `app.py`

建议改动：

- 增加就业 Blueprint 注册

建议方式：

```python
from EmploymentLayer.flask_interface import employment_bp
app.register_blueprint(employment_bp, url_prefix='/api/employment')
```

为什么可接受：

- 这是入口级接线，不改原业务逻辑。

风险：

- 极低

### 12.2 `requirements.txt`

可能改动：

- 如果后续接招聘数据抽取、简历解析、更多表格分析，可能新增少量依赖。

建议：

- 第一版尽量不增重依赖。

为什么：

- 目前项目已经很重，MVP 应先验证方案。

### 12.3 `README.md`

建议改动：

- 在现有 README 中增加“垂直行业扩展”章节
- 或新增 `README-employment.md`

为什么：

- 明确项目支持通用舆情与就业场景双模式


## 13. 风险与挑战

### 13.1 最大风险不是技术，而是数据质量

就业分析是否真正有价值，关键取决于：

- 招聘信息是否足够新
- 数据源是否足够广
- 是否能过滤培训广告、虚假岗位、重复岗位
- 是否能识别“发帖热度”与“真实招聘需求”的差异

这意味着就业层必须逐步建立数据清洗能力。

### 13.2 “就业指导”天然带有建议风险

系统应该输出：

- 依据
- 不确定性
- 风险提示

而不是输出：

- 绝对建议
- 保证式结论

建议在最终报告中增加固定免责声明：

- 报告用于辅助判断，不构成确定性就业承诺
- 市场变化快，请结合个人背景与最新岗位信息判断

### 13.3 公开舆情热度不等于就业机会密度

例如：

- 某岗位在短视频平台很热
- 但真实岗位数未必多

所以必须引入“信号分层”：

- 舆论热度
- 招聘需求
- 企业扩张信号
- 候选人反馈

不能把它们混成一个分数。


## 14. 我给你的最终建议

如果目标是把这个项目认真做成“就业行情分析和就业指导系统”，我建议路线如下：

1. 不要直接改写原有五大引擎的核心语义。
2. 新增一个 `EmploymentLayer`，作为就业领域编排层。
3. 第一阶段只做“就业行情分析报告”。
4. 第二阶段再接入私域就业数据库，强化 `InsightEngine` 价值。
5. 第三阶段才做“个性化求职指导”。
6. 报告模板是最先改、最值得改的一层。
7. `ReportEngine` 尽量高度复用，不要重写。
8. `QueryEngine`、`MediaEngine`、`InsightEngine` 通过 adapter 复用，不要一开始就深度侵入。

换句话说：

> 当前最好的工程路径，不是“把 BettaFish 改掉”，而是“把 BettaFish 产品化成一个多领域分析底座，然后把就业场景作为第一个垂直行业插件接上去”。


## 15. 如果要立刻开始，我建议的第一个开发顺序

如果马上动手，我建议按这个顺序推进：

1. 先新建 `EmploymentLayer/` 目录和基础文件骨架。
2. 先写 `schemas.py`、`scenario_router.py`、`orchestrator.py`。
3. 先做 `query_agent_adapter.py` 和 `report_agent_adapter.py`。
4. 先加两份报告模板：
   - `就业行情分析报告模板.md`
   - `求职指导报告模板.md`
5. 先打通 `/api/employment/generate`。
6. 先让系统能产出第一份“就业行情分析报告”。
7. 再决定要不要深挖 `InsightEngine` 的就业数据库工具层。

这是投入产出比最高的路线。

