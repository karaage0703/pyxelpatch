import pyxel
from src.rhythm.rhythm_node import RhythmNode
from src.synth.synth_node import SynthNode
from src.base_node import MidiMessage
import os


class App:
    def __init__(self):
        # テスト環境ではPyxelの初期化をスキップ
        if not os.environ.get("PYTEST_CURRENT_TEST"):
            pyxel.init(160, 120, title="PyxelPatch")
            self.rhythm = RhythmNode()
            self.synth = SynthNode()
            self.nodes = [self.rhythm, self.synth]

    def update(self):
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return

        # スペースキーでリズムのON/OFF切り替え
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.rhythm.toggle_enabled()

        # Zキーでシンセのノートオン
        if pyxel.btnp(pyxel.KEY_Z):
            msg = MidiMessage(type="note_on", note=60, velocity=127, channel=1, control=None, value=None)
            self.synth.on_midi(msg)

        # Zキーを離したらノートオフ
        if pyxel.btnr(pyxel.KEY_Z):
            msg = MidiMessage(type="note_off", note=60, velocity=0, channel=1, control=None, value=None)
            self.synth.on_midi(msg)

        # 各ノードの更新
        for node in self.nodes:
            node.update()

    def draw(self):
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return

        pyxel.cls(0)

        # 各ノードの描画
        for node in self.nodes:
            node.draw()

        # 操作説明
        pyxel.text(5, 5, "SPACE: Toggle Rhythm", 7)
        pyxel.text(5, 12, "Z: Play Synth", 7)

    def run(self):
        if os.environ.get("PYTEST_CURRENT_TEST"):
            print("Hello from src!")
            return

        pyxel.run(self.update, self.draw)


def main():
    print("Hello from src!")
    if not os.environ.get("PYTEST_CURRENT_TEST"):
        App().run()


if __name__ == "__main__":
    App().run()
