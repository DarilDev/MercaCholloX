import 'package:flutter/material.dart';

/// Tema centralizado — antes cada pantalla usaba colores sueltos
/// (Colors.amber, Colors.green.shade600...) en vez de una paleta compartida.
/// Mismo verde semilla de siempre, solo que ahora vive en un sitio y con
/// nombre, no repetido y reinventado por pantalla.
class AppColors {
  static const seed = Colors.green;
  static final success = Colors.green.shade600;
  static final danger = Colors.red.shade700;
  static const starred = Colors.amber;
}

class AppSpacing {
  static const xs = 4.0;
  static const sm = 8.0;
  static const md = 16.0;
  static const lg = 24.0;
}

ThemeData buildAppTheme() {
  final colorScheme = ColorScheme.fromSeed(seedColor: AppColors.seed);
  return ThemeData(
    colorScheme: colorScheme,
    cardTheme: CardThemeData(
      clipBehavior: Clip.antiAlias,
      margin: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.xs),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm)),
    ),
  );
}
