import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  IconButton,
  useTheme,
  useMediaQuery,
  Chip,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Refresh as RefreshIcon,
  AccessTime as AccessTimeIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface Task {
  task_name: string;
  scheduled_time: string;
  goal_time?: string;
  status: 'pending' | 'completed';
}

const DailySchedule = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const fetchDailySchedule = async () => {
    try {
      const userId = localStorage.getItem('userId');
      if (!userId) {
        navigate('/login');
        return;
      }
      
      const response = await axios.get(`http://localhost:8000/daily_schedule/${userId}`);
      if (response.data.schedule) {
        setTasks(response.data.schedule);
      }
      setError(null);
    } catch (error) {
      console.error('Failed to fetch daily schedule:', error);
      setError('Failed to load daily schedule. Please try again later.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDailySchedule();
  }, [navigate]);

  const handleGenerateSchedule = async () => {
    try {
      setRefreshing(true);
      const userId = localStorage.getItem('userId');
      
      await axios.post(`http://localhost:8000/daily_schedule/generate/${userId}`);
      await fetchDailySchedule();
    } catch (error) {
      console.error('Failed to generate daily schedule:', error);
      setError('Failed to generate daily schedule. Please try again later.');
      setRefreshing(false);
    }
  };

  const handleTaskComplete = async (taskName: string, completed: boolean) => {
    try {
      const userId = localStorage.getItem('userId');
      
      await axios.post('http://localhost:8000/tasks/log', {
        tasks: [{
          user_id: userId,
          task_name: taskName,
          completed,
          actual_completed_time: new Date().toLocaleTimeString('en-US', { hour12: false }),
          log_date: new Date().toISOString().split('T')[0]
        }]
      });
      
      await fetchDailySchedule();
    } catch (error) {
      console.error('Failed to update task status:', error);
      setError('Failed to update task status. Please try again later.');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return theme.palette.success.main;
      case 'pending':
        return theme.palette.warning.main;
      default:
        return theme.palette.grey[500];
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: '100%', width: '100%', p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={3} sx={{ p: 3, borderRadius: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant={isMobile ? "h5" : "h4"} component="h1" fontWeight="bold">
            Today's Schedule
          </Typography>
          <Button
            startIcon={refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
            variant="contained"
            onClick={handleGenerateSchedule}
            disabled={refreshing}
          >
            Generate Schedule
          </Button>
        </Box>

        <Typography variant="body1" sx={{ mb: 3 }}>
          Your schedule for {new Date().toLocaleDateString()}. Mark tasks as completed as you go through your day.
        </Typography>

        <Grid container spacing={2}>
          {tasks.map((task, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card 
                sx={{ 
                  height: '100%',
                  borderLeft: `4px solid ${getStatusColor(task.status)}`,
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" component="h2">
                      {task.task_name}
                    </Typography>
                    <Chip
                      label={task.status}
                      color={task.status === 'completed' ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AccessTimeIcon sx={{ mr: 1, fontSize: '1rem', color: 'text.secondary' }} />
                    <Typography variant="body2" color="text.secondary">
                      Scheduled: {task.scheduled_time}
                    </Typography>
                  </Box>
                  
                  {task.goal_time && (
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <AccessTimeIcon sx={{ mr: 1, fontSize: '1rem', color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary">
                        Goal: {task.goal_time}
                      </Typography>
                    </Box>
                  )}

                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                    <IconButton
                      color="success"
                      onClick={() => handleTaskComplete(task.task_name, true)}
                      disabled={task.status === 'completed'}
                    >
                      <CheckCircleIcon />
                    </IconButton>
                    <IconButton
                      color="error"
                      onClick={() => handleTaskComplete(task.task_name, false)}
                      disabled={task.status === 'completed'}
                    >
                      <CancelIcon />
                    </IconButton>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
          {tasks.length === 0 && (
            <Grid item xs={12}>
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body1" color="text.secondary">
                  No tasks scheduled for today. Click "Generate Schedule" to create your daily schedule.
                </Typography>
              </Box>
            </Grid>
          )}
        </Grid>
      </Paper>
    </Box>
  );
};

export default DailySchedule; 