import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../auth/auth_provider.dart';
import 'student_provider.dart';
import '../../shared/profile_screen.dart';

class StudentDashboard extends StatefulWidget {
  const StudentDashboard({super.key});

  @override
  State<StudentDashboard> createState() => _StudentDashboardState();
}

class _StudentDashboardState extends State<StudentDashboard> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    final provider = context.read<StudentProvider>();
    Future.microtask(() {
       provider.fetchClasses();
       provider.fetchGrades();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final studentProvider = context.watch<StudentProvider>();
    final authProvider = context.read<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Sinh Viên Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => authProvider.logout(),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Lớp Học', icon: Icon(Icons.class_)),
            Tab(text: 'Bảng Điểm', icon: Icon(Icons.grade)),
            Tab(text: 'Cá Nhân', icon: Icon(Icons.person)),
          ],
        ),
      ),
      body: studentProvider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : TabBarView(
              controller: _tabController,
              children: [
                // Classes Tab
                RefreshIndicator(
                  onRefresh: () => studentProvider.fetchClasses(),
                  child: studentProvider.classes.isEmpty
                      ? const Center(child: Text('Chưa đăng ký lớp học nào'))
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: studentProvider.classes.length,
                          itemBuilder: (context, index) {
                            final cls = studentProvider.classes[index];
                            return Card(
                              child: ListTile(
                                leading: const Icon(Icons.book, color: Colors.blue),
                                title: Text(cls['course_name'] ?? 'Class ${cls['id']}'),
                                subtitle: Text(
                                    'Phòng: ${cls['room'] ?? 'N/A'} - Giảng viên: ${cls['lecturer_name'] ?? 'N/A'}'),
                              ),
                            );
                          },
                        ),
                ),
                // Grades Tab
                RefreshIndicator(
                  onRefresh: () => studentProvider.fetchGrades(),
                  child: studentProvider.grades.isEmpty
                      ? const Center(child: Text('Chưa có điểm số'))
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: studentProvider.grades.length,
                          itemBuilder: (context, index) {
                            final grade = studentProvider.grades[index];
                            return Card(
                              color: grade['grade'] != null && grade['grade'] >= 5.0 ? Colors.green[50] : Colors.red[50],
                              child: ListTile(
                                leading: CircleAvatar(
                                  backgroundColor: grade['grade'] != null && grade['grade'] >= 5.0 ? Colors.green : Colors.red,
                                  child: Text(
                                    grade['grade']?.toString() ?? '?',
                                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                                  ),
                                ),
                                title: Text(grade['course_name'] ?? 'Unknown Course'),
                                subtitle: Text('Tín chỉ: ${grade['credits'] ?? 3}'),
                              ),
                            );
                          },
                        ),
                ),
                // Profile Tab
                const ProfileScreen(),
              ],
            ),
    );
  }
}
