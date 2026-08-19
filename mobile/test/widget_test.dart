import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mercachollo/main.dart';

void main() {
  testWidgets('La app arranca y muestra la navegación principal', (WidgetTester tester) async {
    await tester.pumpWidget(const MercaCholloApp());

    expect(find.text('Pasillos'), findsWidgets);
    expect(find.text('Buscar'), findsWidgets);
    expect(find.text('Mi lista'), findsOneWidget);
  });
}
