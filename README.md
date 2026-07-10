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

## 注目すべき米国上場銘柄候補（噂監視リスト）

> これは投資助言ではなく、コミュニティ投稿・ニュース・M&A観測などの未確認情報を監視するための初期候補です。実運用では、EDGAR、公式IR、市場データ、複数コミュニティでの同時発生を必ず照合してください。

| 銘柄コード | 会社名 | 推薦理由となる噂のサマリ | 噂記事・投稿へのリンク |
| --- | --- | --- | --- |
| TSLA | Tesla, Inc. | SpaceXとの将来的な統合・合併可能性について複数アナリストが言及しており、AI計算基盤、エネルギー貯蔵、Elon Musk関連企業間のシナジーが噂の中心です。M&A文脈、公式書類タイミング、オプション異常値を重点監視します。 | https://www.marketwatch.com/story/teslas-stock-could-rise-20-thanks-to-the-potential-for-a-spacex-merger-analyst-says-0d64693e |
| NOK | Nokia Oyj | Redditで「Nvidia追加投資」「米国政府の出資」「AIインフラ化」など複数の噂が整理されており、通信インフラ・AIインフラ文脈のコミュニティ発生源として監視価値があります。 | https://www.reddit.com/r/wallstreetbets/comments/1tfxv2g/addressing_5_rumors_circling_nok_right_now/ |
| RKLB | Rocket Lab USA, Inc. | SpaceX型の垂直統合宇宙プラットフォームへ進化するとのアナリスト評価が出ており、衛星サービス、買収、宇宙インフラ拡張の思惑が強い銘柄です。技術・契約・買収文脈で監視します。 | https://www.marketwatch.com/story/rocket-labs-stock-could-surge-250-as-the-company-takes-a-page-out-of-spacexs-book-analyst-says-3b4f8a4f |
| SOFI | SoFi Technologies, Inc. | M&A活況のなか、成長率の高いフィンテック銘柄として買収候補リストに挙げられています。買収思惑、金融規制、複数コミュニティでの同時発生を監視します。 | https://www.barrons.com/articles/takover-taregt-stocks-merger-boom-7727db11 |
| CAVA | CAVA Group, Inc. | 消費関連の高成長銘柄としてM&A候補リストに含まれており、買収思惑・同業再編・出来高急増を監視する候補です。 | https://www.barrons.com/articles/takover-taregt-stocks-merger-boom-7727db11 |
| BROS | Dutch Bros Inc. | 高成長の外食・消費関連銘柄としてM&A候補リストに挙げられています。買収噂、オプション出来高、SNSでの「takeover」系キーワードを重点監視します。 | https://www.barrons.com/articles/takover-taregt-stocks-merger-boom-7727db11 |
| LMND | Lemonade, Inc. | 高成長企業の買収候補群として言及されており、インシュアテック再編やフィンテックM&Aの噂検出対象として有用です。 | https://www.barrons.com/articles/takover-taregt-stocks-merger-boom-7727db11 |
