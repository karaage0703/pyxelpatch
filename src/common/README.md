# 共通モジュール

このディレクトリには、PyxelPatchの全ノードで共有される共通コンポーネントが含まれています。

## base_node.py

すべてのノードの基底クラス `Node` を定義しています。各ノードはこのクラスを継承して実装されます。

### 重要な概念

#### MIDI同期システム

PyxelPatchでは、以下のMIDI同期システムを採用しています：

- **PPQ (Pulses Per Quarter Note)**
  - 4分音符あたりのパルス数を表す単位
  - MIDIでは24 PPQが標準（1拍を24分割）
  - 例：120 BPMの場合
    - 1拍 = 0.5秒
    - 1パルス = 約0.021秒（0.5秒÷24）

- **同期状態**
  - `synced`: クロック信号を受信しているか
  - `running`: 再生中かどうか
  - `ppq_count`: 現在のパルスカウント（0-23）

- **同期メッセージ**
  - `clock`: PPQパルス（24 PPQN）
  - `start`: シーケンス開始
  - `stop`: シーケンス停止

#### ノードの状態管理

- **enabled**: ノードの有効/無効状態
- **in_channels**: 受信するMIDIチャンネル
- **window_size**: Pyxelウィンドウのサイズ

## midi_utils.py

MIDI通信に関するユーティリティを提供します。

### 主な機能

- **MidiMessage**: MIDIメッセージのデータクラス
  - ノート情報（音程、ベロシティ）
  - コントロール情報
  - 同期信号

- **MidiNode**: MIDI通信を行うクラス
  - UDP経由でのメッセージ送受信
  - ブロードキャストによるノード間通信
  - 非同期受信処理

### 使用例

```python
# MIDIノードの初期化
midi_node = MidiNode("my_node", on_midi_callback)

# MIDIメッセージの送信
msg = MidiMessage(type="note_on", note=60, velocity=127)
midi_node.send_message(msg)

# 終了時
midi_node.close()