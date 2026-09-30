import 'package:flutter/material.dart';

void main() {
  runApp(const QitcoinApp());
}

class QitcoinApp extends StatelessWidget {
  const QitcoinApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Qitcoin Core (QTC)',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0D1117),
        primaryColor: const Color(0xFFF59E0B),
        cardColor: const Color(0xFF161B22),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFFF59E0B),
          secondary: Color(0xFF10B981),
          surface: Color(0xFF161B22),
        ),
      ),
      home: const MainNavigationScreen(),
    );
  }
}

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;
  String _connectedWallet = "None";
  String _activeAddress = "Q1TrillionQitcoinGenesisDevKey888";
  double _balanceQtc = 250000.0;

  void _showWalletConnectModal() {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF161B22),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) {
        return Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text("Connect Web3 / Multi-Wallet", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              ListTile(
                leading: const CircleAvatar(backgroundColor: Colors.orange, child: Text("Q")),
                title: const Text("Native QTC Core Wallet"),
                subtitle: const Text("Direct L1 Node RPC Connection"),
                onTap: () {
                  setState(() { _connectedWallet = "Qitcoin Core"; });
                  Navigator.pop(ctx);
                },
              ),
              ListTile(
                leading: const CircleAvatar(backgroundColor: Colors.deepOrange, child: Icon(Icons.shield)),
                title: const Text("MetaMask (EVM / wQTC)"),
                subtitle: const Text("Ethereum, Arbitrum & Base Bridge"),
                onTap: () {
                  setState(() { _connectedWallet = "MetaMask (0x71C...4022)"; });
                  Navigator.pop(ctx);
                },
              ),
              ListTile(
                leading: const CircleAvatar(backgroundColor: Colors.purple, child: Icon(Icons.flash_on)),
                title: const Text("Phantom (Solana / wQTC)"),
                subtitle: const Text("Fast SVM Liquidity Bridge"),
                onTap: () {
                  setState(() { _connectedWallet = "Phantom (8xQ...9sP)"; });
                  Navigator.pop(ctx);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> screens = [
      _buildWalletScreen(),
      _buildSwapScreen(),
      _buildBridgeScreen(),
      _buildAgentScreen(),
      _buildLaunchpadScreen(),
    ];

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B22),
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(color: const Color(0xFFF59E0B), borderRadius: BorderRadius.circular(8)),
              child: const Text("QTC", style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(width: 10),
            const Text("Qitcoin Portal", style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
          ],
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12.0),
            child: ActionChip(
              backgroundColor: const Color(0xFF21262D),
              avatar: Icon(Icons.account_balance_wallet, size: 16, color: _connectedWallet == "None" ? Colors.grey : Colors.green),
              label: Text(_connectedWallet, style: const TextStyle(fontSize: 12)),
              onPressed: _showWalletConnectModal,
            ),
          )
        ],
      ),
      body: screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (idx) => setState(() => _currentIndex = idx),
        backgroundColor: const Color(0xFF161B22),
        selectedItemColor: const Color(0xFFF59E0B),
        unselectedItemColor: const Color(0xFF8B949E),
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.wallet), label: 'Wallet'),
          BottomNavigationBarItem(icon: Icon(Icons.swap_horiz), label: 'Swap'),
          BottomNavigationBarItem(icon: Icon(Icons.alt_route), label: 'Bridge'),
          BottomNavigationBarItem(icon: Icon(Icons.smart_toy), label: 'AI Agent'),
          BottomNavigationBarItem(icon: Icon(Icons.rocket_launch), label: 'Launchpad'),
        ],
      ),
    );
  }

  Widget _buildWalletScreen() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  const Text("TOTAL QTC BALANCE", style: TextStyle(color: Color(0xFF8B949E), fontSize: 12, letterSpacing: 1.2)),
                  const SizedBox(height: 8),
                  Text("${_balanceQtc.toStringAsFixed(2)} QTC", style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white)),
                  const SizedBox(height: 4),
                  const Text("≈ \$12,500.00 USD (at \$0.05 / QTC)", style: TextStyle(color: Color(0xFF10B981), fontSize: 13)),
                  const Divider(height: 32),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      ElevatedButton.icon(onPressed: () {}, icon: const Icon(Icons.arrow_upward), label: const Text("Send"), style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFF59E0B), foregroundColor: Colors.black)),
                      ElevatedButton.icon(onPressed: () {}, icon: const Icon(Icons.qr_code), label: const Text("Receive"), style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF21262D))),
                    ],
                  )
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: ListTile(
              title: const Text("Your QTC Address"),
              subtitle: Text(_activeAddress, style: const TextStyle(fontSize: 12, color: Color(0xFF58A6FF))),
              trailing: IconButton(icon: const Icon(Icons.copy), onPressed: () {}),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSwapScreen() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text("Decentralized Cross-Chain Swap", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              const TextField(decoration: InputDecoration(labelText: "You Pay (QTC)", suffixText: "QTC", border: OutlineInputBorder())),
              const Center(child: Padding(padding: EdgeInsets.symmetric(vertical: 8), child: Icon(Icons.arrow_downward, color: Color(0xFFF59E0B)))),
              const TextField(decoration: InputDecoration(labelText: "You Receive (USDT)", suffixText: "USDT", border: OutlineInputBorder())),
              const SizedBox(height: 20),
              SizedBox(width: double.infinity, height: 48, child: ElevatedButton(onPressed: () {}, style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFF59E0B), foregroundColor: Colors.black), child: const Text("Execute Instant Swap", style: TextStyle(fontWeight: FontWeight.bold))))
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBridgeScreen() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: ListView(
        children: const [
          Card(
            child: ListTile(
              leading: Icon(Icons.verified_user, color: Color(0xFF10B981)),
              title: Text("NIST FIPS 204 (ML-DSA-65) Active"),
              subtitle: Text("Quantum-Resistant Relayer Attestations"),
            ),
          ),
          Card(
            child: ListTile(
              leading: Icon(Icons.account_balance, color: Color(0xFF58A6FF)),
              title: Text("Proof of Reserve: 100% Solvency"),
              subtitle: Text("Locked: 50,000,000 QTC | Minted: 50,000,000 wQTC"),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAgentScreen() {
    return const Center(child: Text("Multimodal AI Agentics & Conway Grid"));
  }

  Widget _buildLaunchpadScreen() {
    return const Center(child: Text("QTC Token Launchpad & Bonding Curve"));
  }
}
