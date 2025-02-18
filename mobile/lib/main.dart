import 'package:flutter/material.dart';
import 'screens/navigator_screen.dart';  // Ensure the file path is correct

void main() {
  runApp(const GraduallyAI());
}

class GraduallyAI extends StatelessWidget {
  const GraduallyAI({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Gradually AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: Colors.grey[200],
      ),
      home: const NavigatorScreen(),  // Ensure this screen exists in the screens folder
    );
  }
}
