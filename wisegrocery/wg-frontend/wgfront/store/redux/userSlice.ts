import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import AuthService from "../../services/auth.service";

type UserType = {
  username: string,
  email: string | null,
  password: string | null,
  password1: string | null,
  password2: string | null
}

const initialState: UserStateType = {
  user: {
    auth: {
      accessToken: null,
      refreshToken: null,
      authenticated: false,
    },
    status: 'idle',
    error: null,
  },
};

export const registerUser = createAsyncThunk<any, UserType>('user/registerUser', async ({username, email, password1, password2}) => {
  try {
    const response = await AuthService.register(username, email ?? "", password1 ?? "", password2 ?? "");
    //console.log('Response: ');
    //console.log(response);
    return Promise.resolve(response.data);
  } catch (error: any) {
    if (error.response?.data) {
      throw new Error(JSON.stringify(error.response.data));
    } else {
      throw new Error(JSON.stringify(error.message));
    }
  }
});

export const loginUser = createAsyncThunk<any, UserType>('user/loginUser', async ({username, password}) => {
  try {
    const response = await AuthService.login(username, password ?? "");
    return Promise.resolve(response.data);
  } catch (error: any) {
    if (error.response?.data) {
      throw new Error(JSON.stringify(error.response.data));
    } else {
      throw new Error(JSON.stringify(error.message));
    }
  }
});

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    refreshUserTokens(state, action) {
        state.user.auth.accessToken = action.payload.access;
        state.user.auth.refreshToken = action.payload.refresh;
    },
    logoutUser(state) {
      state.user = initialState.user;
    },
  },
  extraReducers(builder) {
    builder
      .addCase(registerUser.pending, (state) => {
        state.user.status = 'loading';
      })
      .addCase(registerUser.fulfilled, (state) => {
        state.user.status = 'succeeded';
        state.user.error = null;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.user.status = 'failed';
        state.user.error = action.error;
        state.user.auth = initialState.user.auth;
      })
      .addCase(loginUser.pending, (state) => {
        state.user.status = 'loading';
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.user.status = 'succeeded';
        state.user.auth.accessToken = action.payload.access;
        state.user.auth.refreshToken = action.payload.refresh;
        state.user.auth.authenticated = true;
        state.user.error = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.user.status = 'failed';
        state.user.error = action.error;
        state.user.auth = initialState.user.auth;
      });
  },
});

export const { logoutUser, refreshUserTokens } = userSlice.actions;

export default userSlice.reducer;