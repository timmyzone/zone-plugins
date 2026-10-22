# PR 類型與合併規則

依 [團隊 Git 分支策略](https://app.notion.com/p/334ee99cff0180de8564f37342bc11e0)；專案額外門檻仍須遵守

## 辨識與路徑

| 類型 | 判定與驗收 | 合併方式 |
| --- | --- | --- |
| 一般 PR | 交付本次功能／修正；通過本次審查與目標版本檢查 | Squash |
| 版本同步 PR | 將已驗收的 release 改動傳至下一版本；查證來源 PR、差異與路徑，沿用來源驗收 | Merge commit |

`release/*`、`merge/*` 名稱本身不構成同步例外；必須查證：

1. 原始來源是遠端完整 `release/[v]X.Y.Z`，新增至目標的內容可追溯至已合併且完成驗收的來源 PR／已驗證同步 PR，記錄連結與 merge commit
2. 本次 source SHA 確實包含這些 commits；差異沒有未驗收的新功能、直接提交或不明內容，不能只用一張已合併 PR 代表整個 release
3. 原始 release 依數值版本只合到下一個較大的遠端 release，最大版本才合到 main；hotfix 的 patch 版本也適用，不反向、不跳級、不 cherry-pick
4. 實際 head 為原始 release，或下節已查證的衝突處理分支；head、base、來源與 Git ancestry 不明時停止，不以分支名稱推測

更新遠端 refs 後，使用 [檢查器的 promotion 模式](version-check.md) 核對路徑；遠端有重複版本或無法辨識的 release 名稱時先釐清，不自行忽略或刪除分支
同步 PR 保留來源票號及其原版本作追蹤，不新增歷史票作本次需求，也不把原票重新比對到目標版本

## 版本同步的衝突處理

只要求建立 PR 時，衝突不構成修改程式的授權；已要求解衝突或修正時才執行：

1. 保留使用者工作區，必要時用隔離 worktree；從最新目標 base 切 `merge/<來源版本>-to-<目標>` 暫時分支，既有同名分支先核對來源，不覆寫
2. 將原始 release merge 進暫時分支，解決衝突並保留 merge ancestry；不把目標分支反合進原始 release，不 rebase／squash 同步 commits
3. 檢查衝突解法沒有額外業務變更，執行受影響驗證；影響範圍大或需求判斷不明時取得相關開發者確認
4. 以暫時分支向原目標發 Merge commit PR，附原始 release、source／base SHA、來源 PR 與衝突處理摘要；重新核對路徑及合併後的 CI

原 release PR 與暫時分支 PR 不可同時排入 auto-merge／queue；若前者已排入，先停用排程並查證仍未合併，再處理替代 PR，不自動關閉或刪除原分支
一般 PR 的衝突依目標 repo 規則處理，仍保留原本的需求驗收與 Squash 方式，不套用版本同步例外

## Approval 與 CI

- 一般 PR 合併至少需要一位有資格的非作者 reviewer approval；agent 自己的審查不能代替 GitHub approval
- 版本同步不額外要求人工 approval，但 GitHub 實際要求的 approval／CODEOWNERS 等規則仍須滿足
- 兩類都須跑本次 head／測試合併結果的適用 CI；來源 PR 曾通過不代表新組合通過，無 checks、未觸發或不明狀態不能當成功；依專案設計不適用的 job 須標明原因
- 啟用 auto-merge 前讀取目標分支有效的 branch protection／rulesets：一般 PR 必須強制至少一人 approval 與必要 CI，同步 PR 必須強制必要 CI；本次 PR 階段適用 CI 已執行成功後才啟用，pending 保留 PR 等待，失敗先回報
- 規則未設定、只在 evaluate 模式、適用必要 CI 未被保護，或權限不足無法確認時，只保留已建立的 PR，不嘗試合併、不自動更改保護設定
- 使用 merge queue 時查證 queue 設定的合併方式符合本次類型；不符合或查不到時停止合併，不以 queue 繞過 Squash／Merge commit 區分。queue 專屬 CI 由有效規則於入列後強制執行，未成功前不能宣稱已完成合併

GitHub 的 [auto-merge](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-auto-merge-for-pull-requests-in-your-repository) 只等待已設定門檻；[required status checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) 可能接受 skipped／neutral，因此仍須確認適用 CI 確實執行，不以 GitHub 可合併狀態代替驗證
