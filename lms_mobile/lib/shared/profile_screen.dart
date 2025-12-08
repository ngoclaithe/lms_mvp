import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../core/api_client.dart';
import '../features/auth/auth_provider.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final ApiClient _apiClient = ApiClient();
  Map<String, dynamic>? _profile;
  bool _isLoading = true;
  bool _isEditing = false;
  final _emailController = TextEditingController();
  final _phoneController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    final role = context.read<AuthProvider>().role;
    final endpoint = role == UserRole.student ? '/students/me' : '/lecturers/me';

    try {
      final response = await _apiClient.client.get(endpoint);
      setState(() {
        _profile = response.data;
        _emailController.text = _profile?['email'] ?? '';
        _phoneController.text = _profile?['phone_number'] ?? '';
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _updateProfile() async {
    final role = context.read<AuthProvider>().role;
    final endpoint = role == UserRole.student ? '/students/me' : '/lecturers/me';

    try {
      await _apiClient.client.put(endpoint, data: {
        'email': _emailController.text,
        'phone_number': _phoneController.text,
        'full_name': _profile?['full_name'], // Keep existing name
      });
      
      setState(() {
        _isEditing = false;
        _profile?['email'] = _emailController.text;
        _profile?['phone_number'] = _phoneController.text;
      });
      
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cập nhật hồ sơ thành công')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Lỗi cập nhật hồ sơ')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_profile == null) return const Center(child: Text('Không thể tải hồ sơ'));

    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          const CircleAvatar(
            radius: 50,
            child: Icon(Icons.person, size: 50),
          ),
          const SizedBox(height: 16),
          Text(
            _profile?['full_name'] ?? 'No Name',
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          Text(
            '@${_profile?['username']}',
            style: const TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 32),
          TextField(
            controller: _emailController,
            enabled: _isEditing,
            decoration: const InputDecoration(
              labelText: 'Email',
              prefixIcon: Icon(Icons.email),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _phoneController,
            enabled: _isEditing,
            decoration: const InputDecoration(
              labelText: 'Số điện thoại',
              prefixIcon: Icon(Icons.phone),
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                if (_isEditing) {
                  _updateProfile();
                } else {
                  setState(() => _isEditing = true);
                }
              },
              child: Text(_isEditing ? 'Lưu Thay Đổi' : 'Chỉnh Sửa'),
            ),
          ),
        ],
      ),
    );
  }
}
