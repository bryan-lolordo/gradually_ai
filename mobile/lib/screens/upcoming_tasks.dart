import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';

class UpcomingTasksScreen extends StatefulWidget {
  const UpcomingTasksScreen({Key? key}) : super(key: key);

  @override
  _UpcomingTasksScreenState createState() => _UpcomingTasksScreenState();
}

class _UpcomingTasksScreenState extends State<UpcomingTasksScreen> {
  String currentTime = DateFormat('hh:mm a').format(DateTime.now());
  List<dynamic> tasks = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadUpcomingTasks();
    _updateTime();
  }

  /// 🔄 Automatically updates the time every minute
  void _updateTime() {
    Future.delayed(const Duration(seconds: 60), () {
      if (mounted) {
        setState(() {
          currentTime = DateFormat('hh:mm a').format(DateTime.now());
        });
        _updateTime();
      }
    });
  }

  /// 📡 Fetches upcoming tasks from API
  Future<void> _loadUpcomingTasks() async {
    try {
      final fetchedTasks = await ApiService.fetchUpcomingTasks(1);
      setState(() {
        tasks = fetchedTasks;
        isLoading = false;
      });
    } catch (error) {
      debugPrint("Error fetching upcoming tasks: $error");
      setState(() {
        isLoading = false;
      });
    }
  }

  /// ✅ Marks task as completed (toggles checkbox)
  void markTaskComplete(int index) {
    setState(() {
      tasks[index]["completed"] = !tasks[index]["completed"];
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Upcoming Tasks")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            /// ⏳ **Current Time Display**
            Center(
              child: Text(
                currentTime,
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 20),

            /// 🔄 **Loading Indicator**
            if (isLoading)
              const Center(child: CircularProgressIndicator()),

            /// 📌 **Task List or Empty Message**
            if (!isLoading && tasks.isEmpty)
              const Center(
                child: Text(
                  "No upcoming tasks.",
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),

            if (!isLoading && tasks.isNotEmpty)
              Expanded(
                child: ListView.builder(
                  itemCount: tasks.length,
                  itemBuilder: (context, index) {
                    final task = tasks[index];
                    return Card(
                      child: ListTile(
                        title: Text("${task['time']} - ${task['task']}"),
                        trailing: IconButton(
                          icon: Icon(
                            task["completed"] ? Icons.check_box : Icons.check_box_outline_blank,
                            color: task["completed"] ? Colors.green : null,
                          ),
                          onPressed: () => markTaskComplete(index),
                        ),
                      ),
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}
