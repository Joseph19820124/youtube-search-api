# 📦 YouTube Search API on AWS (Lambda + API Gateway + Secrets Manager)

這是一個 Serverless 架構專案，透過 **AWS Lambda + API Gateway** 提供 YouTube 搜尋服務，並且安全地從 **AWS Secrets Manager** 取得 API 金鑰，自動部署流程由 **CodePipeline + CodeBuild** 完成。

---

## ✅ 功能簡介

- 提供 HTTP API：`GET /search?q=關鍵字&days=天數`
- 自動搜尋熱門 YouTube 影片（預設為近 7 天內、觀看數排序）
- 無外部套件依賴，使用 `urllib` 完成請求
- 使用 Secrets Manager 保護 API 金鑰安全
- 自動部署成功後寄信通知

---

## 📁 專案結構

```
youtube-search-api/
├── lambda/
│   └── handler.py            # Lambda 主程式
├── template.yaml             # CloudFormation 定義 Lambda / API Gateway / IAM / SNS
├── buildspec.yml             # CodeBuild 腳本
└── README.md                 # 本文件
```

---

## 🔐 Secrets Manager 設定

請至 AWS Secrets Manager 建立一個 Secret，格式如下：

- Secret 名稱：`youtube/api/key`
- Secret 內容：

```json
{
  "YOUTUBE_API_KEY": "你的金鑰"
}
```

Lambda 在執行時會自動取用。

---

## 🚀 自動部署流程（CodePipeline）

1. 將本專案 push 至 GitHub repository
2. 登入 AWS Console → CodePipeline → Create Pipeline
3. 設定 GitHub 為來源，並串接此 repo
4. 建立 CodeBuild 專案（使用 buildspec.yml）
5. Deploy 階段使用 CloudFormation，指定 `template.yaml`
6. 不需要額外傳入任何參數，金鑰從 Secrets Manager 取得

---

## 🌐 測試 API 範例

```
GET https://{api-id}.execute-api.{region}.amazonaws.com/Prod/search?q=python&days=7
```

預設 query 為 `genAI`，days 為 `7`，可省略。

---

## 📬 通知設定

部署成功後會寄出 SNS 通知 email 至：

- `joseph.siyi@gmail.com`

---

## 🛡️ IAM 權限需求

Lambda Function 需要以下 IAM 權限：

- `logs:*`（記錄 log 到 CloudWatch）
- `secretsmanager:GetSecretValue`（讀取 YouTube API 金鑰）

這些權限已在 `template.yaml` 中設定。

---

## 📄 授權

MIT License
