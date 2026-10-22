# Zone Plugins

Zone 團隊共用的 PR 與需求導向審查，Claude Code／Codex 共用同一份 skills
個別專案架構與測試規範由各 repo 提供

| Skill | 用途 |
| --- | --- |
| [zone-pr](plugins/zone-workflow/skills/zone-pr/SKILL.md) | 每次呼叫 zone-review，檢查版本／同步路徑、建立 PR 與啟用 auto-merge |
| [zone-review](plugins/zone-workflow/skills/zone-review/SKILL.md) | 可獨立使用或由 zone-pr 呼叫；依 AC、邊界、架構與品質審查，要求修正才修改 |

## 前置條件

- Git、Python 3.9+；GitHub connector 或已登入的 `gh`
- 可讀取本次 Jira 票與專案必要規範的 connector／API
- 支援 plugin／marketplace 的 Codex 或 Claude Code；工具權限與登入自行提供

## 安裝

直接從此 repo 的 `main` 安裝，不需上架公有 plugin 目錄
本機 Git 須有 repo 讀取權限；若內容僅限團隊，repo 本身須設為 Private

Codex，在終端機執行：

```sh
codex plugin marketplace add timmyzone/zone-plugins --ref main
codex plugin add zone-workflow@zone-plugins
```

Claude Code：

```sh
claude plugin marketplace add timmyzone/zone-plugins
claude plugin install zone-workflow@zone-plugins
```

安裝後重啟 App、開新對話
`marketplace add` 也可使用 SSH URL 或本機 repo 絕對路徑；Codex 遠端來源保留 `--ref main`

## 使用

- 「用 zone-review 審查這個 PR，只檢查本次關聯的 PROJECT-123」
- 「用 zone-pr 將目前已提交變更建立 PR 到 release/v6.2.0，關聯 PROJECT-123」
- 「用 zone-pr 將 release/v6.2.0 同步到下一個版本，先確認逐級路徑與來源 PR」
- 「只產出 PR 草稿，不發布」

Claude Code 可使用 `/zone-workflow:zone-pr` 與 `/zone-workflow:zone-review`
Codex 從技能選單選取對應 skill，或在請求中指名

PR 只檢查本次明確關聯票；子任務沿 parent 取得主票 AC 與修正版本，保留來源對照
`chore`／`refactor` 及其 `/名稱` 分支無關聯票時可免 Jira 檢查；有關聯票仍須檢查
票單範圍、主子票對應與免票條件見 [票單政策](plugins/zone-workflow/references/policy.md)，版本門檻見 [版本檢查](plugins/zone-workflow/skills/zone-pr/references/version-check.md)
純版本同步沿用來源 PR 驗收，不重比原票 fixVersion；逐級路徑、合併方式與衝突處理見 [合併規則](plugins/zone-workflow/skills/zone-pr/references/merge-policy.md)

建立／更新 PR 會在門檻通過後啟用 auto-merge；未設定或無法查證必要 approval／CI 保護時保留 PR，回報未啟用原因
skill 是代理工作流程，不是強制 CI；需要強制執行的規則仍由 branch protection／CI 落實

## 更新

Codex：

```sh
codex plugin marketplace upgrade zone-plugins
```

刷新來源後，於 Plugins 介面確認安裝版本並更新；若仍保留舊版，可重新安裝（本機路徑來源更新檔案後直接重裝，略過 marketplace upgrade）：

```sh
codex plugin remove zone-workflow@zone-plugins
codex plugin add zone-workflow@zone-plugins
```

Claude Code：

```sh
claude plugin marketplace update zone-plugins
claude plugin update zone-workflow@zone-plugins
```

更新後重啟 App、開新對話確認版本與 skills

回退時將獨立 clone 切到已驗證 tag／commit，移除目前 plugin／來源，再以該 clone 的絕對路徑加入 marketplace 並安裝；停止該來源自動更新，避免回到新版

## 解除安裝與刪除

Codex：

```sh
codex plugin remove zone-workflow@zone-plugins
codex plugin marketplace remove zone-plugins
```

Claude Code：

```sh
claude plugin uninstall zone-workflow@zone-plugins
claude plugin marketplace remove zone-plugins
```

Claude Code 上述 uninstall 使用預設 user scope；若曾以 project／local scope 安裝，須在對應專案加上 `--scope project`／`--scope local` 解除安裝
只想移除 plugin 時執行第一行即可；來源還有其他 plugin 在使用時，保留 marketplace
完成後重啟 App、開新對話；自行 clone 的目錄須確認沒有未提交工作後另行刪除

## 維護與驗證

開發依 [團隊 Plugin 標準](PLUGIN_DEVELOPMENT_STANDARD.md)；發布更新時同步遞增兩個 manifest 的版本，檢查通過後 push 到 `main` 並保留對應 tag／commit

```sh
python3 -m unittest discover -s tests -v
claude plugin validate --strict .
claude plugin validate --strict ./plugins/zone-workflow
```

已驗證 Codex CLI 0.163.0、Claude Code 2.1.288：隔離本機來源的安裝、更新、回退、解除安裝與封裝資源引用
尚未驗證 Git 遠端安裝、桌面／新對話中的 skill 行為與真實 Jira／PR 端到端流程

封裝格式：[Codex](https://developers.openai.com/plugins/build/plugins)、[Claude Code manifest](https://code.claude.com/docs/en/plugins-reference)／[marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
