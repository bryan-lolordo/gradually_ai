import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Alert,
  CircularProgress,
  useTheme,
  IconButton,
  Chip,
  Divider,
} from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Event as EventIcon,
} from '@mui/icons-material';
import { format, addDays, parseISO } from 'date-fns';
import api from '../utils/api';
import { useNavigate } from 'react-router-dom';

interface Task {
  task_name: string;
  scheduled_time: string;
  goal_time: string | null;
  status: string;
}

interface DailySchedule {
  user_id: number;
  log_date: string;
  current_timezone: string;
  schedule: Task[];
}

const UpcomingTasks = () => {
  const [schedules, setSchedules] = useState<DailySchedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState(new Date());
  const theme = useTheme();
  const navigate = useNavigate();

  const fetchUpcomingSchedules = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      
      // Fetch schedules for the next 7 days
      const schedulesData = [];
      for (let i = 0; i < 7; i++) {
        const date = format(addDays(startDate, i), 'yyyy-MM-dd');
        const response = await api.get(`/daily_schedule/${token}?date=${date}`);
        if (response.data.schedule && Array.isArray(response.data.schedule)) {
          schedulesData.push(response.data);
        }
      }
      
      setSchedules(schedulesData);
    } catch (err: any) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError(err.response?.data?.detail || 'Failed to fetch upcoming tasks');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUpcomingSchedules();
  }, [startDate]);

  const handlePreviousWeek = () => {
    setStartDate(prev => addDays(prev, -7));
  };

  const handleNextWeek = () => {
    setStartDate(prev => addDays(prev, 7));
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, justifyContent: 'space-between' }}>
        <Typography variant="h4" component="h1">
          Upcoming Tasks
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton onClick={handlePreviousWeek}>
            <ChevronLeftIcon />
          </IconButton>
          <Typography variant="subtitle1">
            {format(startDate, 'MMM d')} - {format(addDays(startDate, 6), 'MMM d, yyyy')}
          </Typography>
          <IconButton onClick={handleNextWeek}>
            <ChevronRightIcon />
          </IconButton>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {schedules.map((schedule, index) => (
          <Grid item xs={12} key={schedule.log_date}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <EventIcon sx={{ mr: 1, color: theme.palette.primary.main }} />
                <Typography variant="h6">
                  {format(parseISO(schedule.log_date), 'EEEE, MMMM d')}
                </Typography>
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                {schedule.schedule.map((task, taskIndex) => (
                  <Grid item xs={12} sm={6} md={4} key={`${task.task_name}-${taskIndex}`}>
                    <Paper 
                      elevation={1} 
                      sx={{ 
                        p: 2, 
                        backgroundColor: theme.palette.background.default,
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 1
                      }}
                    >
                      <Typography variant="subtitle1" fontWeight="bold">
                        {task.task_name}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Chip 
                          label={`Scheduled: ${task.scheduled_time}`}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                        {task.goal_time && (
                          <Chip 
                            label={`Goal: ${task.goal_time}`}
                            size="small"
                            color="secondary"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default UpcomingTasks; 