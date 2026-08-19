import 'package:flutter/material.dart';

import 'categories_screen.dart';
import 'location_screen.dart';
import 'search_screen.dart';
import 'shopping_list_screen.dart';

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  static const _screens = [
    CategoriesScreen(),
    SearchScreen(),
    ShoppingListScreen(),
    LocationScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _index, children: _screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.storefront_outlined), label: 'Pasillos'),
          NavigationDestination(icon: Icon(Icons.search), label: 'Buscar'),
          NavigationDestination(icon: Icon(Icons.shopping_cart_outlined), label: 'Mi lista'),
          NavigationDestination(icon: Icon(Icons.place_outlined), label: 'Ubicación'),
        ],
      ),
    );
  }
}
