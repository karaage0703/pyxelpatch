# ノード実装例

このドキュメントでは、PyxelPatchで実装されているノードの具体例を紹介します。これらの例を参考に、新しいノードを開発できます。

## 1. リズムノード (RhythmNode)

### 概要
- 4ステップのリズムパターンを生成
- MIDIメッセージでドラム音を送信
- パターンを可視化

### 実装例
```python
class RhythmNode(Node):
    def __init__(self, midi_node: MidiNode = None):
        super().__init__(name="SimpleRhythm")
        self.pattern = [1, 0, 1, 0]  # 4ステップのパターン
        self.step = 0

        # 基本的なドラム音を設定
        self.sound = pyxel.Sound()
        self.sound.set("c2", "p", "7", "n", 5)
        pyxel.sounds[0] = self.sound

        # MIDIノード
        self.midi_node = midi_node

    def update(self):
        if not self.enabled:
            return

        # 8フレームごとに次のステップへ
        if pyxel.frame_count % 8 == 0:
            if self.pattern[self.step] == 1:
                # ドラム音を再生
                pyxel.play(0, 0)

                # MIDIメッセージを送信
                if self.midi_node:
                    msg = MidiMessage(
                        type="note_on",
                        note=36,  # キックドラム
                        velocity=127,
                        channel=10,
                        control=None,
                        value=None
                    )
                    self.midi_node.send_message(msg, SYNTH_PORT)

            # 次のステップへ
            self.step = (self.step + 1) % len(self.pattern)

    def draw(self):
        if not self.enabled:
            return

        # パターンを画面下部に表示
        y = pyxel.height - 20
        for i, val in enumerate(self.pattern):
            x = 10 + i * 20
            color = 7 if val == 1 else 5  # 白と暗めの色
            if i == self.step:
                color = 8  # 現在のステップは赤
            pyxel.rect(x, y, 16, 16, color)
```

## 2. シンセノード (SynthNode)

### 概要
- MIDIノート入力による音声生成
- トライアングル波による音色
- 現在の音程を表示

### 実装例
```python
class SynthNode(Node):
    def __init__(self, midi_node: MidiNode = None):
        super().__init__(name="SimpleSynth", in_channels=[1])
        self.current_note = None

        # シンセ音を設定
        self.sound = pyxel.Sound()
        self.sound.set("c3", "t", "7", "n", 10)
        pyxel.sounds[1] = self.sound

        # MIDIノード
        self.midi_node = midi_node

    def on_midi(self, msg: MidiMessage):
        if not self.enabled:
            return

        if msg.type == "note_on" and msg.velocity > 0:
            self.current_note = msg.note
            # 音を鳴らす
            pyxel.play(1, 1)
        elif msg.type in ["note_off", "note_on"] and msg.velocity == 0:
            self.current_note = None

    def draw(self):
        if not self.enabled:
            return

        # 現在の音を表示
        y = 20
        if self.current_note is not None:
            pyxel.text(5, y, f"Note: {self.current_note}", 7)
        else:
            pyxel.text(5, y, "Note: None", 5)
```

## 3. 新しいノードの作成例

### エフェクトノード
```python
class EffectNode(Node):
    def __init__(self, midi_node: MidiNode = None):
        super().__init__(name="Effect", in_channels=[1])
        self.intensity = 0
        self.particles = []
        self.midi_node = midi_node

    def on_midi(self, msg: MidiMessage):
        if not self.enabled:
            return

        if msg.type == "note_on" and msg.velocity > 0:
            # ノートの高さに応じてエフェクトの強度を変更
            self.intensity = msg.velocity / 127.0
            # パーティクルを生成
            self.generate_particles()

    def generate_particles(self):
        # エフェクトの強度に応じてパーティクルを生成
        num_particles = int(self.intensity * 10)
        for _ in range(num_particles):
            self.particles.append({
                'x': pyxel.rndi(0, pyxel.width),
                'y': pyxel.rndi(0, pyxel.height),
                'life': 30
            })

    def update(self):
        if not self.enabled:
            return

        # パーティクルの更新
        for p in list(self.particles):
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)

    def draw(self):
        if not self.enabled:
            return

        # パーティクルの描画
        for p in self.particles:
            size = int(p['life'] / 10)
            pyxel.circ(p['x'], p['y'], size, 8)

        # エフェクト強度の表示
        pyxel.text(5, 5, f"Effect: {self.intensity:.2f}", 7)
```

## 4. アプリケーションの作成例

### ノードアプリケーション
```python
class NodeApp:
    def __init__(self, port: int, title: str):
        pyxel.init(160, 120, title=title)

        # MIDIノードの初期化
        self.midi_node = MidiNode(port, self.on_midi_message)

        # ノードの初期化
        self.node = YourNode(midi_node=self.midi_node)

    def on_midi_message(self, msg):
        """MIDIメッセージを受信した際の処理"""
        self.node.on_midi(msg)

    def update(self):
        # ノードの更新
        self.node.update()

    def draw(self):
        pyxel.cls(0)
        self.node.draw()

    def run(self):
        try:
            pyxel.run(self.update, self.draw)
        finally:
            # 終了時にMIDIノードをクローズ
            self.midi_node.close()

if __name__ == "__main__":
    NodeApp(5002, "Your Node").run()
```

これらの実装例を参考に、独自のノードを開発できます。新しいノードを作成する際は、以下の点に注意してください：

1. 基底クラス`Node`を継承
2. 必須メソッド（`on_midi`, `update`, `draw`）の実装
3. MIDIメッセージの適切な処理
4. 効率的な描画処理
5. エラーハンドリング

また、新しいノードを作成した際は、ドキュメントの更新もお願いします。