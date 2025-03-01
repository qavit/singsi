# SingSi 專案結構

## 目前專案目錄配置

```
/singsi/
│
├── app/                               # 應用程式主目錄
│   ├── api/                           # API 端點定義
│   │   ├── __init__.py
│   │   └── ai.py                      # AI 服務相關 API
│   │
│   ├── core/                          # 核心配置
│   │   └── config.py                  # 配置管理
│   │
│   ├── examples/                      # 範例程式碼與使用示範
│   │   └── conversation_example.py    # 簡單 AI 對話示範
│   │
│   ├── models/                        # 資料模型
│   ├── schemas/                       # Pydantic 結構定義
│   ├── services/                      # 業務邏輯服務
│   │   ├── ai/                        # AI 相關模組
│   │   │   ├── __init__.py
│   │   │   ├── base/                       # 基礎 AI 定義
│   │   │   │   └── ai_service_abstract.py  # AIService 介面
│   │   │   ├── factory/                    # AI 服務工廠模組
│   │   │   │   └── ai_service_factory.py   # AI 服務實例建立工廠
│   │   │   ├── implementations/            # 特定 AI 平台實作
│   │   │   │   └── openai_service.py       # OpenAI 服務實作
│   │   │   └── utils/                      # AI 功能共用工具
│   │   │       └── logging_utils.py        # 紀錄工具
│   │   ├── other_services.py               # 其他業務邏輯模組
│   │   └── __init__.py
│   ├── tasks/                         # 非同步任務
│   ├── utils/                         # 工具函數與共用工具
│   ├── __init__.py
│   └── main.py                        # 應用程式進入點
│
├── tests/                             # 單元與整合測試
├── alembic/                           # 資料庫遷移
├── docs/                              # 文件檔案
│   ├── design_proposals.md            # 設計概述與模式
│   ├── PRD_EN.md                      # 產品需求文件（英文）
│   ├── PRD_zh_TW.md                   # 產品需求文件（正體中文）
│   └── project_structure.md           # 本專案結構文件
│
├── Dockerfile                         # Docker 配置
├── docker-compose.yml                 # Docker Compose 配置
├── .env                               # 環境變數
├── .gitignore                         # Git 忽略檔案
├── requirements.txt                   # 相依套件清單
└── README.md                          # 專案文件
```

## 關鍵組件

- **AI 服務模組**：位於 `app/services/ai/`，有適當區分介面、實作與工廠
- **配置管理**：集中在 `app/core/config.py`，使用 Pydantic 設定
- **API 層**：RESTful 端點定義於 `app/api/` 目錄
- **範例**：在 `app/examples/` 中有示範程式碼展示使用模式

## 架構說明

本專案遵循模組化設計，明確區分各模組職責：

1. 抽象介面定義功能而不包含實作細節
2. 具體實作提供特定功能
3. 工廠模組處理物件建立並進行依賴注入
4. 配置設定集中管理且具備型別檢查

此結構使程式碼易於測試、擴展和維護。
