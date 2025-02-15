import pyxel
from src.rhythm.rhythm_node import RhythmNode
from src.midi_utils import MidiNode, RHYTHM_PORT


class RhythmApp:
    def __init__(self):
        pyxel.init(160, 120, title="Rhythm Node")

        # MIDIノードの初期化
        self.midi_node = MidiNode(RHYTHM_PORT, self.on_midi_message)

        # リズムノードの初期化
        self.rhythm = RhythmNode(midi_node=self.midi_node)

    def on_midi_message(self, msg):
        """MIDIメッセージを受信した際の処理"""
        self.rhythm.on_midi(msg)

    def update(self):
        # スペースキーでリズムのON/OFF切り替え
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.rhythm.toggle_enabled()

        self.rhythm.update()

    def draw(self):
        pyxel.cls(0)
        self.rhythm.draw()

        # 操作説明
        pyxel.text(5, 5, "SPACE: Toggle Rhythm", 7)

    def run(self):
        try:
            pyxel.run(self.update, self.draw)
        finally:
            # 終了時にMIDIノードをクローズ
            self.midi_node.close()


if __name__ == "__main__":
    RhythmApp().run()
