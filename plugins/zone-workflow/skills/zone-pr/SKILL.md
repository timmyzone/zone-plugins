---
name: zone-pr
description: 建立或更新 Zone 專案 GitHub PR，呼叫 zone-review 審查，檢查 Jira 版本或版本同步路徑，依合併門檻啟用 auto-merge；草稿或預覽不發布
---

# Zone PR

## 1. 確認輸入

讀取目標 repo 的 AGENTS.md／CLAUDE.md 與其引用的開發準則，再讀本 plugin 的 [票單政策](../../references/policy.md)

確認 repo、明確 base、head、本次關聯票與使用者要求的是草稿或發布，再依 [合併規則](references/merge-policy.md) 辨識一般 PR／版本同步 PR
透過 Git／GitHub 查證 remote、分支、PR 與工作區狀態；不得只憑目錄名稱猜 repo
PR URL 已指定時核對其 repo、head、base，不符即停止；未指定時依完整 repo／head／base 查 open PR，零筆建立、一筆更新、多筆請使用者指定，不改其他 base 的 PR

只描述 base 與 head 的 committed diff，記錄 base／head SHA；版本同步另記原始 release 與來源 SHA
未提交變更不納入 PR、不自動 stage 或 commit；若使用者預期包含它們，先說明缺口
base 不存在、detached HEAD、空 diff、遠端 head 含本機沒有的 commit 時停止發布
current branch 等於 base 時，可為已存在的 commits 建立專用 head 分支，不直接推送 base

完成條件：repo／base／head 與 PR 類型已查證，diff 範圍及本次票單或同步來源明確

## 2. 審查與發布門檻

一般 PR 依票單政策確認本次票單或免票條件；版本同步 PR 先依合併規則查證來源驗收與逐級路徑
每次執行都呼叫 [zone-review](../zone-review/SKILL.md)，即使先前已審查；傳入 repo、PR 類型、base／head SHA、committed diff、關聯票或已查證的同步來源
兩類均執行 [檢查器](references/version-check.md) 對應模式；腳本通過不代表來源、AC、CI 或 approval 已通過

不把 PR 授權解讀成修改程式授權；遇衝突依合併規則處理，未獲修正授權時回報並停止受影響操作

本次 review 未通過或未完成，或版本、同步來源／路徑、專案發布門檻未通過或無法查證時，交付草稿與缺口，停止發布
GitHub approval／CI 等合併門檻依第 4 節處理，可先建立 PR
完成條件：本次審查及適用的版本／路徑、專案發布門檻通過

## 3. 預覽並發布

採用本次 review 的結論與對照，依 [PR 模板](assets/pr-template.md) 寫精簡繁體中文 title/body
顯示 PR 類型、base ← head、head SHA、票單或同步來源、檢查結果、完整 title/body 與合併方式
只要求草稿／預覽時到此結束；要求建立／更新 PR 即包含發布與啟用 auto-merge，通過門檻後直接執行，不重複詢問

透過可用的 GitHub connector 或 `git`／`gh` 建立必要分支、一般 push、create/edit
不 force push、不修改 Jira、不更改目標版本以繞過門檻
若用 `gh`，將 body 原文保存暫存檔並以 `--body-file` 傳入，不用 `--fill`
push 後重查 PR，避免重複建立；操作失敗先讀取現況再重試

完成條件：遠端 PR 的 title/body、base、head 與 head SHA 均符合已審查內容

## 4. 啟用 auto-merge 並驗證

依合併規則選擇一般 PR 的 Squash 或已查證版本同步的 Merge commit，不只憑分支名稱決定
啟用前查證 [approval／CI 門檻](references/merge-policy.md)；保護不足或無法查證時保留 PR 並回報，不呼叫可能立即合併的命令
重新查證 PR 非 draft、可合併、base／head／同步來源 SHA 與遠端 release 清單未變；有變更則重做受影響的 diff、來源、路徑與驗證，不沿用舊結果
使用 GitHub 正常合併機制；例如 `gh pr merge <PR> --auto --merge|--squash --match-head-commit <SHA>`，只選一種方式
不使用管理員繞過、不更改 branch protection，不自動刪分支

回查 `state`、`mergedAt`、`mergeCommit`、`autoMergeRequest`：

- open 且 autoMergeRequest 的方式符合預期：回報「已啟用 auto-merge」
- 已進入符合所需合併方式的 merge queue：回報「已加入合併佇列」
- merged 且有 mergedAt／mergeCommit：回報「已完成合併」
- 其他情況：回報 PR 已建立／更新及 auto-merge 未成功的原因

附 PR 連結、驗證結果與剩餘缺口；啟用 auto-merge 不等於已合併、部署或通過 UAT
本 skill 只處理本次指定的 PR；後續版本同步須在前一個 PR 已實際合併後才能繼續，不因啟用 auto-merge 就宣稱整條合併鏈完成
