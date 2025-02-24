import pyxel
from src.common.base_node import Node
from src.common.midi_utils import MidiMessage


class RhythmNode(Node):
    """シンプルな4ステップのリズムノード。
    リズムジェネレータからの同期信号に基づいて動作する。
    """

    def __init__(self):
        super().__init__(name="SimpleRhythm")

        # 4ステップの基本パターン [キック, 休符, キック, 休符]
        self.pattern = [1, 0, 1, 0]
        self.step = 0

        # 基本的なドラム音を設定
        self.sound = pyxel.Sound()
        self.sound.set("c2", "p", "7", "n", 5)
        pyxel.sounds[0] = self.sound

    def update(self):
        """毎フレーム実行されるメインロジック"""
        # スペースキーでリズムのON/OFF切り替え
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.toggle_enabled()

    def draw(self):
        """パターンの可視化"""
        super().draw()  # 基本的な状態表示

        # パターンを画面下部に表示
        y = pyxel.height - 20
        for i, val in enumerate(self.pattern):
            x = 10 + i * 20
            color = 7 if val == 1 else 5  # 白と暗めの色
            if i == self.step:
                color = 8  # 現在のステップは赤
            pyxel.rect(x, y, 16, 16, color)

        # 操作説明
        pyxel.text(5, 100, "SPACE: Toggle Rhythm", 7)

    def on_midi(self, msg: MidiMessage):
        """MIDIメッセージを受信した際の処理"""
        super().on_midi(msg)  # 基本的なMIDI処理

        if not self.enabled:
            return

        # 6PPQごと（16分音符）にステップを進める
        if msg.type == "clock" and self.running and self.ppq_count % 6 == 0:
            # 次のステップへ
            self.step = (self.step + 1) % len(self.pattern)

            # 新しいステップの音を処理
            if self.pattern[self.step] == 1:
                # ドラム音を再生
                pyxel.play(0, 0)

        elif msg.type == "start":
            self.step = 0
            # 最初のステップの音を処理
            if self.pattern[self.step] == 1:
                pyxel.play(0, 0)


if __name__ == "__main__":
    RhythmNode().run()
