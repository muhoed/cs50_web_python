import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import SettingsService from '../../services/settings.service';

interface SettingsInterface {
  id: string,
  payload: any
}

const initialState: SettingsStateType = {
  settings: {
    config: {},
    status: 'idle',
    error: null,
  },
};

export const fetchSettings = createAsyncThunk('settings/fetchSettings', async () => {
  const response = await SettingsService.getSettings();
  //return response.data[0];
  return (await response.data[0].json()) as ConfigType;
});

export const setSettings 
    = createAsyncThunk<ConfigType, SettingsInterface>('settings/setSettings', async ({id, payload}: SettingsInterface) => {
  const response = await SettingsService.updateSettings(id, payload);
  //return response.data;
  return (await response.data.json()) as ConfigType;
});

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    settingsReset(state) {
      state.settings.config = {};
      state.settings.status = 'idle';
      state.settings.error = null;
    },
  },
  extraReducers(builder) {
    builder
      .addCase(fetchSettings.pending, (state) => {
        state.settings.status = 'loading';
      })
      .addCase(fetchSettings.fulfilled, (state, action) => {
        state.settings.status = 'succeeded';
        state.settings.config = action.payload;
        state.settings.error = null;
      })
      .addCase(fetchSettings.rejected, (state, action) => {
        state.settings.status = 'failed';
        state.settings.error = action.error.message;
      })
      .addCase(setSettings.pending, (state) => {
        state.settings.status = 'updating';
      })
      .addCase(setSettings.fulfilled, (state, action) => {
        state.settings.status = 'succeeded';
        state.settings.config = action.payload;
        state.settings.error = null;
      })
      .addCase(setSettings.rejected, (state, action) => {
        state.settings.status = 'failed';
        state.settings.error = action.error.message;
      });
  },
});

export const { settingsReset } = settingsSlice.actions;

export default settingsSlice.reducer;