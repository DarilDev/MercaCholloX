import 'package:flutter/material.dart';

import 'categories_screen.dart';
import 'location_screen.dart';
import 'scan_screen.dart';
import 'search_screen.dart';
import 'shopping_list_screen.dart';

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  // Mi lista es la pantalla de inicio (posición 2 en _screens) — el resto
  // del orden de pestañas no cambia.
  int _index = 2;

  static const _screens = [
    CategoriesScreen(),
    SearchScreen(),
    ShoppingListScreen(),
    LocationScreen(),
  ];

  // "Escanear" no vive en el IndexedStack a propósito: si fuera una pestaña
  // más, la cámara quedaría inicializada en segundo plano todo el rato que la
  // app esté abierta en cualquier otra pantalla — se empuja como ruta aparte
  // para que solo consuma cámara/batería mientras está realmente en uso.
  void _onDestinationSelected(int i) {
    if (i == 4) {
      Navigator.push(context, MaterialPageRoute(builder: (_) => const ScanScreen()));
      return;
    }
    setState(() => _index = i);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _index, children: _screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: _onDestinationSelected,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.storefront_outlined), label: 'Supermercados'),
          NavigationDestination(icon: Icon(Icons.search), label: 'Buscar'),
          NavigationDestination(icon: Icon(Icons.shopping_cart_outlined), label: 'Mi lista'),
          NavigationDestination(icon: Icon(Icons.place_outlined), label: 'Ubicación'),
          NavigationDestination(icon: Icon(Icons.qr_code_scanner), label: 'Escanear'),
        ],
      ),
    );
  }
}
