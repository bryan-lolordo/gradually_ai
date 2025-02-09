import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/api_service.dart';

class DailyAgendaScreen extends StatefulWidget {
  const DailyAgendaScreen({Key? key}) : super(key: key);

  @override
  _DailyAgendaScreenState createState() => _DailyAgendaScreenState();
}

class _DailyAgendaScreenState extends State<DailyAgendaScreen> {
  List<dynamic> aiSuggestedTasks = [];
  List<String> completedTasks = [];

  @override
  void initState() {
    super.initState();
    _loadAgenda();
  }

  Future<void> _loadAgenda() async {
    try {
      final tasks = await ApiService.fetchHabitAdjustments(1);  // Replace 1 with actual userId
      setState(() {
        aiSuggestedTasks = tasks;
      });
    } catch (error) {
      print("Error fetching agenda: $error");
    }
  }

  void markTaskAsCompleted(String habit, String suggestedChange) {
    setState(() {
      completedTasks.add("$habit - ${DateFormat('hh:mm a').format(DateTime.now())}");
      aiSuggestedTasks.removeWhere((task) => task['habit'] == habit);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Daily Agenda")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Expanded(
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text("AI Suggested Schedule", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        Expanded(
                          child: ListView.builder(
                            itemCount: aiSuggestedTasks.length,
                            itemBuilder: (context, index) {
                              final task = aiSuggestedTasks[index];
                              return Card(
                                child: ListTile(
                                  title: Text("${task['habit']} → ${task['suggested_change']}"),
                                  trailing: ElevatedButton(
                                    onPressed: () => markTaskAsCompleted(task['habit'], task['suggested_change']),
                                    child: const Text("Log"),
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text("Your Logged Schedule", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        Expanded(
                          child: ListView.builder(
                            itemCount: completedTasks.length,
                            itemBuilder: (context, index) {
                              return Card(
                                child: ListTile(
                                  title: Text(completedTasks[index]),
                                ),
                              );
                            },
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
