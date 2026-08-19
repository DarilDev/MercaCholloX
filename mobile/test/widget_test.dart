import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:mercachollo/main.dart';

void main() {
  testWidgets('La app arranca y muestra la pantalla de búsqueda', (WidgetTester tester) async {
    await tester.pumpWidget(const MercaCholloApp());

    expect(find.text('MercaChollo'), findsOneWidget);
    expect(find.byType(TextField), findsOneWidget);
  });
}
