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
    source: Optional[str] = None  # メッセージの送信元ノード名


class MidiNode:
    BROADCAST_PORT = 5000  # すべてのノードで共通のポート
    BROADCAST_ADDR = "255.255.255.255"  # ブロードキャストアドレス

    def __init__(self, node_name: str, callback: Callable[[MidiMessage], None]):
        """MIDIノードの初期化

        Args:
            node_name: ノードの識別名
            callback: MIDIメッセージを受信した時のコールバック関数
        """
        self.node_name = node_name
        self.callback = callback

        # 受信用ソケット
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # ソケットオプションの設定
        self.receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):  # macOSとLinuxでのみ利用可能
            self.receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # ワイルドカードアドレスにバインド
        self.receiver.bind(("0.0.0.0", self.BROADCAST_PORT))

        # 送信用ソケット
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

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

                # 自分自身が送信したメッセージは無視
                if msg_dict.get("source") == self.node_name:
                    continue

                msg = MidiMessage(**msg_dict)
                self.callback(msg)
            except (json.JSONDecodeError, socket.error, ValueError) as e:
                print(f"Error in MIDI receive loop: {e}")
                time.sleep(0.001)

    def send_message(self, msg: MidiMessage):
        """MIDIメッセージをブロードキャスト送信

        Args:
            msg: 送信するMIDIメッセージ
        """
        # 送信元ノード名を設定
        msg_dict = asdict(msg)
        msg_dict["source"] = self.node_name

        msg_json = json.dumps(msg_dict)
        self.sender.sendto(msg_json.encode(), (self.BROADCAST_ADDR, self.BROADCAST_PORT))

    def close(self):
        """ノードを終了"""
        self.running = False
        self.receiver.close()
        self.sender.close()


# MIDIメッセージタイプ
MIDI_CLOCK = "clock"  # MIDIクロック信号
MIDI_START = "start"  # 再生開始
MIDI_STOP = "stop"  # 再生停止
MIDI_CONTINUE = "continue"  # 再開
MIDI_SONG_POSITION = "song_position"  # 曲位置
