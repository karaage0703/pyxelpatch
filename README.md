# PyxelPatch

PyxelPatchは、Python言語とレトロゲームフレームワーク[Pyxel](https://github.com/kitao/pyxel)を用いて構築する、ノードベースの音楽＆ビジュアルソフトウェアです。Cycling '74のMax (Max/MSP)に着想を得ており、複数のノード（アプリケーションのコンポーネント）を組み合わせることで音楽や映像生成を行います。

## 特徴

- 各ノードが独立したウィンドウで動作
- UDPソケットを使用したMIDIメッセージによるノード間通信
- Pyxelによるレトロスタイルの音声・グラフィック生成
- 拡張可能なノードベースアーキテクチャ

## 実装済みノード

詳細なノードの情報は [src/nodes/README.md](src/nodes/README.md) をご覧ください。

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/karaage0703/pyxelpatch
cd pyxelpatch

# 開発モードでインストール
pip install -e .
```

## 開発予定の機能

- 映像ジェネレータノード (VideoNode)
- ゲームノード (GameNode)
- OSCによる外部ソフトウェアとの連携
- GUI接続管理システム
- 外部MIDIデバイス対応

## 開発者向けドキュメント

PyxelPatchは開発者の貢献を歓迎します。以下のドキュメントを参照してください：

- [設計書](docs/design_document.md) - システム全体の設計と構成
- [ノード開発ガイド](docs/node_development.md) - 技術仕様と実装方法
- [実装例](docs/example_nodes.md) - 具体的なノードの実装例
- [要件定義](docs/requirements_prompt.md) - プロジェクトの要件定義
- [開発参加ガイド](CONTRIBUTING.md) - プロジェクトへの参加方法

## ライセンス

MIT License

## 作者

@karaage0703