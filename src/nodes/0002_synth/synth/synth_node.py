import pyxel
from src.base_node import Node
from src.midi_utils import MidiNode, MidiMessage


class SynthNode(Node):
    """シンプルなシンセノード"""

    def __init__(self, midi_node: MidiNode = None):
        super().__init__(name="SimpleSynth", in_channels=[1])
        # 現在鳴っている音
        self.current_note = None

        # シンセ音を設定
        self.sound = pyxel.Sound()
        self.sound.set("c3", "t", "7", "n", 10)
        pyxel.sounds[1] = self.sound

        # MIDIノード
        self.midi_node = midi_node

    def on_midi(self, msg: MidiMessage):
        """MIDIメッセージを受信した際の処理"""
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
        pass

    def draw(self):
        """シンセの状態を可視化"""
        if not self.enabled:
            return

        # 現在の音を表示
        y = 20
        if self.current_note is not None:
            pyxel.text(5, y, f"Note: {self.current_note}", 7)
        else:
            pyxel.text(5, y, "Note: None", 5)
