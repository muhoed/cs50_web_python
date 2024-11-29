import 'react-native-gesture-handler';
// import '@expo/match-media';
import { Provider as StoreProvider } from "react-redux";
import { PersistGate } from 'redux-persist/integration/react';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import { useColorScheme } from '@/hooks/useColorScheme';
import { Stack } from 'expo-router';
import { useEffect } from 'react';
import 'react-native-reanimated';

import { persistor, store } from '../store/redux/store';
import Spinner from '../components/Spinner';
import setupInterceptors from '../services/setupInterceptors';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {

  setupInterceptors(store);

  const colorScheme = useColorScheme();
  const [loaded] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
  });
  // const config = {
  //   screens: {
  //     Home: 'home',
  //     Groceries: 'groceries',
  //     Products: 'products',
  //     Equipment: 'equipment',
  //     Stock: 'stock',
  //     Shopping: 'shopping',
  //     Cooking: 'cooking',
  //     Notifications: 'notifications',
  //     Settings: 'settings'
  //   },
  // };
  // const linking = {
  //   config,
  //   prefixes: []
  // };

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  return (
    <StoreProvider store={store}>
      <PersistGate loading={<Spinner />} persistor={persistor}>
        <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
          <Stack>
            <Stack.Screen name="(pages)" options={{ headerShown: false }} />
            <Stack.Screen name="+not-found" />
          </Stack>
          <StatusBar style="auto" />
        </ThemeProvider>
      </PersistGate>
    </StoreProvider>
  );
};
