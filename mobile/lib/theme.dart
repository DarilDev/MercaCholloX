import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Tema centralizado — antes cada pantalla usaba colores sueltos
/// (Colors.amber, Colors.green.shade600...) en vez de una paleta compartida.
/// Marca propia (2026-08-22): antes esto era `ColorScheme.fromSeed(Colors.green)`
/// puro, el verde genérico que Material 3 pone por defecto en cualquier app
/// sin personalizar — de ahí lo "soso" que se veía. Ahora un verde más vivo
/// como color de marca, con un ámbar cálido de acento para ofertas/ahorro
/// (coherente con el icono de la app, mismo verde/ámbar).
class AppColors {
  static const primary = Color(0xFF0F9D58);
  static const accent = Color(0xFFFFB300);
  static final success = Colors.green.shade600;
  static final danger = Colors.red.shade700;
  static const starred = accent;
}

class AppSpacing {
  static const xs = 4.0;
  static const sm = 8.0;
  static const md = 16.0;
  static const lg = 24.0;
}

ThemeData buildAppTheme() {
  final colorScheme = ColorScheme.fromSeed(
    seedColor: AppColors.primary,
    primary: AppColors.primary,
    secondary: AppColors.accent,
  );
  final textTheme = GoogleFonts.poppinsTextTheme();
  return ThemeData(
    colorScheme: colorScheme,
    textTheme: textTheme,
    scaffoldBackgroundColor: const Color(0xFFFBF9F4),
    cardTheme: CardThemeData(
      clipBehavior: Clip.antiAlias,
      margin: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.xs),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm)),
    ),
  );
}
