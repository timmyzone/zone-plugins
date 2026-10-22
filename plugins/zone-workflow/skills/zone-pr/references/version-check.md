# PR 版本與路徑檢查

## 一般 PR：版本政策

只允許 `main`、`release/vX.Y.Z`、`release/X.Y.Z` 作為 base，且完整分支必須存在遠端
使用者只給版本別名時，兩種 release 名稱若都存在，請其指定完整分支
本次每張關聯票都須通過版本門檻；每張驗收來源主票須恰好一個 fixVersion，零個或多個均擋下

- release：預期版本取目標分支的 X.Y.Z
- main：遠端 release 分支按 major/minor/patch 數值取最大 M.m.p，預期版本為 M.(m+1).0；沒有 release 或查詢失敗時停止
- Jira 名稱去除前後空白與開頭一個可選 `v`，以預期 X.Y.Z 做字串前綴比對；後綴可為任何字元，包含數字
- 例如預期 6.2.0，接受 `6.2.0`、`v6.2.0(後端)`、`6.2.00`、`6.2.01`；不接受 `6.2.1`、`16.2.0`

這是團隊政策，不是語意版本相等判斷；不為 main 新增版本文件，不自行處理跳版或 major 升版

## 版本同步 PR：路徑政策

先依 [合併規則](merge-policy.md) 查證來源與驗收，才使用 `kind: "promotion"`；原票版本保留在來源追蹤，不重新比對目標版本
`source` 填原始 release 完整名稱，即使實際 head 是已查證的 `merge/*` 暫時分支也相同
檢查器只允許 source → 下一個較大 release，最大 release → main；source／base 必須存在遠端，release 名稱無法解析或同數值版本有多個名稱時阻擋

```json
{
  "kind": "promotion",
  "source": "release/v6.2.0",
  "base": "release/v6.3.0"
}
```

輸出 `ticket_check: "not_checked"` 只表示此模式不做票單比對；不代表來源 PR、AC 或 Git ancestry 已通過，這些由呼叫者查證

## 執行

用 Python 3.9 以上執行此 skill 的 [檢查器](../scripts/check_versions.py)；先依載入的 skill 位置解析其絕對路徑
一般 PR 的 `kind` 可省略或填 `"change"`；其他值拒絕，不能拼錯模式後默默略過檢查
符合無票 chore／refactor 例外時提供已查證的 `head` 與 `tickets: []`；檢查器仍驗證 base 與目標版本推導，輸出 `ticket_check: skipped` 表示免 Jira 比對，不代表 AC 通過
`head` 必須是實際 PR 來源分支；腳本不驗證 head 身分，呼叫者須先查證
一般 PR 的輸入 JSON 由已查證的本次票單建立；不得把歷史票補入，亦不得省略本次關聯票
先依 [票單政策](../../../references/policy.md) 解析主票／子任務：`key` 保留本次關聯票號，`fixVersions` 填入其驗收來源主票的版本
例如本次為子票 PROJECT-124、parent 為 PROJECT-123，輸入 key 為 PROJECT-124，版本取 PROJECT-123；PR 另列此來源對照
多張子票共用主票時，每張子票仍有自己的輸入列；檢查器只比對解析後的版本，不驗證 parent 關係

```json
{
  "base": "main",
  "tickets": [
    { "key": "PROJECT-123", "fixVersions": ["6.4.0(後端)"] }
  ]
}
```

將輸入保存暫存檔，在**目標 repo** 執行：

```sh
python3 "/absolute/path/to/plugin/skills/zone-pr/scripts/check_versions.py" /tmp/pr-versions.json
```

腳本透過 `git ls-remote --heads origin` 取得遠端分支，不修改 Git 或 Jira
目標 repo 使用其他 remote 時加 `--remote <已確認的 remote>`
exit 0 只表示一般 PR 的版本或同步 PR 的分支路徑通過；exit 1 為檢查／輸入／遠端查詢失敗
腳本不查 Jira／GitHub、不決定票單、不驗證 AC、來源提交或 CI，也不證明輸入資料仍是最新
發布前重新確認一般 PR 的票單／Jira 資料，或同步 PR 的來源／路徑，以及兩類的 base 未變；資料變更則重跑
