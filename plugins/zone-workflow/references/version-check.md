# 版本檢查

用 Python 3.9 以上執行 plugin 內的 `scripts/check_versions.py`
輸入 JSON 由已查證的本次票單建立；不得把歷史票補入，亦不得省略本次關聯票

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
