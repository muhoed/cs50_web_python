import 'react-native-gesture-handler';
import { Provider as StoreProvider } from "react-redux";
import { PersistGate } from 'redux-persist/integration/react';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import { useColorScheme } from '@/hooks/useColorScheme';
// import { Stack } from 'expo-router';
import { useEffect } from 'react';
import 'react-native-reanimated';
import { Persistor } from 'redux-persist/lib/types';

//import { persistor, persistantStore } from '../store/redux/store';
import { persistor, store } from '../store/redux/store';
import Spinner from '../components/Spinner';
import setupInterceptors from '../services/setupInterceptors';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';import { Drawer } from 'expo-router/drawer';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

import CustomDrawerContent from '@/components/navbar/CustomDrawerContent';
// import { drawerItemsAccount, drawerItemsMain } from '@/components/navbar/drawerItems';
// import { useWGSelector } from '@/hooks/useWGSelector';

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  //setupInterceptors(persistantStore);
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
    // <StoreProvider store={persistantStore}>
    <StoreProvider store={store}>
      <PersistGate loading={<Spinner />} persistor={persistor as Persistor}>
        <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
          {/* <Stack>
            <Stack.Screen name="(pages)" options={{ headerShown: false }} />
            <Stack.Screen name="+not-found" />
          </Stack> */}
          <GestureHandlerRootView style={{ flex: 1 }}>
            <Drawer drawerContent={
                (props: any) => <CustomDrawerContent {...props} />} >
                <Drawer.Screen name="(pages)" /> 
                <Drawer.Screen name="+not-found" />
            </Drawer>
          </GestureHandlerRootView>
          <StatusBar style="auto" />
        </ThemeProvider>
      </PersistGate>
    </StoreProvider>
  );
};
