# Zone 共用開發流程

供 Zone 各專案與 teammate 共用的 PR 與審查能力

## 維護入口

- `plugins/zone-workflow/skills/`：Claude Code／Codex 共用的 skills
- `plugins/zone-workflow/references/policy.md`：執行時共用政策，規則修改集中於此
- `docs/requirements.md`：已確認的需求與決策背景
- `README.md`：安裝、更新與回退
- `docs/validation.md`：實際驗證結果與未驗證範圍
- 驗證命令：`python3 -m unittest discover -s tests -v`

## 用語

**共用準則**：適用於 Zone 各專案的開發協作要求，不包含個別專案的架構設計

**專案開發準則**：由各專案維護、描述該專案架構與開發限制的規範，是共用審查流程的輸入

**AC 對照表**：逐條連結 Jira 驗收條件、實作位置與測試證據的 PR 內容，用於判斷需求是否被正確完成

**版本門檻**：依 Jira 修正版本與 PR 目標分支判斷是否允許發布的條件
