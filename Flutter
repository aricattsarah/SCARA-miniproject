import 'dart:io';
import 'package:flutter/material.dart';

void main() {
  runApp(const SCARAControlApp());
}

class SCARAControlApp extends StatelessWidget {
  const SCARAControlApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SCARA Robot Control',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: const Color(0xFF15202B),
      ),
      home: const ControlPanel(),
    );
  }
}

class ControlPanel extends StatefulWidget {
  const ControlPanel({super.key});

  @override
  _ControlPanelState createState() => _ControlPanelState();
}

class _ControlPanelState extends State<ControlPanel> {
  Socket? _socket;
  final TextEditingController _ipController = TextEditingController(text: '192.168.82.242');
  final TextEditingController _portController = TextEditingController(text: '12345');
  final TextEditingController _loopController = TextEditingController(text: '1');
  String _connectionStatus = 'Disconnected';
  int _currentControl = 1;
  double _servo1Value = 90;
  double _servo3Value = 90;
  double _servo4Value = 90;
  String _gripperState = 'Release';
  bool _isLocalUpdate = false;
  double _playbackSpeed = 5;

  Future<void> _connectToServer() async {
    try {
      print('Attempting to connect to ${_ipController.text}:${_portController.text}');
      _socket = await Socket.connect(_ipController.text, int.parse(_portController.text));
      setState(() {
        _connectionStatus = 'Connected';
      });
      print('Connected successfully');
      _socket!.listen(
        (data) {
          String response = String.fromCharCodes(data).trim();
          print('Received: $response');
          if (!_isLocalUpdate) {
            setState(() {
              if (response.contains('Gripper holding')) {
                _gripperState = 'Hold';
              } else if (response.contains('Gripper releasing')) {
                _gripperState = 'Release';
              } else if (response.startsWith('S1')) {
                _servo1Value = double.parse(response.substring(2));
              } else if (response.startsWith('S3')) {
                _servo3Value = double.parse(response.substring(2));
              } else if (response.startsWith('S4')) {
                _servo4Value = double.parse(response.substring(2));
              }
            });
          }
          _isLocalUpdate = false;
        },
        onError: (error) {
          print('Socket error: $error');
          setState(() {
            _connectionStatus = 'Error: $error';
          });
          _socket?.destroy();
          _socket = null;
        },
        onDone: () {
          print('Socket closed by server');
          setState(() {
            _connectionStatus = 'Disconnected';
          });
          _socket?.destroy();
          _socket = null;
        },
      );
    } catch (e) {
      print('Connection failed: $e');
      setState(() {
        _connectionStatus = 'Failed to connect: $e';
      });
    }
  }

  void _sendCommand(String command) {
    if (_socket != null) {
      _socket!.write('$command\n');
      print('Sent: $command');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Not connected to server')),
      );
    }
  }

  void _switchControl() {
    setState(() {
      _currentControl = (_currentControl % 5) + 1;
      _sendCommand('servo $_currentControl');
    });
  }

  @override
  void dispose() {
    _socket?.destroy();
    _ipController.dispose();
    _portController.dispose();
    _loopController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SCARA Robot Control'),
        backgroundColor: const Color(0xFF1DA1F2),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextField(
              controller: _ipController,
              decoration: const InputDecoration(
                labelText: 'Server IP',
                labelStyle: TextStyle(color: Colors.white),
                enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.white)),
                focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.blue)),
              ),
              style: const TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _portController,
              decoration: const InputDecoration(
                labelText: 'Server Port',
                labelStyle: TextStyle(color: Colors.white),
                enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.white)),
                focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.blue)),
              ),
              style: const TextStyle(color: Colors.white),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: _connectToServer,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1DA1F2),
                foregroundColor: Colors.white,
              ),
              child: const Text('Connect'),
            ),
            const SizedBox(height: 8),
            Text('Status: $_connectionStatus', style: const TextStyle(color: Colors.white)),

            const SizedBox(height: 16),
            const Text('Servo 1 (Base, 270°)', style: TextStyle(color: Colors.white)),
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.remove, color: Colors.white),
                  onPressed: () {
                    setState(() {
                      _servo1Value = (_servo1Value - 2).clamp(0, 180); // Reduced from 5 to 2
                      if (_currentControl == 1) {
                        _isLocalUpdate = true;
                        _sendCommand('S1${_servo1Value.round()}');
                      }
                    });
                  },
                ),
                Expanded(
                  child: Slider(
                    value: _servo1Value,
                    min: 0,
                    max: 180,
                    divisions: 90, // Finer divisions for smoother control
                    label: _servo1Value.round().toString(),
                    onChanged: (value) {
                      setState(() {
                        _servo1Value = value;
                        if (_currentControl == 1) {
                          _isLocalUpdate = true;
                          _sendCommand('S1${value.round()}');
                        }
                      });
                    },
                    activeColor: const Color(0xFF1DA1F2),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.add, color: Colors.white),
                  onPressed: () {
                    setState(() {
                      _servo1Value = (_servo1Value + 2).clamp(0, 180); // Reduced from 5 to 2
                      if (_currentControl == 1) {
                        _isLocalUpdate = true;
                        _sendCommand('S1${_servo1Value.round()}');
                      }
                    });
                  },
                ),
              ],
            ),

            const SizedBox(height: 16),
            const Text('Servo 2 (Linear Actuator)', style: TextStyle(color: Colors.white)),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: () => _sendCommand('up'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1DA1F2),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Up'),
                ),
                ElevatedButton(
                  onPressed: () => _sendCommand('stop'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1DA1F2),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Stop'),
                ),
                ElevatedButton(
                  onPressed: () => _sendCommand('down'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1DA1F2),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Down'),
                ),
              ],
            ),

            const SizedBox(height: 16),
            const Text('Servo 3 (Link 3, 360°)', style: TextStyle(color: Colors.white)),
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.remove, color: Colors.white),
                  onPressed: () {
                    setState(() {
                      _servo3Value = (_servo3Value - 5).clamp(0, 180);
                      if (_currentControl == 3) {
                        _isLocalUpdate = true;
                        _sendCommand('S3${_servo3Value.round()}');
                      }
                    });
                  },
                ),
                Expanded(
                  child: Slider(
                    value: _servo3Value,
                    min: 0,
                    max: 180,
                    divisions: 36,
                    label: _servo3Value.round().toString(),
                    onChanged: (value) {
                      setState(() {
                        _servo3Value = value;
                        if (_currentControl == 3) {
                          _isLocalUpdate = true;
                          _sendCommand('S3${value.round()}');
                        }
                      });
                    },
                    activeColor: const Color(0xFF1DA1F2),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.add, color: Colors.white),
                  onPressed: () {
                    setState(() {
                      _servo3Value = (_servo3Value + 5).clamp(0, 180);
                      if (_currentControl == 3) {
                        _isLocalUpdate = true;
                        _sendCommand('S3${_servo3Value.round()}');
                      }
                    });
                  },
                ),
              ],
            ),

            const SizedBox(height: 16),
            const Text('Servo 4 (Link 4, 180°)', style: TextStyle(color: Colors.white)),
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.remove, color: Colors.white),
                  onPressed: () {
                    setState(() {
                      _servo4Value = (_servo4Value - 5).clamp(0, 180);
                      if (_currentControl == 4) {
                        _isLocalUpdate = true;
                        _sendCommand('S4${_servo4Value.round()}');
                      }
                    });
                  },
                ),
                Expanded(
                  child: Slider(
                    value: _servo4Value,
                    min: 0,
                    max: 180,
                    divisions: 36,
                    label: _servo4Value.round().toString(),
                    onChanged: (value) {
                      setState(() {
                        _servo4Value = value;
                        if (_currentControl == 4) {
                          _isLocalUpdate = true;
                          _sendCommand('S4${value.round()}');
                        }
                      });
                    },
                    activeColor: const Color(0xFF1DA1F2),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.add, color: Colors.white),
                  onPressed: () {
                    setState(() {
                      _servo4Value = (_servo4Value + 5).clamp(0, 180);
                      if (_currentControl == 4) {
                        _isLocalUpdate = true;
                        _sendCommand('S4${_servo4Value.round()}');
                      }
                    });
                  },
                ),
              ],
            ),

            const SizedBox(height: 16),
            Text('Gripper: $_gripperState', style: const TextStyle(color: Colors.white)),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: () => _sendCommand('grip'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1DA1F2),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Grip'),
                ),
                ElevatedButton(
                  onPressed: () => _sendCommand('release'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1DA1F2),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Release'),
                ),
              ],
            ),

            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _switchControl,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1DA1F2),
                foregroundColor: Colors.white,
              ),
              child: Text('Switch Control (Servo $_currentControl)'),
            ),

            const SizedBox(height: 16),
            const Text('Motion Recording & Playback', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: () => _sendCommand('record'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1DA1F2),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Record'),
                ),
                ElevatedButton(
                  onPressed: () => _sendCommand('stop_recording'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1DA1F2),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Stop Recording'),
                ),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: () => _sendCommand('play ${_loopController.text} ${_playbackSpeed.round()}'), // Fixed to send integer
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1DA1F2),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Play'),
                ),
                ElevatedButton(
                  onPressed: () => _sendCommand('stop_playback'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1DA1F2),
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Stop'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Text('Loops: ', style: TextStyle(color: Colors.white)),
                SizedBox(
                  width: 60,
                  child: TextField(
                    controller: _loopController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.white)),
                      focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.blue)),
                    ),
                    style: const TextStyle(color: Colors.white),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            const Text('Playback Speed (0-10):', style: TextStyle(color: Colors.white)),
            Slider(
              value: _playbackSpeed,
              min: 0,
              max: 10,
              divisions: 10,
              label: _playbackSpeed.round().toString(),
              onChanged: (value) {
                setState(() {
                  _playbackSpeed = value;
                });
              },
              activeColor: const Color(0xFF1DA1F2),
            ),
          ],
        ),
      ),
    );
  }
}
