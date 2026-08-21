import 'package:flutter/material.dart';

import 'screens/home_shell.dart';
import 'theme.dart';

void main() {
  runApp(const MercaCholloApp());
}

class MercaCholloApp extends StatelessWidget {
  const MercaCholloApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MercaChollo',
      theme: buildAppTheme(),
      home: const HomeShell(),
    );
  }
}
