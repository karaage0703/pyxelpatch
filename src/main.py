import pyxel
from src.rhythm.rhythm_node import RhythmNode
from src.synth.synth_node import SynthNode
from src.base_node import MidiMessage


class App:
    def __init__(self):
        pyxel.init(160, 120, title="PyxelPatch")
        self.rhythm = RhythmNode()
        self.synth = SynthNode()

        # ノードのリスト
        self.nodes = [self.rhythm, self.synth]

    def update(self):
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
        pyxel.cls(0)

        # 各ノードの描画
        for node in self.nodes:
            node.draw()

        # 操作説明
        pyxel.text(5, 5, "SPACE: Toggle Rhythm", 7)
        pyxel.text(5, 12, "Z: Play Synth", 7)

    def run(self):
        pyxel.run(self.update, self.draw)


if __name__ == "__main__":
    App().run()
