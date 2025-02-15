# Contributing to PyxelPatch

PyxelPatchへの開発参加を歓迎します！このドキュメントでは、新しいノードの開発やプロジェクトへの貢献方法について説明します。

## 開発の始め方

1. リポジトリをフォーク
2. 開発環境のセットアップ
   ```bash
   git clone https://github.com/YOUR_USERNAME/pyxelpatch.git
   cd pyxelpatch
   pip install -e .
   ```
3. 新しいブランチを作成
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 新しいノードの作成方法

### 1. ディレクトリ構造
新しいノードを作成する場合、以下のような構造にしたがってください：
```
src/
  └── your_node/
       ├── __init__.py
       └── your_node.py
```

### 2. 基底クラスの継承
すべてのノードは`Node`基底クラスを継承する必要があります：
```python
from src.base_node import Node, MidiMessage

class YourNode(Node):
    def __init__(self):
        super().__init__(name="YourNodeName")
        # ノード固有の初期化
```

### 3. 必須メソッドの実装
以下のメソッドを実装してください：
- `update()`: 毎フレーム実行されるメインロジック
- `draw()`: 描画処理
- `on_midi(msg)`: MIDIメッセージを受信した際の処理

### 4. アプリケーションファイルの作成
ノードを実行するための`your_node_app.py`を作成：
```python
import pyxel
from src.your_node.your_node import YourNode
from src.midi_utils import MidiNode, YOUR_NODE_PORT

class YourNodeApp:
    def __init__(self):
        pyxel.init(160, 120, title="Your Node")
        self.midi_node = MidiNode(YOUR_NODE_PORT, self.on_midi_message)
        self.node = YourNode(midi_node=self.midi_node)
        # ...
```

## MIDI通信の仕様

### ポート番号の割り当て
- RhythmNode: 5000
- SynthNode: 5001
- 新規ノード: 5002以降を使用

### MIDIメッセージフォーマット
```python
MidiMessage(
    type="note_on",  # "note_on", "note_off", "control_change"など
    note=60,         # ノート番号（0-127）
    velocity=127,    # ベロシティ（0-127）
    channel=1,       # MIDIチャンネル（1-16）
    control=None,    # コントロール番号（0-127）
    value=None       # コントロール値（0-127）
)
```

## プルリクエストのガイドライン

1. コーディング規約
   - PEP8に準拠
   - ruffによる自動フォーマット
   - 日本語でのコメント推奨

2. プルリクエストの内容
   - 変更内容の簡潔な説明
   - 動作確認方法の記載
   - スクリーンショットや動画（UI変更がある場合）

3. レビュープロセス
   - CIチェックの通過確認
   - コードレビューへの対応
   - 必要に応じたドキュメント更新

## ドキュメント

新しいノードを追加する場合、以下のドキュメントも更新してください：

1. README.md
   - 新ノードの概要と特徴
   - 実行方法と操作方法

2. docs/ディレクトリ
   - ノードの詳細な仕様
   - 実装の解説
   - 使用例

## 質問・フィードバック

- Issueを作成して質問やフィードバックを投稿
- Discussionsでアイデアや提案を共有

ご協力ありがとうございます！