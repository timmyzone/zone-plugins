# Zone Plugins

Zone 團隊共用的 PR 與需求導向審查，Claude Code／Codex 共用同一份 skills
個別專案架構與測試規範由各 repo 提供

| Skill | 用途 |
| --- | --- |
| `zone-pr` | Jira AC、目標版本檢查、PR 對照表與 auto-merge |
| `zone-review` | 依 AC、邊界案例、架構與品質審查；要求修正才修改 |

## 前置條件

- Git、Python 3.9+；GitHub connector 或已登入的 `gh`
- 可讀取本次 Jira 票與專案必要規範的 connector／API
- 平台須支援 plugin／marketplace；最低平台版本尚未建立相容性矩陣
- plugin 不附帳密或外部 skills；工具權限與登入由 teammate 自行提供

## 團隊內部分發

透過 GitHub repo 分發，每人使用自己的 Codex／Claude Code 帳號安裝
不提交公有 plugin 目錄、不需要公司 workspace 或 Admin 後台
此處 marketplace 是 repo 內的安裝清單，仍須保留 `.agents/plugins/marketplace.json` 與 plugin manifest

維護者將內容 commit／push 到 `main`，並給每位 teammate repo 讀取權限即可
若內容僅限團隊存取，GitHub repo 本身也必須是 Private；未上架公有 plugin 不代表 repo 私有
2026-10-21 查詢此 repo 為 Public；本次交付未修改可見性

## 每位 teammate 安裝

先確認本機 Git 可以讀取 repo，例如 `git ls-remote https://github.com/timmyzone/zone-plugins.git`
私有 repo 需使用各自的 Git 憑證；網頁有讀取權限不代表本機 Git 已登入
遠端安裝使用此 repo 的 `main` 分支

Codex，在終端機執行：

```sh
codex plugin marketplace add timmyzone/zone-plugins --ref main
codex plugin add zone-workflow@zone-plugins
```

重啟桌面 App，開新對話使用
也可只執行第一行，再到 Plugins 選取 Zone Plugins 來源、安裝 zone-workflow
若本機 Git 使用 SSH，可將來源改為 `git@github.com:timmyzone/zone-plugins.git`，保留 `--ref main`

Claude Code：

```sh
claude plugin marketplace add timmyzone/zone-plugins
claude plugin install zone-workflow@zone-plugins
```

開新對話載入。開發時可把 marketplace add 的來源改為此 repo 的絕對路徑

## 使用

- 「用 zone-review 審查這個 PR，只檢查本次關聯的 PROJECT-123」
- 「用 zone-pr 將目前已提交變更建立 PR 到 release/v6.2.0，關聯 PROJECT-123」
- 「只產出 PR 草稿，不發布」

Claude Code 可使用 `/zone-workflow:zone-pr` 與 `/zone-workflow:zone-review`
Codex 從技能選單選取對應 skill，或在請求中指名

建立／更新 PR 會在門檻通過後啟用 auto-merge；無必要檢查的 repo 可能立即合併
skill 是代理工作流程，不是強制 CI；需要強制執行的規則仍由 branch protection／CI 落實

## 更新與回退

維護者同步遞增兩個 plugin manifest 的版本，驗證後將 Git commit／tag push 到此 repo
使用者更新：

```sh
claude plugin marketplace update zone-plugins
claude plugin update zone-workflow@zone-plugins
codex plugin marketplace upgrade zone-plugins
```

Codex 刷新 catalog 後，於 Plugins 介面確認安裝版本並更新；若仍保留舊版，移除後重新安裝
兩平台更新後重啟 App、開新對話確認版本與 skills；每人自行更新，沒有管理員每日同步

回退時將此 repo 的**獨立 checkout** 切到已驗證 tag／commit，以本機 marketplace 來源重新安裝
先移除原 plugin／marketplace，再將該 checkout 路徑加入；不要對有未提交修改的工作目錄執行 reset
第一版尚未發布 tag，沒有可用的歷史版本；回退後停止自動更新，避免再升回新版

## 驗證

```sh
python3 -m unittest discover -s tests -v
claude plugin validate .
claude plugin validate ./plugins/zone-workflow
```

測試覆蓋版本正反案例、數值排序、多票、資料缺漏、遠端失敗與封裝引用
流程情境與實際驗證界線見 [驗證紀錄](docs/validation.md)
共用規則維護於 [policy.md](plugins/zone-workflow/references/policy.md)，需求決策保留於 [requirements.md](docs/requirements.md)

## 格式依據

- [OpenAI plugin 封裝與 marketplace](https://developers.openai.com/plugins/build/plugins)：採仍支援的 `.codex-plugin/plugin.json`，指向共用 skills
- [Claude Code manifest](https://code.claude.com/docs/en/plugins-reference) 與 [marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
