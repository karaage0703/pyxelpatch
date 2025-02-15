from src.midi_utils import MidiMessage


class Node:
    """PyxelPatchのすべてのノードが継承する基底クラス。"""

    def __init__(self, name, in_channels=None):
        self.name = name
        self.enabled = True
        # ノードが受信するMIDIチャンネル一覧 (None or [] は全チャンネル受信の例)
        self.in_channels = in_channels if in_channels else []
        # このノードが発生させるMIDIイベントの一時キュー
        self.output_events = []

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

    def update(self):
        """Pyxelのupdate()内で毎フレーム呼ばれる。各ノード固有のロジックを処理。"""
        pass

    def draw(self):
        """Pyxelのdraw()内で毎フレーム呼ばれる。各ノード固有の描画処理。"""
        pass
