import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

import '../models/scan_result.dart';
import '../services/api_client.dart';
import '../theme.dart';
import '../utils/add_to_list.dart';
import '../widgets/error_view.dart';
import '../widgets/product_tile.dart';
import '../widgets/scan_overlay.dart';
import 'product_detail_screen.dart';
import 'scan_history_screen.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final _apiClient = ApiClient();
  final _controller = MobileScannerController(
    formats: [BarcodeFormat.ean13, BarcodeFormat.ean8, BarcodeFormat.upcA],
  );
  bool _busy = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  // Un solo código a la vez: sin este freno, la cámara sigue detectando el
  // mismo código en cada frame mientras se muestra el resultado del anterior.
  Future<void> _onDetect(BarcodeCapture capture) async {
    if (_busy || capture.barcodes.isEmpty) return;
    final ean = capture.barcodes.first.rawValue;
    if (ean == null) return;

    setState(() => _busy = true);
    await _controller.stop();
    try {
      final result = await _apiClient.scanBarcode(ean);
      if (!mounted) return;
      final addName = result.matchedProduct?.name ?? result.name;
      final addImageUrl = result.matchedProduct?.imageUrl ?? result.imageUrl;
      await showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        builder: (_) => _ScanResultSheet(
          result: result,
          onAdd: addName == null
              ? null
              : () {
                  Navigator.pop(context);
                  addToShoppingList(context, _apiClient, addName, imageUrl: addImageUrl);
                },
        ),
      );
    } catch (e) {
      if (!mounted) return;
      await showModalBottomSheet(context: context, builder: (_) => ErrorView(error: e));
    } finally {
      if (mounted) {
        setState(() => _busy = false);
        await _controller.start();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Escanear'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const ScanHistoryScreen()),
            ),
          ),
        ],
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final size = constraints.biggest;
          final windowWidth = size.width * 0.8;
          final scanWindow = Rect.fromCenter(
            center: size.center(Offset.zero),
            width: windowWidth,
            height: windowWidth * 0.55,
          );
          return Stack(
            fit: StackFit.expand,
            children: [
              MobileScanner(
                controller: _controller,
                scanWindow: scanWindow,
                onDetect: _onDetect,
                errorBuilder: (context, error) => Center(
                  child: Padding(
                    padding: const EdgeInsets.all(AppSpacing.lg),
                    child: Text(
                      error.errorCode == MobileScannerErrorCode.permissionDenied
                          ? 'MercaChollo necesita permiso de cámara para escanear.'
                          : 'No se pudo abrir la cámara.',
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              ),
              ScanOverlay(scanWindow: scanWindow),
              Positioned(
                top: scanWindow.bottom + AppSpacing.md,
                left: 0,
                right: 0,
                child: const Text(
                  'Apunta al código de barras',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _ScanResultSheet extends StatelessWidget {
  final ScanResult result;
  final VoidCallback? onAdd;

  const _ScanResultSheet({required this.result, required this.onAdd});

  Color _gradeColor(String? grade) {
    switch (grade) {
      case 'A':
        return AppColors.success;
      case 'B':
        return const Color(0xFF8BC34A);
      case 'C':
        return const Color(0xFFFFC107);
      case 'D':
        return Colors.orange;
      case 'E':
        return AppColors.danger;
      default:
        return Colors.grey;
    }
  }

  String _novaLabel(int? nova) {
    switch (nova) {
      case 1:
        return 'Sin procesar o mínimamente procesado';
      case 2:
        return 'Ingrediente culinario procesado';
      case 3:
        return 'Procesado';
      case 4:
        return 'Ultraprocesado';
      default:
        return 'Nivel de procesado desconocido';
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _gradeColor(result.nutriscoreGrade);
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.md),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 28,
                  backgroundColor: color.withValues(alpha: 0.15),
                  child: Text(
                    result.nutriscoreGrade ?? '?',
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: color),
                  ),
                ),
                const SizedBox(width: AppSpacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        result.name ?? 'Producto sin nombre',
                        style: Theme.of(context).textTheme.titleMedium,
                      ),
                      Text('Nutri-Score ${result.nutriscoreGrade ?? "desconocido"}'),
                    ],
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.factory_outlined),
              title: Text(_novaLabel(result.novaGroup)),
              subtitle: const Text('Nivel de procesado (NOVA)'),
            ),
            ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.science_outlined),
              title: Text('${result.additivesCount} aditivos detectados'),
            ),
            if (result.matchedProduct != null) ...[
              const Divider(height: 24),
              Text('En tu caché de precios', style: Theme.of(context).textTheme.titleSmall),
              ProductTile(
                product: result.matchedProduct!,
                onTap: () {
                  Navigator.pop(context);
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => ProductDetailScreen(product: result.matchedProduct!),
                    ),
                  );
                },
              ),
            ],
            if (onAdd != null) ...[
              const SizedBox(height: AppSpacing.md),
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: onAdd,
                  icon: const Icon(Icons.add_shopping_cart),
                  label: const Text('Añadir a mi lista'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
