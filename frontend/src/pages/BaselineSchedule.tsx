import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  Alert,
  CircularProgress,
  Grid,
  TextField,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Save as SaveIcon } from '@mui/icons-material';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface Task {
  task_name: string;
  scheduled_time: string;
  goal_time?: string;
}

const BaselineSchedule = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveLoading, setSaveLoading] = useState(false);
  const [newTask, setNewTask] = useState<Task>({ task_name: '', scheduled_time: '' });
  
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    const fetchBaselineSchedule = async () => {
      try {
        const userId = localStorage.getItem('userId');
        if (!userId) {
          navigate('/login');
          return;
        }
        
        const response = await axios.get(`http://localhost:8000/baseline_schedule/${userId}`);
        if (response.data.tasks) {
          setTasks(response.data.tasks);
        }
        setError(null);
      } catch (error) {
        console.error('Failed to fetch baseline schedule:', error);
        setError('Failed to load baseline schedule. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchBaselineSchedule();
  }, [navigate]);

  const handleAddTask = () => {
    if (newTask.task_name && newTask.scheduled_time) {
      setTasks([...tasks, newTask]);
      setNewTask({ task_name: '', scheduled_time: '' });
    }
  };

  const handleDeleteTask = (index: number) => {
    const updatedTasks = tasks.filter((_, i) => i !== index);
    setTasks(updatedTasks);
  };

  const handleSave = async () => {
    try {
      setSaveLoading(true);
      const userId = localStorage.getItem('userId');
      
      await axios.post('http://localhost:8000/baseline_schedule/set', {
        user_id: userId,
        tasks: tasks
      });
      
      setError(null);
    } catch (error) {
      console.error('Failed to save baseline schedule:', error);
      setError('Failed to save baseline schedule. Please try again later.');
    } finally {
      setSaveLoading(false);
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
            Baseline Schedule
          </Typography>
          <Button
            startIcon={saveLoading ? <CircularProgress size={20} /> : <SaveIcon />}
            variant="contained"
            onClick={handleSave}
            disabled={saveLoading}
          >
            Save Schedule
          </Button>
        </Box>

        <Typography variant="body1" sx={{ mb: 3 }}>
          Set your default daily schedule. This will be used as a template for generating your daily schedules.
        </Typography>

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Task Name"
              value={newTask.task_name}
              onChange={(e) => setNewTask({ ...newTask, task_name: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Scheduled Time"
              type="time"
              value={newTask.scheduled_time}
              onChange={(e) => setNewTask({ ...newTask, scheduled_time: e.target.value + ':00' })}
              InputLabelProps={{ shrink: true }}
              inputProps={{ step: 300 }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Goal Time (Optional)"
              type="time"
              value={newTask.goal_time || ''}
              onChange={(e) => setNewTask({ ...newTask, goal_time: e.target.value ? e.target.value + ':00' : undefined })}
              InputLabelProps={{ shrink: true }}
              inputProps={{ step: 300 }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleAddTask}
              disabled={!newTask.task_name || !newTask.scheduled_time}
              sx={{ height: '100%' }}
            >
              Add Task
            </Button>
          </Grid>
        </Grid>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Task Name</TableCell>
                <TableCell>Scheduled Time</TableCell>
                <TableCell>Goal Time</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tasks.map((task, index) => (
                <TableRow key={index}>
                  <TableCell>{task.task_name}</TableCell>
                  <TableCell>{task.scheduled_time}</TableCell>
                  <TableCell>{task.goal_time || '-'}</TableCell>
                  <TableCell align="right">
                    <IconButton onClick={() => handleDeleteTask(index)} color="error">
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {tasks.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No tasks added yet. Add your first task above.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default BaselineSchedule; 