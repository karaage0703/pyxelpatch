import pyxel
from dataclasses import dataclass
from typing import Dict, List
from src.common.base_node import Node
from src.common.midi_utils import (
    MidiNode,
    ADVANCED_RHYTHM_PORT,
    MidiMessage,
    MIDI_CLOCK,
    MIDI_START,
    MIDI_STOP,
)


@dataclass
class DrumSound:
    """ドラム音の設定を保持するデータクラス"""

    name: str
    note: int  # MIDIノート番号
    sound_id: int  # Pyxel sound ID
    volume: int  # 0-100
    pattern: List[int]  # ステップパターン
    muted: bool  # ミュート状態


class AdvancedRhythmNode(Node):
    """高度な機能を持つリズムノード。

    - 複数の音色（キック、スネア、ハイハット、クラップ）
    - パターン切り替え機能
    - 音量調整機能
    """

    def __init__(self):
        super().__init__(name="AdvancedRhythm")
        # Pyxelの初期化
        pyxel.init(240, 180, title="Advanced Rhythm Node")

        # ドラム音の初期化
        self._init_drum_sounds()

        # 同期関連
        self.synced = False
        self.ppq_count = 0  # Pulses Per Quarter note カウンタ
        self.running = False
        self.step = 0

        # パターンバンク（各ドラム音ごとに複数のパターンを保持）
        self.pattern_banks = {
            "kick": [
                [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # 基本的な4つ打ち
                [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0],  # 変化系1
                [1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0],  # 変化系2
            ],
            "snare": [
                [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],  # 基本的な裏打ち
                [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0],  # 変化系1
                [0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0],  # 変化系2
            ],
            "hihat": [
                [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 基本的な16ビート
                [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],  # 8ビート
                [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1],  # 変化系
            ],
            "clap": [
                [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],  # 基本的な裏打ち
                [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1],  # 変化系1
                [0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1],  # 変化系2
            ],
        }

        # 現在のパターン番号
        self.current_pattern = {name: 0 for name in self.drums.keys()}

        # MIDIノードの初期化
        self.midi_node = MidiNode(ADVANCED_RHYTHM_PORT, self.on_midi)

    def _init_drum_sounds(self):
        """ドラム音の初期化"""
        self.drums: Dict[str, DrumSound] = {
            "kick": DrumSound(
                name="Kick",
                note=36,  # C1
                sound_id=0,
                volume=100,
                pattern=[1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
                muted=False,
            ),
            "snare": DrumSound(
                name="Snare",
                note=38,  # D1
                sound_id=1,
                volume=100,
                pattern=[0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                muted=False,
            ),
            "hihat": DrumSound(
                name="HiHat",
                note=42,  # F#1
                sound_id=2,
                volume=100,
                pattern=[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                muted=False,
            ),
            "clap": DrumSound(
                name="Clap",
                note=39,  # D#1
                sound_id=3,
                volume=100,
                pattern=[0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                muted=False,
            ),
        }

        # キックドラム
        kick = pyxel.Sound()
        kick.set("c2", "p", "7", "n", 5)
        pyxel.sounds[0] = kick

        # スネアドラム
        snare = pyxel.Sound()
        snare.set("c3", "n", "7", "n", 8)
        pyxel.sounds[1] = snare

        # ハイハット
        hihat = pyxel.Sound()
        hihat.set("f3", "s", "7", "n", 2)
        pyxel.sounds[2] = hihat

        # クラップ
        clap = pyxel.Sound()
        clap.set("d3", "n", "7", "f", 3)
        pyxel.sounds[3] = clap

    def update(self):
        """毎フレーム実行されるメインロジック"""
        # スペースキーでリズムのON/OFF切り替え
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.toggle_enabled()

        # 1-4キーでミュート切り替え
        for i, key in enumerate([pyxel.KEY_1, pyxel.KEY_2, pyxel.KEY_3, pyxel.KEY_4]):
            if pyxel.btnp(key):
                self._toggle_mute(list(self.drums.keys())[i])

        # マウスクリックでパターン切り替え
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # クリックされた位置を確認
            for i, (name, drum) in enumerate(self.drums.items()):
                base_y = 40 + i * 30
                if base_y <= pyxel.mouse_y <= base_y + 8:
                    # パターン領域内でのクリックを確認
                    pattern_x = (pyxel.mouse_x - 60) // 10
                    if 0 <= pattern_x < 16:
                        self._cycle_pattern(name)

    def draw(self):
        """パターンの可視化"""
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

        # 各ドラム音のパターンを表示
        base_y = 40
        for i, (name, drum) in enumerate(self.drums.items()):
            # ドラム名
            color = 5 if drum.muted else 7
            pyxel.text(5, base_y + i * 30, f"{drum.name}", color)

            # パターン表示
            pattern = self.pattern_banks[name][self.current_pattern[name]]
            for j, val in enumerate(pattern):
                x = 60 + j * 10
                y = base_y + i * 30
                color = 5 if val == 0 else (13 if drum.muted else 7)
                if j == self.step:
                    color = 8 if val == 1 else 2  # 現在のステップは赤/暗赤
                pyxel.rect(x, y, 8, 8, color)

            # パターン番号を表示
            pyxel.text(220, base_y + i * 30, f"P{self.current_pattern[name] + 1}", 6)

        # 操作説明
        pyxel.text(5, 160, "SPACE: Toggle Rhythm", 13)
        pyxel.text(5, 170, "1-4: Toggle Mute", 13)
        pyxel.text(120, 170, "CLICK: Change Pattern", 13)

    def on_midi(self, msg: MidiMessage):
        """MIDIメッセージを受信した際の処理"""
        if not self.enabled:
            return

        if msg.type == MIDI_CLOCK:
            self.synced = True
            self.ppq_count = (self.ppq_count + 1) % 24

            # 6PPQごと（16分音符）にステップを進める
            if self.running and self.ppq_count % 6 == 0:
                self._process_step()
                # 次のステップへ
                self.step = (self.step + 1) % 16

        elif msg.type == MIDI_START:
            self.running = True
            self.ppq_count = 0
            self.step = 0

        elif msg.type == MIDI_STOP:
            self.running = False
            self.ppq_count = 0

    def _process_step(self):
        """現在のステップの音を処理"""
        for name, drum in self.drums.items():
            if drum.muted:
                continue

            pattern = self.pattern_banks[name][self.current_pattern[name]]
            if pattern[self.step] == 1:
                # ドラム音を再生
                pyxel.play(drum.sound_id, drum.sound_id)

    def _toggle_mute(self, drum_name: str):
        """指定したドラム音のミュート状態を切り替え"""
        if drum_name in self.drums:
            self.drums[drum_name].muted = not self.drums[drum_name].muted

    def _cycle_pattern(self, drum_name: str):
        """指定したドラム音の次のパターンに切り替え"""
        if drum_name in self.pattern_banks:
            self.current_pattern[drum_name] = (self.current_pattern[drum_name] + 1) % len(self.pattern_banks[drum_name])

    def run(self):
        """アプリケーションの実行"""
        try:
            pyxel.mouse(True)  # マウス操作を有効化
            pyxel.run(self.update, self.draw)
        finally:
            # 終了時にMIDIノードをクローズ
            self.midi_node.close()


if __name__ == "__main__":
    AdvancedRhythmNode().run()
