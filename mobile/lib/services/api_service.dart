import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = "http://127.0.0.1:8000"; // Change this for deployment

  // Fetch habit adjustments
  static Future<List<dynamic>> fetchHabitAdjustments(int userId) async {
    final response = await http.get(Uri.parse("$baseUrl/adjust_habits/$userId"));
    if (response.statusCode == 200) {
      return json.decode(response.body)['adjustments'];
    } else {
      throw Exception("Failed to load habits");
    }
  }

  // Update habit status
  static Future<bool> updateHabit(int adjustmentId, String status) async {
    final response = await http.post(
      Uri.parse("$baseUrl/update_habit/$adjustmentId"),
      headers: {"Content-Type": "application/json"},
      body: json.encode({"status": status}),
    );
    return response.statusCode == 200;
  }

  // Fetch habit history
  static Future<List<dynamic>> fetchHabitHistory(int userId) async {
    final response = await http.get(Uri.parse("$baseUrl/habit_history/$userId"));
    if (response.statusCode == 200) {
      return json.decode(response.body)['accepted'];
    } else {
      throw Exception("Failed to load habit history");
    }
  }
  
  // Fetch upcoming tasks
  static Future<List<Map<String, dynamic>>> fetchUpcomingTasks(int userId) async {
    final response = await http.get(Uri.parse("$baseUrl/upcoming_tasks/$userId"));

    if (response.statusCode == 200) {
      List<dynamic> jsonData = json.decode(response.body);
      return jsonData.map((task) => Map<String, dynamic>.from(task)).toList();
    } else {
      throw Exception("Failed to load upcoming tasks");
    }
  }
}