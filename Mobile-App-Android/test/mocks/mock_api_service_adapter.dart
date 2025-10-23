import 'dart:typed_data';
import 'package:flora_seven/domain/models/api_response.dart';
import 'package:flora_seven/domain/models/plant_data.dart';
import 'package:flora_seven/domain/models/pump_status.dart';
import 'package:flora_seven/domain/models/thresholds.dart';
import 'package:flora_seven/services/api/api_service_interface.dart';
import '../providers/connection_status_provider_test.mocks.dart';

/// A mock adapter that makes MockEnhancedApiService compatible with ApiServiceInterface
class MockApiServiceAdapter implements ApiServiceInterface {
  final MockEnhancedApiService _mockApiService;

  MockApiServiceAdapter(this._mockApiService);

  @override
  Future<void> initialize() async {
    return;
  }

  @override
  Future<void> updateBaseUrl(String newBaseUrl) async {
    return;
  }

  @override
  String getBaseUrl() {
    return 'http://mock-server.com';
  }

  @override
  Future<bool> isServerAvailable() {
    return _mockApiService.isServerAvailable();
  }

  @override
  Future<Map<String, dynamic>?> getStatus() {
    return _mockApiService.getStatus();
  }

  @override
  Future<PlantData?> getPlantData() async {
    final result = await _mockApiService.getPlantData();
    return result;
  }

  @override
  Future<Uint8List?> getLatestImage() async {
    final result = await _mockApiService.getLatestImage();
    return result;
  }

  @override
  String getLatestImageUrl() {
    return _mockApiService.getLatestImageUrl();
  }

  @override
  Future<bool> uploadImage(dynamic imageBytes, String filename) {
    return _mockApiService.uploadImage(imageBytes, filename);
  }

  @override
  Future<Thresholds?> getThresholds() async {
    final result = await _mockApiService.getThresholds();
    return result;
  }

  @override
  Future<bool> updateThresholds(dynamic thresholds) {
    return _mockApiService.updateThresholds(thresholds);
  }

  @override
  Future<bool> sendWaterCommand({required bool state, required int durationSec}) {
    return _mockApiService.sendWaterCommand(state: state, durationSec: durationSec);
  }

  @override
  Future<bool> waterPlant({int durationSec = 5}) {
    return _mockApiService.waterPlant(durationSec: durationSec);
  }

  @override
  Future<bool> sendCaptureImageCommand({String resolution = 'high', bool flash = false}) {
    return _mockApiService.sendCaptureImageCommand(resolution: resolution, flash: flash);
  }

  @override
  Future<bool> sendReadNowCommand() {
    return _mockApiService.sendReadNowCommand();
  }

  @override
  Future<Map<String, dynamic>?> getHardwareStatus() {
    return _mockApiService.getHardwareStatus();
  }

  @override
  bool isConnected() {
    return _mockApiService.isConnected();
  }

  @override
  Future<bool> setAutoWatering(bool enabled) {
    return _mockApiService.setAutoWatering(enabled);
  }

  @override
  Future<PumpStatus> getPumpStatus() async {
    final result = await _mockApiService.getPumpStatus();
    return result;
  }

  @override
  Future<PumpStatus> startWatering({required int duration}) async {
    final result = await _mockApiService.startWatering(duration: duration);
    return result;
  }

  @override
  Future<PumpStatus> stopWatering() async {
    final result = await _mockApiService.stopWatering();
    return result;
  }

  @override
  Future<Map<String, dynamic>?> getConnectionStatus() {
    return _mockApiService.getConnectionStatus();
  }

  @override
  Future<List<Map<String, dynamic>>?> getHistoricalData({
    required String startTime,
    required String endTime,
    String? sensorType,
  }) {
    return _mockApiService.getHistoricalData(
      startTime: startTime,
      endTime: endTime,
      sensorType: sensorType,
    );
  }

  @override
  Future<ApiResponse> get(String endpoint, {Map<String, dynamic>? queryParams}) async {
    final result = await _mockApiService.get(endpoint, queryParams: queryParams);
    // Convert to ApiResponse
    return ApiResponse(
      success: result.success,
      data: result.data,
      message: result.message,
    );
  }

  @override
  Future<ApiResponse> post(String endpoint, {dynamic data, Map<String, dynamic>? queryParams}) async {
    final result = await _mockApiService.post(endpoint, data: data, queryParams: queryParams);
    // Convert to ApiResponse
    return ApiResponse(
      success: result.success,
      data: result.data,
      message: result.message,
    );
  }
}
