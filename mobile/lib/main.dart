import 'package:flutter/material.dart';

import 'screens/search_screen.dart';

void main() {
  runApp(const MercaCholloApp());
}

class MercaCholloApp extends StatelessWidget {
  const MercaCholloApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MercaChollo',
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.green)),
      home: const SearchScreen(),
    );
  }
}
