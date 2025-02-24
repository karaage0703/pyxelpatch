import pyxel
from src.common.midi_utils import MidiMessage, MidiNode, MIDI_CLOCK, MIDI_START, MIDI_STOP


class Node:
    """PyxelPatchのすべてのノードが継承する基底クラス。"""

    def __init__(self, name, window_size=(160, 120), in_channels=None):
        self.name = name
        self.enabled = True
        # ノードが受信するMIDIチャンネル一覧 (None or [] は全チャンネル受信の例)
        self.in_channels = in_channels if in_channels else []
        # このノードが発生させるMIDIイベントの一時キュー
        self.output_events = []

        # Pyxelの初期化
        self.window_width, self.window_height = window_size
        pyxel.init(self.window_width, self.window_height, title=f"PyxelPatch - {name}")

        # MIDI同期関連の状態
        self.synced = False
        self.ppq_count = 0  # Pulses Per Quarter note カウンタ
        self.running = False

        # MIDIノードの初期化
        self.midi_node = MidiNode(name.lower(), self.on_midi)

    def set_enabled(self, state: bool):
        """ノードの有効/無効を設定"""
        self.enabled = state

    def toggle_enabled(self):
        """ノードの有効/無効を切り替え"""
        self.enabled = not self.enabled

    def on_midi(self, msg: MidiMessage):
        """外部または他ノードから来るMIDIイベントを処理。サブクラスでオーバーライド。"""
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

    def update(self):
        """Pyxelのupdate()内で毎フレーム呼ばれる。各ノード固有のロジックを処理。"""
        pass

    def draw(self):
        """Pyxelのdraw()内で毎フレーム呼ばれる。各ノード固有の描画処理。"""
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

    def run(self):
        """アプリケーションの実行"""
        try:
            pyxel.run(self.update, self.draw)
        finally:
            # 終了時にMIDIノードをクローズ
            self.midi_node.close()
