import 'package:flutter/material.dart';
import '../../core/api_client.dart';

class LecturerClassDetailScreen extends StatefulWidget {
  final int classId;
  final String courseName;

  const LecturerClassDetailScreen({
    super.key,
    required this.classId,
    required this.courseName,
  });

  @override
  State<LecturerClassDetailScreen> createState() =>
      _LecturerClassDetailScreenState();
}

class _LecturerClassDetailScreenState extends State<LecturerClassDetailScreen> {
  final ApiClient _apiClient = ApiClient();
  List<dynamic> _students = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchStudents();
  }

  Future<void> _fetchStudents() async {
    try {
      final response = await _apiClient.client.get(
        '/lecturers/my-classes/${widget.classId}/students',
      );
      setState(() {
        _students = response.data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Failed to load students';
        _isLoading = false;
      });
    }
  }

  Future<void> _updateGrade(int enrollmentId, double newGrade) async {
    try {
      await _apiClient.client.put(
        '/lecturers/grades',
        data: {'enrollment_id': enrollmentId, 'grade': newGrade},
      );
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Grade updated successfully')),
      );
      _fetchStudents(); // Refresh list
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Failed to update grade')));
    }
  }

  void _showGradeDialog(dynamic student) {
    final gradeController = TextEditingController(
      text: student['grade']?.toString() ?? '',
    );

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Grade for ${student['student_name']}'),
        content: TextField(
          controller: gradeController,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          decoration: const InputDecoration(labelText: 'Enter Grade (0-10)'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final grade = double.tryParse(gradeController.text);
              if (grade != null && grade >= 0 && grade <= 10) {
                _updateGrade(student['enrollment_id'], grade);
                Navigator.pop(context);
              } else {
                // Show validation error
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.courseName)),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? Center(child: Text(_error!))
          : ListView.builder(
              itemCount: _students.length,
              itemBuilder: (context, index) {
                final student = _students[index];
                return ListTile(
                  leading: CircleAvatar(
                    child: Text(student['student_nam']?[0] ?? 'S'),
                  ),
                  title: Text(student['student_name'] ?? 'Unknown'),
                  subtitle: Text(
                    'MSSV: ${student['student_id']}',
                  ), // Assuming student_id is MSSV for display
                  trailing: Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: student['grade'] != null
                          ? Colors.green[100]
                          : Colors.grey[200],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      student['grade']?.toString() ?? 'N/A',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                  onTap: () => _showGradeDialog(student),
                );
              },
            ),
    );
  }
}
