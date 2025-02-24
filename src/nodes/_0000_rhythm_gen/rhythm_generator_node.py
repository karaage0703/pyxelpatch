import time
import pyxel
from src.common.base_node import Node
from src.common.midi_utils import (
    MidiMessage,
    MidiNode,
    MIDI_CLOCK,
    MIDI_START,
    MIDI_STOP,
)


class RhythmGeneratorNode(Node):
    """システムのマスタークロックとして動作するリズムジェネレータ。

    同期信号を生成し、他のノードに送信することで同期を実現する。
    """

    def __init__(self):
        super().__init__("RhythmGenerator")

        # MIDI通信
        self.midi = MidiNode("rhythm_generator", self.on_midi)

        # テンポ管理
        self.bpm = 120
        self.running = False
        self.ppq_count = 0  # Pulses Per Quarter note カウンタ

        # タイミング管理
        self.last_clock = 0
        self.clock_interval = self._calculate_clock_interval()
        self.accumulated_time = 0

        # Pyxel初期化
        pyxel.init(160, 120, title="Rhythm Generator")
        pyxel.mouse(True)  # マウス操作を有効化

        # UI状態
        self.dragging = False
        self.drag_start_y = 0
        self.drag_start_bpm = 0

    def _calculate_clock_interval(self) -> float:
        """現在のBPMからMIDIクロック間隔を計算"""
        # BPMから1拍の長さ（秒）を計算
        beat_duration = 60.0 / self.bpm
        # 1拍を24分割（MIDI規格）した間隔を返す
        return beat_duration / 24.0

    def update(self):
        """毎フレーム実行される更新処理"""
        # マウス操作によるBPM制御
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.dragging = True
            self.drag_start_y = pyxel.mouse_y
            self.drag_start_bpm = self.bpm
        elif pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
            if self.dragging:
                # マウスのY座標の変化からBPMを調整（上下反転）
                delta_y = self.drag_start_y - pyxel.mouse_y
                new_bpm = self.drag_start_bpm + delta_y
                self.bpm = max(40, min(240, new_bpm))  # BPMを40-240の範囲に制限
                self.clock_interval = self._calculate_clock_interval()
        else:
            self.dragging = False

        # スペースキーで再生/停止を切り替え
        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.running:
                self.stop()
            else:
                self.start()

        # クロック信号の生成
        if self.running:
            current_time = time.time()
            elapsed = current_time - self.last_clock
            self.accumulated_time += elapsed

            # 累積時間がクロック間隔を超えた場合にクロックを送信
            while self.accumulated_time >= self.clock_interval:
                self.send_clock()
                self.accumulated_time -= self.clock_interval

            self.last_clock = current_time

    def draw(self):
        """毎フレーム実行される描画処理"""
        pyxel.cls(0)

        # 現在のBPMを表示
        pyxel.text(10, 10, f"BPM: {self.bpm:.1f}", 7)

        # 再生状態を表示
        status = "RUNNING" if self.running else "STOPPED"
        pyxel.text(10, 20, f"Status: {status}", 7)

        # PPQカウント表示（デバッグ用）
        pyxel.text(10, 30, f"PPQ: {self.ppq_count}", 7)

        # クロック間隔を表示（デバッグ用）
        pyxel.text(10, 40, f"Interval: {self.clock_interval * 1000:.1f}ms", 7)

        # 操作方法を表示
        pyxel.text(10, 100, "SPACE: Start/Stop", 13)
        pyxel.text(10, 110, "DRAG: Change BPM (40-240)", 13)

    def send_clock(self):
        """MIDIクロック信号を送信"""
        msg = MidiMessage(type=MIDI_CLOCK)
        self.midi.send_message(msg)

        # PPQカウントを更新
        self.ppq_count = (self.ppq_count + 1) % 24

    def start(self):
        """再生を開始"""
        self.running = True
        self.last_clock = time.time()
        self.accumulated_time = 0
        # 開始信号を送信
        msg = MidiMessage(type=MIDI_START)
        self.midi.send_message(msg)

    def stop(self):
        """再生を停止"""
        self.running = False
        self.ppq_count = 0
        self.accumulated_time = 0
        # 停止信号を送信
        msg = MidiMessage(type=MIDI_STOP)
        self.midi.send_message(msg)

    def on_midi(self, msg: MidiMessage):
        """MIDIメッセージを受信した際の処理"""
        # 現状は外部からのMIDI入力は想定しない
        pass


if __name__ == "__main__":
    node = RhythmGeneratorNode()
    pyxel.run(node.update, node.draw)
