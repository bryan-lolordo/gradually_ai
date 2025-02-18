import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_calendar/calendar.dart';

/// This is the calendar screen widget for your app.
class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});

  @override
  _CalendarScreenState createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Calendar"),
        leading: IconButton(
          icon: Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SfCalendar(
        view: CalendarView.day,  // Set the calendar view to day
      dataSource: MeetingDataSource(_getDataSource()),
      timeSlotViewSettings: TimeSlotViewSettings(
        startHour: 6,  // Adjust start hour as needed
        endHour: 22,   // Adjust end hour as needed
        nonWorkingDays: <int>[DateTime.saturday, DateTime.sunday],  // Optional
        timeIntervalHeight: 70,  // Adjust the height of each time slot
        timeFormat: 'h:mm a',  // Adjust the time format
      ),
    ));
  }

  List<Meeting> _getDataSource() {
    final List<Meeting> meetings = <Meeting>[];
    final DateTime today = DateTime.now();
    final DateTime startTime = DateTime(today.year, today.month, today.day, 9);
    final DateTime endTime = startTime.add(const Duration(hours: 2));
    meetings.add(Meeting(
        'Conference', startTime, endTime, const Color(0xFF0F8644), false));
    return meetings;
  }
}

/// Custom data source class for the calendar
class MeetingDataSource extends CalendarDataSource {
  MeetingDataSource(List<Meeting> source) {
    appointments = source;
  }

  @override
  DateTime getStartTime(int index) => _getMeetingData(index).from;
  @override
  DateTime getEndTime(int index) => _getMeetingData(index).to;
  @override
  String getSubject(int index) => _getMeetingData(index).eventName;
  @override
  Color getColor(int index) => _getMeetingData(index).background;
  @override
  bool isAllDay(int index) => _getMeetingData(index).isAllDay;

  Meeting _getMeetingData(int index) => appointments![index] as Meeting;
}

class Meeting {
  Meeting(this.eventName, this.from, this.to, this.background, this.isAllDay);

  String eventName;
  DateTime from;
  DateTime to;
  Color background;
  bool isAllDay;
}
