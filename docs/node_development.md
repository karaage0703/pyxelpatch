# ノード開発ガイド

このガイドでは、PyxelPatchの新しいノードを開発する際の詳細な手順と技術的な考慮事項について説明します。

## 1. ノードの基本構造

### 基底クラス (Node)
すべてのノードは`Node`基底クラスを継承します：

```python
class Node:
    def __init__(self, name, in_channels=None):
        self.name = name
        self.enabled = True
        self.in_channels = in_channels if in_channels else []

    def on_midi(self, msg):
        """MIDIメッセージを受信した際の処理"""
        pass

    def update(self):
        """毎フレーム実行されるメインロジック"""
        pass

    def draw(self):
        """描画処理"""
        pass
```

### 必須メソッド
1. `on_midi(msg)`: MIDIメッセージの受信処理
   - MIDIメッセージを受け取った際の動作を実装
   - 必要に応じて音声再生やパラメーター変更を行う

2. `update()`: フレーム更新処理
   - 毎フレーム呼び出される
   - アニメーションや状態更新などを実装

3. `draw()`: 描画処理
   - Pyxelの描画APIを使用
   - ノードの状態を可視化

## 2. MIDI通信

### MIDIメッセージの送信
```python
# MIDIメッセージの作成
msg = MidiMessage(
    type="note_on",
    note=60,
    velocity=127,
    channel=1,
    control=None,
    value=None
)

# メッセージの送信
self.midi_node.send_message(msg, DEST_PORT)
```

### MIDIメッセージの受信
```python
def on_midi(self, msg):
    if not self.enabled:
        return

    if msg.type == "note_on" and msg.velocity > 0:
        # ノートオンの処理
        self.play_sound()
    elif msg.type == "control_change":
        # コントロールチェンジの処理
        self.update_parameter(msg.control, msg.value)
```

## 3. Pyxelの活用

### サウンド
```python
# サウンドの設定
self.sound = pyxel.Sound()
self.sound.set("c3", "t", "7", "n", 10)
pyxel.sounds[0] = self.sound

# 再生
pyxel.play(0, 0)
```

### グラフィック
```python
def draw(self):
    # 背景クリア
    pyxel.cls(0)

    # 図形描画
    pyxel.rect(x, y, w, h, col)
    pyxel.circ(x, y, r, col)

    # テキスト描画
    pyxel.text(x, y, "テキスト", col)
```

## 4. 実装例

### シンプルなノードの例
```python
class SimpleNode(Node):
    def __init__(self):
        super().__init__(name="SimpleNode", in_channels=[1])
        # Pyxelの初期化
        pyxel.init(160, 120, title="Simple Node")

        self.value = 0

        # サウンド初期化
        self.sound = pyxel.Sound()
        self.sound.set("c3", "t", "7", "n", 10)
        pyxel.sounds[0] = self.sound

        # MIDIノードの初期化
        self.midi_node = MidiNode(PORT_NUMBER, self.on_midi)

    def on_midi(self, msg):
        if not self.enabled:
            return

        if msg.type == "note_on" and msg.velocity > 0:
            self.value = msg.note
            pyxel.play(0, 0)

    def update(self):
        # キーボード入力処理
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.enabled = not self.enabled

    def draw(self):
        pyxel.cls(0)
        pyxel.text(5, 5, f"Value: {self.value}", 7)
        pyxel.text(5, 15, "SPACE: Toggle Enable", 7)

    def run(self):
        """アプリケーションの実行"""
        try:
            pyxel.run(self.update, self.draw)
        finally:
            self.midi_node.close()


if __name__ == "__main__":
    SimpleNode().run()
```

### ノードの実装手順
1. `src/nodes/`以下に番号付きのディレクトリを作成（例: `0003_name`）
2. ノードの実装ファイルとパッケージ初期化ファイルを作成：
   - `node_name.py`: ノードの実装
   - `__init__.py`: 相対インポートの設定

### ノードの実行方法
新しいノードを作成したら、以下のようにモジュールとして実行できます：

```bash
python -m src.nodes.xxxx_name.node_name
```

## 5. デバッグとテスト

### デバッグ表示
```python
def draw(self):
    # 状態の可視化
    pyxel.text(5, 5, f"State: {self.state}", 7)
    pyxel.text(5, 15, f"MIDI In: {self.last_midi}", 7)

    # パラメーターの表示
    pyxel.text(5, 25, f"Param1: {self.param1}", 7)
    pyxel.text(5, 35, f"Param2: {self.param2}", 7)
```

### エラーハンドリング
```python
def on_midi(self, msg):
    try:
        # MIDIメッセージの処理
        if msg.type == "note_on":
            self.handle_note_on(msg)
    except Exception as e:
        print(f"Error in MIDI handling: {e}")
```

## 6. パフォーマンスの考慮

1. 更新処理の最適化
   - 重い処理は`update()`内で分散実行
   - 必要なときのみ処理を実行

2. 描画の効率化
   - 必要な部分のみ再描画
   - 複雑な描画は事前計算

3. メモリ使用
   - 大きなデータは適切に解放
   - 無限に増加する配列などに注意

## 7. ベストプラクティス

1. コードの構造化
   - 機能ごとにメソッドを分割
   - 責務の明確な分離

2. エラー処理
   - 適切な例外処理
   - エラーメッセージの表示

3. ドキュメント
   - コードコメントの充実
   - 使用方法の説明

4. テスト
   - 基本機能のテスト
   - エッジケースの考慮