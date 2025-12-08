import 'package:flutter/foundation.dart';
import '../../core/api_client.dart';

class StudentProvider with ChangeNotifier {
  final ApiClient _apiClient = ApiClient();
  List<dynamic> _classes = [];
  List<dynamic> _grades = [];
  bool _isLoading = false;
  String? _error;

  List<dynamic> get classes => _classes;
  List<dynamic> get grades => _grades;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchClasses() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiClient.client.get('/students/my-classes');
      _classes = response.data;
    } catch (e) {
      _error = 'Failed to load classes';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchGrades() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiClient.client.get('/students/my-grades');
      _grades = response.data;
    } catch (e) {
      _error = 'Failed to load grades';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
