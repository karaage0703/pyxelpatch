import pyxel
from src.common.base_node import Node
from src.common.midi_utils import (
    MidiNode,
    SYNTH_PORT,
    RHYTHM_PORT,
    MidiMessage,
    MIDI_CLOCK,
    MIDI_START,
    MIDI_STOP,
)


class RhythmNode(Node):
    """シンプルな4ステップのリズムノード。
    リズムジェネレータからの同期信号に基づいて動作する。
    """

    def __init__(self):
        super().__init__(name="SimpleRhythm")
        # Pyxelの初期化
        pyxel.init(160, 120, title="Rhythm Node")

        # 4ステップの基本パターン [キック, 休符, キック, 休符]
        self.pattern = [1, 0, 1, 0]
        self.step = 0

        # 同期関連
        self.synced = False
        self.ppq_count = 0  # Pulses Per Quarter note カウンタ
        self.running = False

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

        # 操作説明
        pyxel.text(5, 100, "SPACE: Toggle Rhythm", 7)

    def on_midi(self, msg: MidiMessage):
        """MIDIメッセージを受信した際の処理"""
        if not self.enabled:
            return

        if msg.type == MIDI_CLOCK:
            self.synced = True
            self.ppq_count = (self.ppq_count + 1) % 24

            # 6PPQごと（16分音符）にステップを進める
            if self.running and self.ppq_count % 6 == 0:
                if self.pattern[self.step] == 1:
                    # ドラム音を再生
                    pyxel.play(0, 0)

                    # MIDIメッセージを送信
                    msg = MidiMessage(
                        type="note_on",
                        note=36,  # キックドラム
                        velocity=127,
                        channel=10,
                    )
                    self.midi_node.send_message(msg, SYNTH_PORT)

                # 次のステップへ
                self.step = (self.step + 1) % len(self.pattern)

        elif msg.type == MIDI_START:
            self.running = True
            self.ppq_count = 0
            self.step = 0

        elif msg.type == MIDI_STOP:
            self.running = False
            self.ppq_count = 0

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
