# PyxelPatch

PyxelPatchは、Python言語とレトロゲームフレームワーク[Pyxel](https://github.com/kitao/pyxel)を用いて構築する、ノードベースの音楽＆ビジュアルソフトウェアです。複数のノード（アプリケーションのコンポーネント）を組み合わせることで音楽や映像生成を行います。

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

## ライセンス

MIT License

## 作者

@karaage0703
