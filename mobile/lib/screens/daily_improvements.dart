import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class DailyImprovementsScreen extends StatefulWidget {
  const DailyImprovementsScreen({super.key});

  @override
  _DailyImprovementsScreenState createState() => _DailyImprovementsScreenState();
}

class _DailyImprovementsScreenState extends State<DailyImprovementsScreen> {
  late String currentTime;

  @override
  void initState() {
    super.initState();
    currentTime = DateFormat('hh:mm a').format(DateTime.now());
    _updateTime();
  }

  void _updateTime() {
    Future.delayed(const Duration(seconds: 30), () {
      if (mounted) {
        setState(() {
          currentTime = DateFormat('hh:mm a').format(DateTime.now());
        });
        _updateTime();  // Recursive call to keep time updating
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Daily Improvements")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text("Daily Changes", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            _buildChangeCard("Go to bed", "1 AM", "12:30 AM"),
            _buildChangeCard("Eat lunch", "2:00 PM", "1:15 PM"),
            const SizedBox(height: 20),
            const Text("Habit Improvements", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            _buildProgressBar("Sleep", 0.2, "20% → 24%"),
            _buildProgressBar("Meals", 0.66, "66%"),
            _buildProgressBar("Work", 0.48, "48% → 52%"),
          ],
        ),
      ),
    );
  }

  Widget _buildChangeCard(String habit, String oldTime, String newTime) {
    return Card(
      child: ListTile(
        title: Text("$habit: $oldTime → $newTime"),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(icon: const Icon(Icons.check), onPressed: () {}),
            IconButton(icon: const Icon(Icons.close), onPressed: () {}),
            IconButton(icon: const Icon(Icons.swap_horiz), onPressed: () {}),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressBar(String habit, double progress, String label) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(habit, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 5),
          Stack(
            children: [
              Container(
                height: 20,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
              FractionallySizedBox(
                widthFactor: progress,
                child: Container(
                  height: 20,
                  decoration: BoxDecoration(
                    color: Colors.green,
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 5),
          Text(label, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
