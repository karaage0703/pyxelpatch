import pyxel
from dataclasses import dataclass
from typing import Dict, List
from src.common.base_node import Node
from src.common.midi_utils import MidiMessage


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
        super().__init__(name="AdvancedRhythm", window_size=(240, 180))
        # ドラム音の初期化
        self._init_drum_sounds()
        self.step = 0

        # マウス操作を有効化
        pyxel.mouse(True)

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

        # マウスクリックでパターンのON/OFF切り替え
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            # クリックされた位置を確認
            for i, (name, drum) in enumerate(self.drums.items()):
                base_y = 40 + i * 30
                if base_y <= pyxel.mouse_y <= base_y + 8:
                    # パターン領域内でのクリックを確認
                    pattern_x = (pyxel.mouse_x - 60) // 10
                    if 0 <= pattern_x < 16:
                        self._toggle_step(name, pattern_x)

    def draw(self):
        """パターンの可視化"""
        super().draw()  # 基本的な状態表示

        # 各ドラム音のパターンを表示
        base_y = 40
        for i, (name, drum) in enumerate(self.drums.items()):
            # ドラム名
            color = 5 if drum.muted else 7
            pyxel.text(5, base_y + i * 30, f"{drum.name}", color)

            # パターン表示
            for j, val in enumerate(drum.pattern):
                x = 60 + j * 10
                y = base_y + i * 30
                color = 5 if val == 0 else (13 if drum.muted else 7)
                if j == self.step:
                    color = 8 if val == 1 else 2  # 現在のステップは赤/暗赤
                pyxel.rect(x, y, 8, 8, color)

        # 操作説明
        pyxel.text(5, 160, "SPACE: Toggle Rhythm", 13)
        pyxel.text(5, 170, "1-4: Toggle Mute", 13)
        pyxel.text(120, 170, "CLICK: Toggle Step", 13)

    def on_midi(self, msg: MidiMessage):
        """MIDIメッセージを受信した際の処理"""
        super().on_midi(msg)  # 基本的なMIDI処理

        if not self.enabled:
            return

        # 6PPQごと（16分音符）にステップを進める
        if msg.type == "clock" and self.running and self.ppq_count % 6 == 0:
            # 次のステップへ
            self.step = (self.step + 1) % 16
            # 新しいステップの音を処理
            self._process_step()

        elif msg.type == "start":
            self.step = 0
            # 最初のステップの音を処理
            self._process_step()

    def _process_step(self):
        """現在のステップの音を処理"""
        for name, drum in self.drums.items():
            if drum.muted:
                continue

            if drum.pattern[self.step] == 1:
                # ドラム音を再生
                pyxel.play(drum.sound_id, drum.sound_id)

    def _toggle_mute(self, drum_name: str):
        """指定したドラム音のミュート状態を切り替え"""
        if drum_name in self.drums:
            self.drums[drum_name].muted = not self.drums[drum_name].muted

    def _toggle_step(self, drum_name: str, step: int):
        """指定したドラム音の指定ステップのON/OFFを切り替え"""
        if drum_name in self.drums:
            self.drums[drum_name].pattern[step] = 1 - self.drums[drum_name].pattern[step]  # 0 -> 1, 1 -> 0


if __name__ == "__main__":
    AdvancedRhythmNode().run()
