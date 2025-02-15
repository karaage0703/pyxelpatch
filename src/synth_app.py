import pyxel
from src.synth.synth_node import SynthNode
from src.midi_utils import MidiNode, SYNTH_PORT, MidiMessage


class SynthApp:
    def __init__(self):
        pyxel.init(160, 120, title="Synth Node")

        # MIDIノードの初期化
        self.midi_node = MidiNode(SYNTH_PORT, self.on_midi_message)

        # シンセノードの初期化
        self.synth = SynthNode(midi_node=self.midi_node)

    def on_midi_message(self, msg):
        """MIDIメッセージを受信した際の処理"""
        self.synth.on_midi(msg)

    def update(self):
        # Zキーでシンセのノートオン
        if pyxel.btnp(pyxel.KEY_Z):
            msg = MidiMessage(type="note_on", note=60, velocity=127, channel=1, control=None, value=None)
            self.synth.on_midi(msg)

        # Zキーを離したらノートオフ
        if pyxel.btnr(pyxel.KEY_Z):
            msg = MidiMessage(type="note_off", note=60, velocity=0, channel=1, control=None, value=None)
            self.synth.on_midi(msg)

        self.synth.update()

    def draw(self):
        pyxel.cls(0)
        self.synth.draw()

        # 操作説明
        pyxel.text(5, 5, "Z: Play Synth", 7)

    def run(self):
        try:
            pyxel.run(self.update, self.draw)
        finally:
            # 終了時にMIDIノードをクローズ
            self.midi_node.close()


if __name__ == "__main__":
    SynthApp().run()
