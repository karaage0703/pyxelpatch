import socket
import json
from dataclasses import dataclass, asdict
from typing import Optional, Callable
import threading
import time


@dataclass
class MidiMessage:
    type: str
    note: Optional[int] = None
    velocity: Optional[int] = None
    channel: Optional[int] = None
    control: Optional[int] = None
    value: Optional[int] = None


class MidiNode:
    def __init__(self, port: int, callback: Callable[[MidiMessage], None]):
        """MIDIノードの初期化

        Args:
            port: 受信用ポート番号
            callback: MIDIメッセージを受信した時のコールバック関数
        """
        self.port = port
        self.callback = callback

        # 受信用ソケット
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver.bind(("127.0.0.1", port))

        # 送信用ソケット
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 受信スレッド
        self.running = True
        self.thread = threading.Thread(target=self._receive_loop)
        self.thread.daemon = True
        self.thread.start()

    def _receive_loop(self):
        """メッセージ受信ループ"""
        while self.running:
            try:
                data, _ = self.receiver.recvfrom(1024)
                msg_dict = json.loads(data.decode())
                msg = MidiMessage(**msg_dict)
                self.callback(msg)
            except (json.JSONDecodeError, socket.error, ValueError) as e:
                # JSONデコードエラー、ソケットエラー、値エラーを個別に処理
                print(f"Error in MIDI receive loop: {e}")
                time.sleep(0.001)  # 短い待機時間

    def send_message(self, msg: MidiMessage, dest_port: int):
        """MIDIメッセージを送信

        Args:
            msg: 送信するMIDIメッセージ
            dest_port: 送信先のポート番号
        """
        msg_json = json.dumps(asdict(msg))
        self.sender.sendto(msg_json.encode(), ("127.0.0.1", dest_port))

    def close(self):
        """ノードを終了"""
        self.running = False
        self.receiver.close()
        self.sender.close()


# ポート番号の定義
RHYTHM_GEN_PORT = 5000  # リズムジェネレータ（マスタークロック）
RHYTHM_PORT = 5001  # リズムマシン
ADVANCED_RHYTHM_PORT = 5002  # 高度なリズムマシン
SYNTH_PORT = 5003  # シンセサイザー

# MIDIメッセージタイプ
MIDI_CLOCK = "clock"  # MIDIクロック信号
MIDI_START = "start"  # 再生開始
MIDI_STOP = "stop"  # 再生停止
MIDI_CONTINUE = "continue"  # 再開
MIDI_SONG_POSITION = "song_position"  # 曲位置
