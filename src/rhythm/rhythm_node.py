import pyxel
from src.base_node import Node, MidiMessage


class RhythmNode(Node):
    """シンプルな4ステップのリズムノード"""

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
        if not self.enabled:
            return

        # 8フレームごとに次のステップへ
        if pyxel.frame_count % 8 == 0:
            if self.pattern[self.step] == 1:
                # ドラム音を再生
                pyxel.play(0, 0)

            # 次のステップへ
            self.step = (self.step + 1) % len(self.pattern)

    def draw(self):
        """パターンの可視化"""
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
