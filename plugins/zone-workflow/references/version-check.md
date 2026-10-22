# 版本檢查

用 Python 3.9 以上執行 plugin 內的 `scripts/check_versions.py`
符合無票例外時提供已查證的 `head` 與 `tickets: []`；檢查器仍驗證 base 與目標版本推導，輸出 `ticket_check: skipped` 表示免 Jira 比對，不代表 AC 通過
`head` 必須是實際 PR 來源分支；腳本不驗證 head 身分，呼叫者須先查證
輸入 JSON 由已查證的本次票單建立；不得把歷史票補入，亦不得省略本次關聯票
先依 [共用政策](policy.md) 解析主票／子任務：`key` 保留本次關聯票號，`fixVersions` 填入其驗收來源主票的版本
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
python3 /absolute/path/to/plugin/scripts/check_versions.py /tmp/pr-versions.json
```

腳本透過 `git ls-remote --heads origin` 取得遠端分支，不修改 Git 或 Jira
目標 repo 使用其他 remote 時加 `--remote <已確認的 remote>`
exit 0 只表示輸入票單的版本通過；exit 1 為版本／輸入／遠端查詢失敗
腳本不查 Jira、不決定關聯票、不驗證 AC，也不證明輸入資料仍是最新
發布前重新確認票單、Jira 資料及 base 未變；資料變更則重跑
