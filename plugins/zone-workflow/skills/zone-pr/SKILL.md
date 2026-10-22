---
name: zone-pr
description: 建立或更新 Zone 專案 GitHub PR，檢查本次 Jira AC 與目標版本，產出 AC 對照表並啟用 auto-merge；只要求草稿或預覽時不發布
---

# Zone PR

## 1. 確認輸入

讀取目標 repo 的 AGENTS.md／CLAUDE.md 與其引用的開發準則，再讀本 plugin 的 [共用政策](../../references/policy.md)

確認 repo、明確 base、head、本次關聯票與使用者要求的是草稿或發布
透過 Git／GitHub 查證 remote、分支、PR 與工作區狀態；不得只憑目錄名稱猜 repo
PR URL 已指定時核對其 repo、head、base；未指定時依 head 查 open PR，零筆建立、一筆更新、多筆請使用者指定

只描述 base 與 head 的 committed diff，記錄 head SHA
未提交變更不納入 PR、不自動 stage 或 commit；若使用者預期包含它們，先說明缺口
base 不存在、detached HEAD、空 diff、遠端 head 含本機沒有的 commit 時停止發布
current branch 等於 base 時，可為已存在的 commits 建立專用 head 分支，不直接推送 base

完成條件：repo／base／head 唯一且已查證，diff 範圍與本次票單明確

## 2. 核對需求與版本

先依共用政策判定是否符合無票 chore／refactor 例外；有票時辨識主票／子任務、取得驗收來源主票，建立關聯票 → 主票及 AC／實作／測試對照
審查行為依 [審查流程](../zone-review/SKILL.md)，只讀取流程，不把 PR 授權解讀成修改程式授權
版本檢查使用 [檢查器說明](../../references/version-check.md)

缺漏、失敗或無法查證時，交付已完成的草稿與缺口，停止發布
完成條件：每張關聯票的驗收來源、AC 與版本通過，或已查證符合免票例外；兩者皆須通過 base 與適用專案發布門檻

## 3. 預覽並發布

依 [PR 模板](../../references/pr-template.md) 寫精簡繁體中文 title/body
顯示 base ← head、head SHA、票單、版本檢查結果、完整 title/body 與合併方式
只要求草稿／預覽時到此結束；已要求建立／更新 PR 時直接執行，不重複詢問

透過可用的 GitHub connector 或 `git`／`gh` 建立必要分支、一般 push、create/edit
不 force push、不修改 Jira、不更改目標版本以繞過門檻
若用 `gh`，將 body 原文保存暫存檔並以 `--body-file` 傳入，不用 `--fill`
push 後重查 PR，避免重複建立；操作失敗先讀取現況再重試

完成條件：遠端 PR 的 title/body、base、head 與 head SHA 均符合已審查內容

## 4. 啟用 auto-merge 並驗證

依共用政策選定 Merge commit 或 Squash
再次查證 PR 非 draft、可合併且 head SHA 未改變；衝突、未知狀態或 SHA 改變時停止，回報或重做受影響檢查
使用 GitHub 正常合併機制；例如 `gh pr merge <PR> --auto --merge|--squash --match-head-commit <SHA>`，只選一種方式
不使用管理員繞過、不更改 branch protection，不自動刪分支

回查 `state`、`mergedAt`、`mergeCommit`、`autoMergeRequest`：

- open 且 autoMergeRequest 的方式符合預期：回報「已啟用 auto-merge」
- merged 且有 mergedAt／mergeCommit：回報「已完成合併」
- 其他情況：回報 PR 已建立／更新及 auto-merge 未成功的原因

附 PR 連結、驗證結果與剩餘缺口；啟用 auto-merge 不等於已合併、部署或通過 UAT
