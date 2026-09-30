import 'package:serverpod/serverpod.dart';

// This is the starting point for your Serverpod server.
void run(List<String> args) async {
  // Initialize Serverpod and connect it with the generated code.
  final pod = Serverpod(
    args,
    Protocol(),
    Endpoints(),
  );

  print('====================================================');
  print('QITCOIN SERVERPOD HIGH-PERFORMANCE BACKEND INITIALIZED');
  print('Real-time WebSockets, PQC Bridge & Multimodal Agents Active');
  print('====================================================');

  // Start the server.
  await pod.start();
}
