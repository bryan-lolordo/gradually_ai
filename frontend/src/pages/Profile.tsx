import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Grid,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { Edit as EditIcon, Save as SaveIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';

interface UserData {
  id?: number;
  username?: string;
  email?: string;
  timezone?: string;
  created_at?: string;
}

const Profile = () => {
  const [userData, setUserData] = useState<UserData>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState<UserData>({});
  const [saveLoading, setSaveLoading] = useState(false);
  
  const theme = useTheme();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        console.log('Fetching user data for Profile...');
        const response = await api.get('/api/users/me');
        console.log('Profile user data response:', response.data);
        setUserData(response.data);
        setEditedData(response.data);
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

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = async () => {
    try {
      setSaveLoading(true);
      const response = await api.put('/api/users/me', editedData);
      setUserData(response.data);
      setIsEditing(false);
      setError(null);
    } catch (error) {
      console.error('Failed to update user data:', error);
      setError('Failed to update user data. Please try again later.');
    } finally {
      setSaveLoading(false);
    }
  };

  const handleCancel = () => {
    setEditedData(userData);
    setIsEditing(false);
  };

  const handleChange = (field: keyof UserData) => (event: React.ChangeEvent<HTMLInputElement>) => {
    setEditedData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
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
            Profile Settings
          </Typography>
          {!isEditing ? (
            <Button
              startIcon={<EditIcon />}
              variant="contained"
              onClick={handleEdit}
              color="primary"
            >
              Edit Profile
            </Button>
          ) : (
            <Box>
              <Button
                variant="outlined"
                onClick={handleCancel}
                sx={{ mr: 1 }}
                disabled={saveLoading}
              >
                Cancel
              </Button>
              <Button
                startIcon={saveLoading ? <CircularProgress size={20} /> : <SaveIcon />}
                variant="contained"
                onClick={handleSave}
                disabled={saveLoading}
              >
                Save Changes
              </Button>
            </Box>
          )}
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Username"
              value={isEditing ? editedData.username : userData.username}
              onChange={handleChange('username')}
              disabled={!isEditing}
              variant="outlined"
              sx={{ mb: 2 }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Email"
              value={isEditing ? editedData.email : userData.email}
              onChange={handleChange('email')}
              disabled={!isEditing}
              variant="outlined"
              sx={{ mb: 2 }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Timezone"
              value={isEditing ? editedData.timezone : userData.timezone}
              onChange={handleChange('timezone')}
              disabled={!isEditing}
              variant="outlined"
              sx={{ mb: 2 }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Member Since"
              value={new Date(userData.created_at || '').toLocaleDateString()}
              disabled
              variant="outlined"
              sx={{ mb: 2 }}
            />
          </Grid>
        </Grid>

        <Box sx={{ mt: 4 }}>
          <Typography variant="h6" gutterBottom color="primary">
            Account Security
          </Typography>
          <Button
            variant="outlined"
            color="primary"
            onClick={() => navigate('/change-password')}
          >
            Change Password
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default Profile; 