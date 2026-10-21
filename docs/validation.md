# 第一版驗證

日期：2026-10-20
範圍：本機 plugin，未 commit／push，未操作真實 Jira／PR

## 自動驗證

- Python unittest：7 項測試通過，包含多組正反案例
- 版本：兩種 release 名稱、任意後綴、數值排序、main 下一個 minor、拒絕來源 release 版本與跳版
- 輸入：無票、多票其中一張不符、零個／多個 fixVersions、重複票、錯誤型別
- CLI：暫存本機 Git repo 作為 remote，驗證成功、遠端失敗與非法 JSON；不連真實 Jira／GitHub
- 封裝：雙平台身份／版本一致、marketplace 路徑存在、Markdown 內部引用不超出 plugin
- Claude Code 2.1.288：marketplace、plugin 與 skills 原生 validate 通過
- skill-creator quick_validate：兩個 skills 均通過；PyYAML 使用暫存 uv 環境，未加入專案執行依賴

## 流程情境核對

以下是主代理靜態對照，非獨立代理執行或平台端到端測試

| 輸入情境 | 預期行為 | 規則位置 |
| --- | --- | --- |
| 本次 P-1、歷史 commit 有 P-2 | 只查 P-1 | policy：本次 Jira 票單 |
| 本次 P-1 與 P-2 都明確列出 | 兩張皆須通過 | policy：本次 Jira 票單 |
| 缺票、缺 AC、純重構無 AC | 審查／草稿可做，發布停止 | policy：本次 Jira 票單 |
| Jira／必要規範無法讀取 | 列出缺口，停止發布 | policy：共用政策 |
| 只要求 review 或 PR 預覽 | 不修改、不發布、不合併 | zone-review／zone-pr |
| 明確要求 review 並修正 | 修正與驗證，不重複詢問 | zone-review |
| release → main，最大 release 6.3.0，票 6.3.0 | 擋下；main 要求 6.4.0* | policy：版本政策 |
| merge/* 或 release/* → release／main | Merge commit，其餘 Squash | policy：發布與合併 |
| PR head 在審查後改變 | 停止合併，重做受影響檢查 | zone-pr：啟用 auto-merge |
| auto-merge 已設定但 PR 仍 open | 只回報已啟用 | zone-pr：啟用 auto-merge |

## 尚未驗證

- Claude Code／Codex 真正安裝、載入、更新、回退與模型執行效果
- Codex CLI 0.162.1 指令介面已核對；未註冊此 marketplace，唯讀 list 未列出此 plugin，不當作原生載入通過
- GitHub 遠端安裝需先 commit／push 到 repo，不需提交公有 plugin 目錄；目前 repo 尚無 commit
- 原指定 Notion 在前次對話讀取失敗，本次未重新查詢；共用準則採使用者已提供並確認的內容
- skills 是行為指引，靜態檢查不保證每次模型執行都遵守；正式採用前應在測試 repo 跑上述流程情境

## 2026-10-21 分發文件調整

- 核對指定對話與 OpenAI 官方 Git marketplace CLI 文件，改以各自帳號、repo 讀取權限安裝
- 本機 CLI help 支援 marketplace add 的 `--ref main` 與 `plugin add zone-workflow@zone-plugins`
- GitHub 唯讀查詢回報 repo 為 Public、預設分支名稱為空；未變更 repo 可見性
- 本次僅調整文件，未進行安裝、push 或端到端測試
