import 'react-native-gesture-handler';
import '@expo/match-media';
import { Provider as PaperProvider } from 'react-native-paper';

import WGDrawerNavigator from '../../components/navbar/WGDrawerNavigator';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { NavigationContainer } from '@react-navigation/native';
import { Platform } from 'react-native';
import Home from './Home';
import Notifications from './Notifications';
import Settings from './Settings';
import CustomNavigationBar from '../../components/navbar/CustomNavigationBar';
import Groceries from './Groceries';
import Shopping from './Shopping';
import Cooking from './Cooking';
import Products from './Products';
import Equipment from './Equipment';
import Stock from './Stock';

const Stack = createNativeStackNavigator();

export default function PageLayout() {

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
    prefixes: []
  };

  return (
    <PaperProvider>
      <NavigationContainer linking={linking}>
        {
          Platform.OS === 'web' ?
          <Stack.Navigator 
            initialRouteName="Home"
            screenOptions={{
              header: (props: any) => <CustomNavigationBar {...props} />
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
  );
}