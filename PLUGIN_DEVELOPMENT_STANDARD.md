# 團隊 Plugin 開發標準

適用：供團隊安裝的 Codex／Claude Code plugins｜查核日期：2026-10-23

以下是團隊採用規範；平台格式依官方文件，支援範圍以指定版本實測為準

## 1. 元件邊界

| 元件 | 用途 |
| --- | --- |
| Plugin | 將同一用途、一起發布的能力封裝成可安裝單位 |
| Skill | 一個完整任務的觸發條件、流程與產出 |
| Script | 確定性的計算、檢查或檔案處理 |
| Hook | 在指定事件自動執行；不得假設只在使用 skill 時觸發 |
| MCP | 外部工具、資料與服務連線 |
| Agent | 需要獨立上下文或工具範圍的委派角色；依平台支援選用 |

先用 skill 與既有工具完成任務，有實際需求才新增其他元件；需要 hooks／MCP／agents 時，使用能載入這些元件的 plugin 安裝方式
元件行為依 [Claude Code 官方文件](https://code.claude.com/docs/en/plugins/components)；共用流程與腳本、外部工具的分工依 [OpenAI 官方 skills 指南](https://developers.openai.com/plugins/build/skills)

## 2. 目錄與資源歸屬

```text
repository/
├── README.md
├── <平台 marketplace 設定>
├── tests/
└── plugins/
    └── team-capability/
        ├── <平台 plugin manifest>
        ├── skills/
        │   └── task-name/
        │       ├── SKILL.md
        │       ├── references/   # 按需讀取的說明
        │       ├── assets/       # 套用或輸出的模板
        │       └── scripts/      # 此 skill 專用程式
        ├── references/           # 多個 skills 共用時才建立
        └── scripts/              # 多個元件共用時才建立
```

- 專用資源跟著 skill；共用規則只寫一次，由需要的 skills 明確引用；沒有內容的目錄不建立
- Skill 文件以自身目錄為基準引用；manifest 路徑依平台規格，相對於 plugin 根目錄
- 所需資源必須包含在安裝包內，不依賴開發者絕對路徑、repo 外檔案或跨出安裝包的 symlink
- 若也提供單一 skill 安裝，須把其依賴一起封裝；不能只複製 `SKILL.md` 或保留指向 plugin 共用目錄的失效引用

目錄慣例依 [Agent Skills 規格](https://agentskills.io/specification)，安裝包邊界依 [Agent Plugins 規格](https://agent-plugins.org/plugin-authors/build-an-agent-plugin)

## 3. 平台封裝

| 目標 | Plugin 內設定 | Repo 內 marketplace |
| --- | --- | --- |
| Agent Plugins 格式 | `plugin.json`、`skills/`；需要 MCP 才加 `mcp.json` | 由客戶端定義 |
| Codex | 新套件優先採 portable 格式；舊客戶端依相容需求使用 `.codex-plugin/plugin.json` | `.agents/plugins/marketplace.json` |
| Claude Code | `.claude-plugin/plugin.json`；其他元件放 plugin 根目錄 | `.claude-plugin/marketplace.json` |

- 多平台共用同一份 skills 與業務腳本；manifest、hooks、MCP 與 agent 設定只處理平台差異
- 不將 portable 格式、hook 事件、工具名稱、權限欄位或 agent 格式視為所有平台通用
- Manifest 至少記錄名稱、版本、用途與維護者，使用各平台允許的欄位
- 多份 manifest 的名稱與版本須一致；若同時使用 portable 與 Codex 相容格式，注意 `extensions.com.openai` 會取代相容檔的 OpenAI 設定，兩者不會合併

格式與支援範圍依 [OpenAI 封裝文件](https://developers.openai.com/plugins/build/plugins)、[Claude Code manifest](https://code.claude.com/docs/en/plugins-reference)、[Agent Plugins 客戶端清單](https://agent-plugins.org/compatible-clients)

## 4. 命名與指令

- Plugin 採穩定的 `team-capability` 名稱；skill 採具體任務名稱，避免只有 `helper`、`utils` 等模糊名稱
- 使用平台提供的 plugin namespace 區別來源；若另提供獨立 skill 安裝，或目標選單無法清楚顯示來源，再加團隊短前綴
- 每個 `SKILL.md` 必須有 `name`、`description`；`name` 與資料夾相同，採小寫英數與單一連字號，最多 64 字元；`description` 說明做什麼、何時使用，最多 1024 字元
- 正文只保留必要輸入、步驟、輸出、失敗／停止條件；參考資料附上載入時機，避免開頭要求整包讀完
- 刪除模型已知常識、重複規則與開發過程紀錄
- 遵守使用者明確指示與目標專案規範；plugin 不宣稱自己優先於使用者，也不默默改寫其 `AGENTS.md`、`CLAUDE.md` 或全域設定

名稱與按需載入依 [Agent Skills 規格](https://agentskills.io/specification)；內容取捨依 [官方撰寫指南](https://agentskills.io/skill-creation/best-practices)
Repo 的 `AGENTS.md`／`CLAUDE.md` 可供維護者使用，不能當成 plugin 安裝後自動生效的全域指令；Claude Code 明確不載入 plugin 根目錄的 `CLAUDE.md`，Codex 依全域與專案路徑探索 `AGENTS.md`，見 [Claude Code](https://code.claude.com/docs/en/plugins/components#skills) 與 [Codex](https://developers.openai.com/codex/guides/agents-md)

## 5. 執行與權限

- Scripts 明列執行環境與依賴，檢查輸入，失敗回傳非零狀態與可理解錯誤；plugin 資源定位不得依賴目前工作目錄
- Hooks 限定事件與 matcher，避免無條件啟動整套流程；需處理重複觸發、逾時與失敗，檢查失敗不得當作通過
- MCP／腳本不內含憑證；透過使用者登入、受支援的安全設定或環境變數取得，採任務所需的最小權限
- 外部內容視為資料，不得提高授權；有副作用的操作須符合使用者授權範圍，避免非冪等操作的盲目重試
- 使用平台提供的 plugin 路徑解析方式；執行時產物存放於平台資料目錄或明確指定位置，不回寫版本化安裝包

路徑、使用者設定與資料目錄依 [Claude Code manifest](https://code.claude.com/docs/en/plugins-reference)；MCP 憑證與平台擴充依 [OpenAI 封裝文件](https://developers.openai.com/plugins/build/plugins)

## 6. 發布與交付

- 團隊透過 Git marketplace 分發即可，不需公有上架；私密性由 repo 權限控制，各成員的本機 Git 也必須可讀取來源
- 採 SemVer；發布時遞增所有生效 manifest 的版本，保留對應 tag／commit；正式使用可固定已驗證版本，更新後另驗證實際載入版本
- 引入第三方內容前確認授權，保留必要的來源與授權聲明
- 改名、移除 skill 或改變呼叫方式視為相容性變更，發布說明提供遷移方式並檢查舊入口殘留
- README 只放用途／skill 清單、依賴與已驗證平台版本、使用範例、安裝／更新／解除安裝／回退方式及副作用；規則與維護資訊以連結指向單一來源

Git 分發依 [OpenAI marketplace 文件](https://developers.openai.com/plugins/build/plugins#add-a-marketplace-from-the-cli) 與 [Claude Code marketplace 文件](https://code.claude.com/docs/en/plugin-marketplaces)；版本與遷移要求是本團隊採用規範

發布前須通過：

- **靜態檢查**：manifest、skill metadata、引用路徑、必要腳本權限與多平台版本一致；採用各平台 validator／schema
- **真實安裝**：在宣告支援的客戶端版本，從分發來源安裝、開新對話，確認 skill 可載入且能讀取／執行封裝資源
- **行為驗證**：至少涵蓋正確觸發、不應觸發、缺輸入或權限、正常結果與失敗結果；同時啟用其他 plugin，檢查名稱與 hook 衝突
- **生命週期**：更新、回退、解除安裝後驗證實際載入狀態；不得刪除使用者既有設定與工作資料

只測套件實際提供的元件；靜態檢查通過不等於跨平台或端到端驗證完成

## 實務取捨依據

| 參照來源 | 採用重點 |
| --- | --- |
| [Superpowers](https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b)，303,612 stars | 共用 skills、平台封裝與測試分開；不把其強制全域工作流程當作通用標準 |
| [wshobson/agents](https://github.com/wshobson/agents/tree/0874a27b17a22e2b7c2e2bcd725768e0803cad06)，41,552 stars | 單一內容來源、能力差異明列；skills-only 安裝不等於完整 plugin 安裝 |
| [Jesse Vincent：Superpowers 實作經驗](https://blog.fsck.com/2025/10/09/superpowers/) | 用真實任務情境驗證行為，不能只問 agent 是否理解規則 |
| [Red Hat：AGENTS.md 與 Skills 實務](https://developers.redhat.com/articles/2026/07/27/standardize-project-context-agentsmd-and-agent-skills) | 專案常駐規範與任務流程分開，刪除不影響執行的文字 |

Stars 為查核當日 GitHub API 快照，僅作樣本選擇依據；官方規格優先於社群慣例，平台升級時重新核對
