import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Alert,
  CircularProgress,
  useTheme,
  useMediaQuery,
  IconButton,
  Button,
  TextField,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  CheckCircleOutline as CheckCircleOutlineIcon,
  AccessTime as AccessTimeIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Add as AddIcon,
  DragIndicator as DragIndicatorIcon,
} from '@mui/icons-material';
import type { DropResult } from 'react-beautiful-dnd';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

interface Task {
  task_name: string;
  scheduled_time: string;
  goal_time: string | null;
  status: string;
  actual_completed_time?: string;
}

const Calendar = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [isAddTaskOpen, setIsAddTaskOpen] = useState(false);
  const [newTaskName, setNewTaskName] = useState('');
  const [selectedTask, setSelectedTask] = useState('');
  const [selectedTime, setSelectedTime] = useState<Date | null>(null);

  // Generate time slots for 24 hours
  const timeSlots = Array.from({ length: 24 }, (_, i) => 
    `${i.toString().padStart(2, '0')}:00:00`
  );

  const fetchDailySchedule = async (date: string) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await axios.get(`http://localhost:8000/daily_schedule/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'User-Timezone': Intl.DateTimeFormat().resolvedOptions().timeZone
        },
        params: {
          date: date
        }
      });

      if (response.data.schedule) {
        setTasks(response.data.schedule);
      } else {
        await axios.post(`http://localhost:8000/daily_schedule/generate/${userId}`, {
          date: date
        });
        const newResponse = await axios.get(`http://localhost:8000/daily_schedule/${userId}`, {
          headers: {
            'Authorization': userId,
            'User-Timezone': Intl.DateTimeFormat().resolvedOptions().timeZone
          },
          params: {
            date: date
          }
        });
        if (newResponse.data.schedule) {
          setTasks(newResponse.data.schedule);
        }
      }
      setError(null);
    } catch (error) {
      console.error('Failed to fetch daily schedule:', error);
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        navigate('/login');
        return;
      }
      setError('Failed to load daily schedule. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDailySchedule(selectedDate);
  }, [selectedDate, navigate]);

  const handleDateChange = (offset: number) => {
    const date = new Date(selectedDate);
    date.setDate(date.getDate() + offset);
    setSelectedDate(date.toISOString().split('T')[0]);
  };

  const formatDisplayDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleTaskComplete = async (taskName: string, completedTime: string) => {
    try {
      const userId = localStorage.getItem('userId');
      
      // Update local state with both status and completion time
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.task_name === taskName 
            ? { 
                ...task, 
                status: 'completed', 
                actual_completed_time: completedTime 
              }
            : task
        )
      );

      // Then send to backend
      await axios.post('http://localhost:8000/tasks/log', {
        tasks: [{
          user_id: Number(userId),
          task_name: taskName,
          completed: true,
          actual_completed_time: completedTime,
          log_date: selectedDate
        }]
      }, {
        headers: {
          'Authorization': userId
        }
      });

    } catch (error) {
      console.error('Failed to log task completion:', error);
      setError('Failed to update task status. Please try again later.');
      // Refresh data on error to ensure consistency
      await fetchDailySchedule(selectedDate);
    }
  };

  const handleQuickComplete = async (taskName: string) => {
    const now = new Date();
    const timeString = now.toTimeString().split(' ')[0];
    await handleTaskComplete(taskName, timeString);
  };

  const getTasksForTimeSlot = (timeSlot: string) => {
    return tasks.filter(task => {
      const taskTime = task.scheduled_time?.split(':')[0].padStart(2, '0') + ':00:00';
      return taskTime === timeSlot;
    });
  };

  const getCompletedTasksForTimeSlot = (timeSlot: string) => {
    return tasks.filter(task => {
      if (!task.actual_completed_time || task.status !== 'completed') return false;
      const completedHour = task.actual_completed_time.split(':')[0].padStart(2, '0');
      const slotHour = timeSlot.split(':')[0];
      return completedHour === slotHour;
    });
  };

  const handleDragEnd = async (result: DropResult) => {
    if (!result.destination) return;

    try {
      const taskId = result.draggableId;
      const destinationTime = timeSlots[parseInt(result.destination.droppableId)];
      const taskToUpdate = tasks.find(t => t.task_name === taskId);

      if (taskToUpdate) {
        await handleTaskComplete(taskToUpdate.task_name, destinationTime);
        await fetchDailySchedule(selectedDate);
      }
    } catch (error) {
      console.error('Failed to update task time:', error);
      setError('Failed to update task completion time');
    }
  };

  const getUncompletedTasks = () => {
    return tasks.filter(task => task.status !== 'completed');
  };

  const handleAddTaskSubmit = async () => {
    if (!selectedTime) return;

    const timeString = selectedTime.toTimeString().split(' ')[0];
    const taskName = selectedTask || newTaskName;

    if (!taskName) return;

    try {
      if (selectedTask) {
        // Log existing task
        await handleTaskComplete(taskName, timeString);
      } else {
        // Create and log new task
        const userId = localStorage.getItem('userId');
        await axios.post(`http://localhost:8000/daily_schedule/${userId}/task`, {
          task_name: taskName,
          scheduled_time: timeString,
          log_date: selectedDate
        }, {
          headers: { 'Authorization': userId }
        });
        await handleTaskComplete(taskName, timeString);
      }
      
      setIsAddTaskOpen(false);
      setNewTaskName('');
      setSelectedTask('');
      setSelectedTime(null);
      await fetchDailySchedule(selectedDate);
    } catch (error) {
      console.error('Failed to add task:', error);
      setError('Failed to add task. Please try again.');
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
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton onClick={() => handleDateChange(-1)}>
              <ChevronLeftIcon />
            </IconButton>
            <Typography variant={isMobile ? "h5" : "h4"} component="h1" sx={{ mx: 2, fontWeight: "bold" }}>
              {formatDisplayDate(selectedDate)}
            </Typography>
            <IconButton onClick={() => handleDateChange(1)}>
              <ChevronRightIcon />
            </IconButton>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setIsAddTaskOpen(true)}
          >
            Add Task
          </Button>
        </Box>

        <DragDropContext onDragEnd={handleDragEnd}>
          <Grid container spacing={2}>
            {/* Time Column */}
            <Grid item xs={2}>
              {timeSlots.map((timeSlot) => (
                <Box
                  key={timeSlot}
                  sx={{
                    height: '120px',
                    borderBottom: 1,
                    borderColor: 'divider',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Typography variant="body2" color="textSecondary">
                    {timeSlot.substring(0, 5)}
                  </Typography>
                </Box>
              ))}
            </Grid>

            {/* Scheduled Tasks Column */}
            <Grid item xs={5}>
              <Typography variant="h6" gutterBottom align="center">
                Scheduled Tasks
              </Typography>
              {timeSlots.map((timeSlot) => {
                const slotTasks = getTasksForTimeSlot(timeSlot);
                return (
                  <Box
                    key={timeSlot}
                    sx={{
                      height: '120px',
                      borderBottom: 1,
                      borderColor: 'divider',
                      p: 1,
                    }}
                  >
                    {slotTasks.map((task) => (
                      <Paper
                        key={task.task_name}
                        sx={{
                          p: 1,
                          mb: 1,
                          backgroundColor: theme.palette.primary.light,
                          color: 'white',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                        }}
                      >
                        <Box>
                          <Typography variant="body2">
                            {task.task_name}
                          </Typography>
                          <Typography variant="caption">
                            {task.scheduled_time}
                          </Typography>
                        </Box>
                        <Tooltip title="Mark as completed now">
                          <IconButton
                            size="small"
                            onClick={() => handleQuickComplete(task.task_name)}
                            sx={{ color: 'white' }}
                          >
                            {task.status === 'completed' 
                              ? <CheckCircleIcon /> 
                              : <CheckCircleOutlineIcon />}
                          </IconButton>
                        </Tooltip>
                      </Paper>
                    ))}
                  </Box>
                );
              })}
            </Grid>

            {/* Actual Completion Column */}
            <Grid item xs={5}>
              <Typography variant="h6" gutterBottom align="center">
                Actual Completion
              </Typography>
              {timeSlots.map((timeSlot, index) => (
                <Droppable droppableId={index.toString()} key={timeSlot}>
                  {(provided) => (
                    <Box
                      ref={provided.innerRef}
                      {...provided.droppableProps}
                      sx={{
                        height: '120px',
                        borderBottom: 1,
                        borderColor: 'divider',
                        p: 1,
                      }}
                    >
                      {getCompletedTasksForTimeSlot(timeSlot).map((task, taskIndex) => (
                        <Draggable
                          key={task.task_name}
                          draggableId={task.task_name}
                          index={taskIndex}
                        >
                          {(provided, snapshot) => (
                            <Paper
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              sx={{
                                p: 1,
                                mb: 1,
                                backgroundColor: theme.palette.success.light,
                                color: 'white',
                                opacity: snapshot.isDragging ? 0.8 : 1,
                              }}
                            >
                              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                  <div {...provided.dragHandleProps}>
                                    <DragIndicatorIcon sx={{ mr: 1 }} />
                                  </div>
                                  <Typography variant="body2">
                                    {task.task_name}
                                  </Typography>
                                </Box>
                                <Typography variant="caption">
                                  {task.actual_completed_time}
                                </Typography>
                              </Box>
                            </Paper>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </Box>
                  )}
                </Droppable>
              ))}
            </Grid>
          </Grid>
        </DragDropContext>
      </Paper>

      {/* Add Task Dialog */}
      <Dialog open={isAddTaskOpen} onClose={() => setIsAddTaskOpen(false)}>
        <DialogTitle>Add Task</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, minWidth: 300, mt: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Select Existing Task</InputLabel>
              <Select
                value={selectedTask}
                onChange={(e) => {
                  setSelectedTask(e.target.value);
                  setNewTaskName('');
                }}
              >
                <MenuItem value="">
                  <em>Add New Task</em>
                </MenuItem>
                {getUncompletedTasks().map(task => (
                  <MenuItem key={task.task_name} value={task.task_name}>
                    {task.task_name} ({task.scheduled_time})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {!selectedTask && (
              <TextField
                label="New Task Name"
                value={newTaskName}
                onChange={(e) => setNewTaskName(e.target.value)}
                fullWidth
              />
            )}

            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <TimePicker
                label="Completion Time"
                value={selectedTime}
                onChange={(newValue) => setSelectedTime(newValue)}
              />
            </LocalizationProvider>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsAddTaskOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleAddTaskSubmit}
            disabled={(!selectedTask && !newTaskName) || !selectedTime}
          >
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Calendar; 