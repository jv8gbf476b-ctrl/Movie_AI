# Movie_AI

AI video prompt assistant.

## 目的

Movie_AIは、写真やシーンの希望から、Kling / Runway / Pika などの動画生成AIで使える高品質な英語プロンプトを作るためのAIアシスタント。

動画生成AIそのものを自作するのではなく、既存の動画生成サービスを使いやすくする「動画監督AI」を目指す。

## 開発方針

- Pythonで作る
- GitHubで管理する
- BO_AIとは別プロジェクトとして育てる
- 最初はプロンプト生成に特化する
- 後から写真解析AIや動画生成サービス連携を追加する

## Ver.1 目標

- 写真①をアップロード
- 写真②をアップロード
- シーンを選択
- 雰囲気を選択
- Kling / Runway / Pika向けの英語プロンプトを生成
- コピーしやすく表示する

## Ver.2 目標

- AIが写真を解析する
- 人物の特徴を自動で説明する
- 手入力を減らす

## Ver.3 目標

- AIが写真に合うシーンを提案する
- 海辺、夜景、カフェ、旅行、映画風などを自動提案する

## Ver.4 目標

- Kling / Runway / Pika などの動画生成サービスと連携する
- Movie_AI内から動画生成まで進められるようにする

## ファイル構成予定

```text
Movie_AI/
├── app.py
├── prompts.py
├── image_ai.py
├── config.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── script.js
└── uploads/
