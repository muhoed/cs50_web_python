import React, {createContext, useContext} from 'react';
import axios from 'axios';
import {AuthContext} from './AuthContext';
import createAuthRefreshInterceptor from 'axios-auth-refresh';
import { useDispatch } from 'react-redux';

import { deleteValueFromStorageForKey, saveToStorage } from '../store/storage';
import { settingsReset } from '../store/redux/settingsSlice';

const AxiosContext = createContext();
const {Provider} = AxiosContext;

const AxiosProvider = ({children}) => {
  const authContext = useContext(AuthContext);
  const dispatch = useDispatch();

  const authAxios = axios.create({
    baseURL: 'http://localhost:8000/api',
  });

  const publicAxios = axios.create({
    baseURL: 'http://localhost:8000/api',
  });

  authAxios.interceptors.request.use(
    config => {
      if (!config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${authContext.getAccessToken()}`;
      }

      return config;
    },
    error => {
      return Promise.reject(error);
    },
  );

  const refreshAuthLogic = async (failedRequest) => {
    const data = {
      refresh: authContext.authState.refreshToken,
    };

    const options = {
      method: 'POST',
      data,
      url: 'http://localhost:8000/api/token/refresh/',
    };

    return await axios(options)
      .then(async (tokenRefreshResponse) => {
        failedRequest.response.config.headers.Authorization =
          'Bearer ' + tokenRefreshResponse.data.access;

        authContext.setAuthState({
          ...authContext.authState,
          accessToken: tokenRefreshResponse.data.access,
        });

        await saveToStorage(
          'token',
          JSON.stringify({
            access: tokenRefreshResponse.data.access,
            refresh: tokenRefreshResponse.data.refresh,
          }),
        );

        return Promise.resolve();
      })
      .catch(e => {
        console.log('Error refresh token: ' + e + '. Please re-login.');
        authContext.setAuthState({
          accessToken: null,
          refreshToken: null,
        });
        deleteValueFromStorageForKey('token');
        dispatch(settingsReset());
      });
  };

  createAuthRefreshInterceptor(authAxios, refreshAuthLogic, {});

  return (
    <Provider
      value={{
        authAxios,
        publicAxios,
      }}>
      {children}
    </Provider>
  );
};

export {AxiosContext, AxiosProvider};