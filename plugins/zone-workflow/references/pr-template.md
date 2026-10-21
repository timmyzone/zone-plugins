# PR 內容

標題描述實際行為；票號前綴依目標 repo 規範
內容以 committed diff 為準，不把生成檔或 commit 清單當作功能描述
下列欄位替換為真實資料，API／DB／Notes 無內容時移除

```markdown
## Related Tickets

- <已查證的本次 Jira 票連結>

## Changes

- <問題與修正後的行為>

## AC 對照

| AC | 實作位置 | 測試 |
| --- | --- | --- |
| <票號與逐條 AC> | <檔案:行號／函式> | <測試名稱、執行結果；未執行須註明> |

## API Changes

<契約改變才填寫>

## DB Changes

<schema／migration／資料改變才填寫>

## Notes

<影響審查、合併或上線判斷的風險與限制>
```
