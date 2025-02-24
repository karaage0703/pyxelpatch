import pyxel
from src.common.base_node import Node
from src.common.midi_utils import MidiMessage


class SynthNode(Node):
    """シンプルなシンセノード。
    リズムジェネレータからの同期信号に対応。
    """

    def __init__(self):
        super().__init__(name="SimpleSynth", in_channels=[1])

        # 現在鳴っている音
        self.current_note = None

        # シンセ音を設定
        self.sound = pyxel.Sound()
        self.sound.set("c3", "t", "7", "n", 10)
        pyxel.sounds[1] = self.sound

    def on_midi(self, msg: MidiMessage):
        """MIDIメッセージを受信した際の処理"""
        super().on_midi(msg)  # 基本的なMIDI処理

        if not self.enabled:
            return

        if msg.type == "note_on" and msg.velocity > 0:
            self.current_note = msg.note
            # 音を鳴らす
            pyxel.play(1, 1)

        elif msg.type in ["note_off", "note_on"] and msg.velocity == 0:
            self.current_note = None

    def update(self):
        """毎フレーム実行されるメインロジック"""
        # Zキーでシンセのノートオン
        if pyxel.btnp(pyxel.KEY_Z):
            msg = MidiMessage(type="note_on", note=60, velocity=127, channel=1)
            self.on_midi(msg)

        # Zキーを離したらノートオフ
        if pyxel.btnr(pyxel.KEY_Z):
            msg = MidiMessage(type="note_off", note=60, velocity=0, channel=1)
            self.on_midi(msg)

    def draw(self):
        """シンセの状態を可視化"""
        super().draw()  # 基本的な状態表示

        # 現在の音を表示
        y = 30
        if self.current_note is not None:
            pyxel.text(5, y, f"Note: {self.current_note}", 7)
        else:
            pyxel.text(5, y, "Note: None", 5)

        # 操作説明
        pyxel.text(5, 100, "Z: Play Synth", 7)


if __name__ == "__main__":
    SynthNode().run()
