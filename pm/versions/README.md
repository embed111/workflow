# PM版本目录

## 定位
- 本目录用于保存每个版本的独立目录。
- 当前口径下，一个版本对应一个目录，不再拆成“版本文件在这里、版本历史在别处”。

## 目录规则
- 路径模式：`pm/versions/<version>/`
- 每个版本目录至少包含：
  - `版本计划.md`
  - `history/YYYY-MM/YYYY-MM-DD.md`
- 其中：
  - `版本计划.md` 负责该版本的完整排期正文
  - `history/` 负责该版本的日级推进、调整、后移和排期变化记录

## 自动初始化
- 若当前 active 版本已经存在，但下一个版本目录还没建，可以在 `workflow` 根目录执行：
  - `python .repository/pm-main/scripts/bin/bootstrap_next_pm_version.py --shell-root .`
- 该脚本默认会：
  - 自动按现有最高版本号创建下一个 `pm/versions/V{N+1}/`
  - 补齐 `版本计划.md`、`需求映射与覆盖矩阵.md`、当日 `history/YYYY-MM/YYYY-MM-DD.md`
  - 同步更新 `pm/PM版本目录导航.md`
- 默认是幂等的：已存在的版本骨架不会被覆盖，只会继续补齐缺失的导航与路线图入口。

## 与其他文件的关系
- `pm/PM版本推进计划.md`
  - 稳定总计划，只做治理原则、路线图和结构规则
- `pm/PM版本目录导航.md`
  - 单独维护版本目录导航、状态与路径索引
- `pm/PM当前版本计划.md`
  - 当前活跃版本自动引用文件，只负责指向当前版本目录中的 `版本计划.md`，并保留单份状态快照
- `pm/versions/<version>/版本计划.md`
  - 该版本的完整计划正文
- `pm/versions/<version>/history/YYYY-MM/YYYY-MM-DD.md`
  - 该版本的日级推进、调整、后移和排期变化记录
