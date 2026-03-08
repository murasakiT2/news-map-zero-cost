# World News Map (0円構成)

## 構成
- GitHub Pages: 静的配信
- GitHub Actions: 30分ごとにRSS収集
- D3 + TopoJSON: 世界地図描画
- Natural Earth / world-atlas 系データ: 国ポリゴン表示

## 使い方
1. このリポジトリを **public** で作成
2. 中身を push
3. GitHub Pages を `Deploy from a branch` / `main` / `/root` に設定
4. Actions を有効化
5. `update-news` を手動実行

## 0円を守る注意
- リポジトリは public にする
- GitHub-hosted runner の無料条件は public repository 前提
- OSM 公開タイルは使わない
- 地図はポリゴン塗り分けだけで構成する

## 精度改善ポイント
- `COUNTRY_PATTERNS` に地名を追加
- 同一事件クラスタリング用の `event_hash` を追加
- 日本語ソースを追加する場合は RSS 利用条件を確認
