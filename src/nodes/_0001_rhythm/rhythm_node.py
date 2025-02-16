import pyxel
from src.common.base_node import Node
from src.common.midi_utils import MidiNode, SYNTH_PORT, RHYTHM_PORT, MidiMessage


class RhythmNode(Node):
    """シンプルな4ステップのリズムノード"""

    def __init__(self):
        super().__init__(name="SimpleRhythm")
        # Pyxelの初期化
        pyxel.init(160, 120, title="Rhythm Node")

        # 4ステップの基本パターン [キック, 休符, キック, 休符]
        self.pattern = [1, 0, 1, 0]
        self.step = 0

        # 基本的なドラム音を設定
        self.sound = pyxel.Sound()
        self.sound.set("c2", "p", "7", "n", 5)
        pyxel.sounds[0] = self.sound

        # MIDIノードの初期化
        self.midi_node = MidiNode(RHYTHM_PORT, self.on_midi)

    def update(self):
        """毎フレーム実行されるメインロジック"""
        # スペースキーでリズムのON/OFF切り替え
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.toggle_enabled()

        if not self.enabled:
            return

        # 8フレームごとに次のステップへ
        if pyxel.frame_count % 8 == 0:
            if self.pattern[self.step] == 1:
                # ドラム音を再生
                pyxel.play(0, 0)

                # MIDIメッセージを送信
                msg = MidiMessage(
                    type="note_on",
                    note=36,  # キックドラム
                    velocity=127,
                    channel=10,
                    control=None,
                    value=None,
                )
                self.midi_node.send_message(msg, SYNTH_PORT)

            # 次のステップへ
            self.step = (self.step + 1) % len(self.pattern)

    def draw(self):
        """パターンの可視化"""
        pyxel.cls(0)

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

        # 操作説明
        pyxel.text(5, 5, "SPACE: Toggle Rhythm", 7)

    def toggle_enabled(self):
        """リズムのON/OFF切り替え"""
        self.enabled = not self.enabled

    def run(self):
        """アプリケーションの実行"""
        try:
            pyxel.run(self.update, self.draw)
        finally:
            # 終了時にMIDIノードをクローズ
            self.midi_node.close()


if __name__ == "__main__":
    RhythmNode().run()
