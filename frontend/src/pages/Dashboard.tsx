import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActionArea,
  IconButton,
  useTheme,
  useMediaQuery,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Today as TodayIcon,
  Settings as SettingsIcon,
  ChevronRight as ChevronRightIcon,
  AccessTime as AccessTimeIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';

const Dashboard = () => {
  const [userData, setUserData] = useState<{ email?: string; username?: string }>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        console.log('Fetching user data for Dashboard...');
        const response = await api.get('/users/me');
        console.log('Dashboard user data response:', response.data);
        setUserData(response.data);
        setError(null);
      } catch (error) {
        console.error('Failed to fetch user data:', error);
        setError('Failed to load user data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchUserData();
  }, [navigate]);

  const quickActions = [
    {
      title: 'Calendar View',
      description: 'View your schedule in a 24-hour calendar format',
      icon: <TodayIcon fontSize="large" />,
      onClick: () => navigate('/calendar'),
      color: theme.palette.primary.main,
    },
    {
      title: 'Daily Schedule',
      description: 'View and manage your schedule for today',
      icon: <ScheduleIcon fontSize="large" />,
      onClick: () => navigate('/daily-schedule'),
      color: theme.palette.secondary.main,
    },
    {
      title: 'Baseline Schedule',
      description: 'Set up your default daily schedule template',
      icon: <AccessTimeIcon fontSize="large" />,
      onClick: () => navigate('/baseline-schedule'),
      color: theme.palette.info.main,
    },
    {
      title: 'Profile Settings',
      description: 'Update your account information and preferences',
      icon: <PersonIcon fontSize="large" />,
      onClick: () => navigate('/profile'),
      color: theme.palette.grey[700],
    },
  ];

  return (
    <Box sx={{ height: '100%', width: '100%', p: 3 }}>
      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {/* Loading State */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Welcome Section */}
          <Box 
            sx={{ 
              mb: 4,
              p: 3,
              background: theme.palette.primary.main,
              color: 'white',
              borderRadius: 2,
              boxShadow: 3,
            }}
          >
            <Typography variant={isMobile ? "h5" : "h4"} component="h1" gutterBottom fontWeight="bold">
              Welcome{userData.username ? `, ${userData.username}` : ''}!
            </Typography>
            <Typography variant="body1">
              Manage your schedule and access all features from your personalized dashboard.
            </Typography>
          </Box>

          {/* Quick Actions Grid */}
          <Grid container spacing={3}>
            {quickActions.map((action, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Card 
                  sx={{ 
                    height: '100%',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 6,
                    },
                  }}
                >
                  <CardActionArea 
                    onClick={action.onClick}
                    sx={{ height: '100%', p: 2 }}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <Box sx={{ 
                          p: 1,
                          borderRadius: 1,
                          backgroundColor: action.color + '20',
                          color: action.color,
                        }}>
                          {action.icon}
                        </Box>
                        <ChevronRightIcon 
                          sx={{ 
                            ml: 'auto',
                            color: theme.palette.text.secondary,
                          }} 
                        />
                      </Box>
                      <Typography variant="h6" component="h2" gutterBottom>
                        {action.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {action.description}
                      </Typography>
                    </CardContent>
                  </CardActionArea>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Overview Section */}
          <Paper 
            elevation={2} 
            sx={{ 
              mt: 4, 
              p: 3,
              borderRadius: 2,
              backgroundColor: theme.palette.background.default,
            }}
          >
            <Typography variant="h6" gutterBottom color="primary">
              Getting Started
            </Typography>
            <Typography variant="body1" paragraph>
              Start by setting up your Baseline Schedule - this will be your default daily schedule template.
              Then, check your Daily Schedule to see today's tasks and track your progress.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Need assistance? Our support team is here to help you 24/7.
            </Typography>
          </Paper>
        </>
      )}
    </Box>
  );
};

export default Dashboard; 