import React, {createContext, useEffect, useState} from 'react';
import { getValueFromStorageByKey } from '../store/storage';

const AuthContext = createContext(null);
const {Provider} = AuthContext;

const AuthProvider = ({children}) => {
  const [authState, setAuthState] = useState({
    accessToken: null,
    refreshToken: null,
    authenticated: null,
  });
  const [status, setStatus] = useState('idle');

  useEffect(() => {
    setStatus('loading');
    try {
      const getJWT = getValueFromStorageByKey('token');
      getJWT.then(tokens => {
        let jwt = JSON.parse(tokens);

        setAuthState({
          accessToken: jwt.access || null,
          refreshToken: jwt.refresh || null,
          authenticated: jwt.access !== null,
        });
      });
      setStatus('success');
    } catch(error) {
      console.log(error);
      setStatus('error');
    }
  }, []);

  const getAccessToken = () => {
    return authState.accessToken;
  };

  if (status === 'loading') {
    return (<Spinner />);
  }

  return (
    <Provider
      value={{
        authState,
        setAuthState,
        getAccessToken,
      }}>
      {children}
    </Provider>
  );
};

export {AuthContext, AuthProvider};