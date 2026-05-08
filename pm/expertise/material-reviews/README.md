# 外部资料评审目录

## 定位
- 本目录只存“外部资料是否应该进入理论库”的评审记录。
- 不在这里保存大段资料摘抄，也不把它当最终理论库正文。

## 目录结构
- 月度目录：`pm/expertise/material-reviews/YYYY-MM/`
- 月度 README：`pm/expertise/material-reviews/YYYY-MM/README.md`
- 具体评审卡：`pm/expertise/material-reviews/YYYY-MM/YYYY-MM-DD-<role>-<topic>.md`

## 支持脚本
- 当前月目录和 README 默认用以下命令补齐：
  - `python .repository/pm-main/scripts/bin/refresh_pm_expertise_material_reviews.py --shell-root .`
- 若需要重建当前月 README 索引，可追加：
  - `--overwrite-existing`

## 命名建议
- `YYYY-MM-DD-<role>-<topic>.md`

## 结论口径
- `纳入`
- `合并`
- `替换`
- `拒绝`
- `延后观察`
