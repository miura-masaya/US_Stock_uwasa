# US Stock Uwasa

米国株の噂・未確認情報を収集し、NLPで分類し、信頼度をスコアリングして通知するためのPython骨格実装です。

## ディレクトリ構造

```text
collector/   Reddit、Stocktwits、X、市場データ、EDGARの収集層
nlp/         キーワード抽出、文脈分類、Bot・ノイズ除去
scoring/     信頼度スコア計算
notifier/    Slack Webhook、Email通知
data/        JSON出力先
main.py      全体統合のエントリポイント
```

## 実行

```bash
python main.py
```
