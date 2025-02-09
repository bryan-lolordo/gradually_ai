import 'package:flutter/material.dart';
import 'daily_improvements.dart';  // Ensure the file path is correct
import 'upcoming_tasks.dart';  // Ensure the file path is correct
import 'daily_agenda_screen.dart';  // Ensure the file path is correct
import 'calendar_screen.dart';  // Ensure the file path is correct

class NavigatorScreen extends StatelessWidget {
  const NavigatorScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Main Screen")),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              child: Text('Today\'s Improvements'),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const DailyImprovementsScreen()),
              ),
            ),
            ElevatedButton(
              child: Text('Upcoming Tasks'),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => UpcomingTasksScreen()),
              ),
            ),
            ElevatedButton(
              child: Text('Daily Agenda'),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => DailyAgendaScreen()),
              ),
            ),
            ElevatedButton(
              child: Text('Calendar Screen'),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => CalendarScreen()),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
