import 'react-native-gesture-handler';
import '@expo/match-media';
import { Provider as PaperProvider } from 'react-native-paper';
import { Provider as StoreProvider } from "react-redux";
import { PersistGate } from 'redux-persist/integration/react';

import { persistor, store } from './store/redux/store';
import WGDrawerNavigator from './components/navbar/WGDrawerNavigator';
import Spinner from './components/Spinner';
import setupInterceptors from './services/setupInterceptors';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { NavigationContainer } from '@react-navigation/native';
import { Platform } from 'react-native-web';
import Home from './pages/Home';
import Notifications from './pages/Notifications';
import Settings from './pages/Settings';
import CustomNavigationBar from './components/navbar/CustomNavigationBar';
import Groceries from './pages/Groceries';
import Shopping from './pages/Shopping';
import Cooking from './pages/Cooking';
import Products from './pages/Products';
import Equipment from './pages/Equipment';
import Stock from './pages/Stock';

const Stack = createNativeStackNavigator();

export default function App() {

  setupInterceptors(store);

  const config = {
    screens: {
      Home: 'home',
      Groceries: 'groceries',
      Products: 'products',
      Equipment: 'equipment',
      Stock: 'stock',
      Shopping: 'shopping',
      Cooking: 'cooking',
      Notifications: 'notifications',
      Settings: 'settings'
    },
  };

  const linking = {
    config,
  };

  return (
    <StoreProvider store={store}>
      <PersistGate loading={<Spinner />} persistor={persistor}>
          <PaperProvider>
            <NavigationContainer linking={linking}>
              {
                Platform.OS === 'web' ?
                <Stack.Navigator 
                  initialRouteName="Home"
                  screenOptions={{
                    header: (props) => <CustomNavigationBar {...props} />
                  }}>
                  <Stack.Screen name="Home" component={Home} />
                  <Stack.Screen name="Groceries" component={Groceries} />
                  <Stack.Screen name="Products" component={Products} />
                  <Stack.Screen name="Equipment" component={Equipment} />
                  <Stack.Screen name="Stock" component={Stock} />
                  <Stack.Screen name="Shopping" component={Shopping} />
                  <Stack.Screen name="Cooking" component={Cooking} />
                  <Stack.Screen name="Notifications" component={Notifications} />
                  <Stack.Screen name="Settings" component={Settings} />
                </Stack.Navigator> :
                <Stack.Navigator screenOptions={{ headerShown: false }}>
                  <Stack.Screen name="MainDrawer" component={WGDrawerNavigator} />
                </Stack.Navigator>
              }
            </NavigationContainer>
          </PaperProvider>
      </PersistGate>
    </StoreProvider>
  );
}