import random
import math
import pyxel
from typing import List, Tuple

from src.common.base_node import Node
from src.common.midi_utils import (
    MidiNode,
    MidiMessage,
    MIDI_CLOCK,
    MIDI_START,
    MIDI_STOP,
)


class Particle:
    """パーティクルクラス - 視覚効果用の動的な点を表現"""

    def __init__(self, x: float, y: float, dx: float, dy: float, life: int, color: int):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.life = life
        self.color = color
        self.original_life = life

    def update(self) -> bool:
        """パーティクルの位置を更新し、生存しているかを返す"""
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.1  # 重力効果
        self.life -= 1
        return self.life > 0

    def draw(self):
        """パーティクルを描画"""
        alpha = self.life / self.original_life
        size = max(1, int(2 * alpha))
        pyxel.circ(int(self.x), int(self.y), size, self.color)


class VideoNode(Node):
    """MIDIイベントに反応して視覚効果を生成するノード"""

    def __init__(self):
        super().__init__(name="VideoNode")

        # Pyxelの初期化
        pyxel.init(160, 120, title="PyxelPatch - Video Node")

        # パーティクル管理
        self.particles: List[Particle] = []

        # ビジュアルエフェクト用の状態管理
        self.flash_intensity = 0.0  # フラッシュ効果の強度
        self.beat_progress = 0.0  # 拍の進行度
        self.base_color = 1  # 基本色（0-15）

        # 画面中央座標
        self.center_x = pyxel.width // 2
        self.center_y = pyxel.height // 2

        # 同期関連
        self.synced = False
        self.ppq_count = 0  # Pulses Per Quarter note カウンタ
        self.running = False

        # MIDIノードの初期化
        self.midi_node = MidiNode("video", self.on_midi)

    def on_midi(self, msg: MidiMessage):
        """MIDIメッセージを受信した際の処理"""
        if not self.enabled:
            return

        if msg.type == MIDI_CLOCK:
            self.synced = True
            self.ppq_count = (self.ppq_count + 1) % 24

            # 24PPQで4分音符
            if self.running and self.ppq_count == 0:
                self.on_quarter_note()

        elif msg.type == MIDI_START:
            self.running = True
            self.ppq_count = 0

        elif msg.type == MIDI_STOP:
            self.running = False
            self.ppq_count = 0

        elif msg.type == "note_on":
            # ノートオンでパーティクル生成
            velocity = msg.velocity / 127.0
            note = msg.note

            # ノート番号から色を決定
            color = note % 15 + 1

            # パーティクルを放射状に生成
            num_particles = int(velocity * 10) + 5
            for _ in range(num_particles):
                angle = random.random() * math.pi * 2
                speed = random.random() * 3 + 2
                dx = math.cos(angle) * speed
                dy = math.sin(angle) * speed

                particle = Particle(self.center_x, self.center_y, dx, dy, life=30, color=color)
                self.particles.append(particle)

            # フラッシュ効果を設定
            self.flash_intensity = velocity

    def on_quarter_note(self):
        """4分音符のタイミングで呼ばれる"""
        # 拍に合わせて色を変更
        self.base_color = (self.base_color + 1) % 15 + 1

        # 中央から外側に向かってパーティクルを生成
        for i in range(8):
            angle = (i / 8.0) * math.pi * 2
            particle = Particle(
                self.center_x, self.center_y, math.cos(angle) * 2, math.sin(angle) * 2, life=20, color=self.base_color
            )
            self.particles.append(particle)

    def update(self):
        """毎フレーム実行されるメインロジック"""
        # スペースキーでビジュアルのON/OFF切り替え
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.toggle_enabled()

        # パーティクルの更新
        self.particles = [p for p in self.particles if p.update()]

        # フラッシュ効果の減衰
        self.flash_intensity *= 0.9

        # 拍の進行度を更新
        self.beat_progress = (self.beat_progress + 0.1) % 1.0

    def draw(self):
        """Pyxelの描画処理"""
        # 画面クリア
        pyxel.cls(0)

        # 背景の円を描画（拍の進行に合わせて拡大縮小）
        radius = 20 + math.sin(self.beat_progress * math.pi * 2) * 5
        pyxel.circ(self.center_x, self.center_y, radius, self.base_color)

        # パーティクルの描画
        for particle in self.particles:
            particle.draw()

        # フラッシュ効果
        if self.flash_intensity > 0.1:
            flash_color = 7  # 白色
            size = int(self.flash_intensity * 20)
            pyxel.circb(self.center_x, self.center_y, size, flash_color)
            pyxel.circb(self.center_x, self.center_y, size + 1, flash_color)

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
        pyxel.text(5, 100, "SPACE: Toggle Visual", 7)

    def run(self):
        """アプリケーションの実行"""
        try:
            pyxel.run(self.update, self.draw)
        finally:
            # 終了時にMIDIノードをクローズ
            self.midi_node.close()


if __name__ == "__main__":
    VideoNode().run()
