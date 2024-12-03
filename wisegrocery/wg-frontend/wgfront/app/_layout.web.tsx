import 'react-native-gesture-handler';
import { Provider as StoreProvider } from "react-redux";
import { PersistGate } from 'redux-persist/integration/react';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import { useColorScheme } from '@/hooks/useColorScheme.web';
import { Stack } from 'expo-router';
import { useEffect } from 'react';
import 'react-native-reanimated';
import { Persistor } from 'redux-persist/lib/types';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { Provider as PaperProvider } from 'react-native-paper';

//import { persistor, persistantStore } from '../store/redux/store';
import { persistor, store } from '../store/redux/store';
//import { store } from '../store/redux/store';
import Spinner from '../components/Spinner';
import setupInterceptors from '../services/setupInterceptors';
import CustomNavigationBar from '../components/navbar/CustomNavigationBar.web';

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  setupInterceptors(store);

  const colorScheme = useColorScheme();
  const [loaded] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
  });

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
      <PersistGate loading={<Spinner />} persistor={persistor as Persistor}>
        <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
          <PaperProvider>
            <Stack screenOptions={{
                header: (props: any) => <CustomNavigationBar {...props} />
              }}>
              <Stack.Screen name="(pages)" options={{ headerShown: false }} />
              <Stack.Screen name="+not-found" />
            </Stack>
          </PaperProvider>
          <StatusBar style="auto" />
        </ThemeProvider>
      </PersistGate>
    </StoreProvider>
  );
};
