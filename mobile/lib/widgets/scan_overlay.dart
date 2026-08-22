import 'package:flutter/material.dart';

/// Máscara oscura con un recorte del tamaño de [scanWindow] más esquinas
/// marcadas — guía visual estándar de escáner para que se sepa dónde
/// apuntar el código de barras. El mismo [scanWindow] se le pasa también a
/// `MobileScanner` para que la detección quede restringida a esa zona.
class ScanOverlay extends StatelessWidget {
  final Rect scanWindow;

  const ScanOverlay({super.key, required this.scanWindow});

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: CustomPaint(
        size: Size.infinite,
        painter: _ScanOverlayPainter(scanWindow),
      ),
    );
  }
}

class _ScanOverlayPainter extends CustomPainter {
  final Rect scanWindow;

  _ScanOverlayPainter(this.scanWindow);

  @override
  void paint(Canvas canvas, Size size) {
    final backgroundPath = Path()..addRect(Rect.fromLTWH(0, 0, size.width, size.height));
    final cutoutPath = Path()..addRRect(RRect.fromRectAndRadius(scanWindow, const Radius.circular(16)));
    final maskPath = Path.combine(PathOperation.difference, backgroundPath, cutoutPath);
    canvas.drawPath(maskPath, Paint()..color = Colors.black.withValues(alpha: 0.6));

    canvas.drawRRect(
      RRect.fromRectAndRadius(scanWindow, const Radius.circular(16)),
      Paint()
        ..color = Colors.white
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2,
    );

    _drawCorner(canvas, scanWindow.topLeft, const Offset(1, 1));
    _drawCorner(canvas, scanWindow.topRight, const Offset(-1, 1));
    _drawCorner(canvas, scanWindow.bottomLeft, const Offset(1, -1));
    _drawCorner(canvas, scanWindow.bottomRight, const Offset(-1, -1));
  }

  void _drawCorner(Canvas canvas, Offset corner, Offset direction) {
    const length = 24.0;
    final paint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.stroke
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(corner, corner + Offset(length * direction.dx, 0), paint);
    canvas.drawLine(corner, corner + Offset(0, length * direction.dy), paint);
  }

  @override
  bool shouldRepaint(_ScanOverlayPainter oldDelegate) => oldDelegate.scanWindow != scanWindow;
}
