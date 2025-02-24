import pyxel
from src.common.base_node import Node
from src.common.midi_utils import (
    MidiNode,
    MidiMessage,
    MIDI_CLOCK,
    MIDI_START,
    MIDI_STOP,
)


class SynthNode(Node):
    """シンプルなシンセノード。
    リズムジェネレータからの同期信号に対応。
    """

    def __init__(self):
        super().__init__(name="SimpleSynth", in_channels=[1])
        # Pyxelの初期化
        pyxel.init(160, 120, title="Synth Node")

        # 現在鳴っている音
        self.current_note = None

        # 同期関連
        self.synced = False
        self.ppq_count = 0  # Pulses Per Quarter note カウンタ
        self.running = False

        # シンセ音を設定
        self.sound = pyxel.Sound()
        self.sound.set("c3", "t", "7", "n", 10)
        pyxel.sounds[1] = self.sound

        # MIDIノードの初期化
        self.midi_node = MidiNode("synth", self.on_midi)

    def on_midi(self, msg: MidiMessage):
        """MIDIメッセージを受信した際の処理"""
        if not self.enabled:
            return

        if msg.type == MIDI_CLOCK:
            self.synced = True
            self.ppq_count = (self.ppq_count + 1) % 24

        elif msg.type == MIDI_START:
            self.running = True
            self.ppq_count = 0

        elif msg.type == MIDI_STOP:
            self.running = False
            self.ppq_count = 0

        elif msg.type == "note_on" and msg.velocity > 0:
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
        pyxel.cls(0)

        if not self.enabled:
            return

        # 状態表示
        status = []
        if not self.synced:
            status.append("WAITING FOR SYNC")
        elif not self.running:
            status.append("STOPPED")
        elif not self.enabled:
            status.append("DISABLED")
        else:
            status.append("RUNNING")

        status_text = " | ".join(status)
        pyxel.text(5, 5, status_text, 7)

        # PPQカウント表示（デバッグ用）
        pyxel.text(5, 15, f"PPQ: {self.ppq_count}", 7)

        # 現在の音を表示
        y = 30
        if self.current_note is not None:
            pyxel.text(5, y, f"Note: {self.current_note}", 7)
        else:
            pyxel.text(5, y, "Note: None", 5)

        # 操作説明
        pyxel.text(5, 100, "Z: Play Synth", 7)

    def run(self):
        """アプリケーションの実行"""
        try:
            pyxel.run(self.update, self.draw)
        finally:
            # 終了時にMIDIノードをクローズ
            self.midi_node.close()


if __name__ == "__main__":
    SynthNode().run()
