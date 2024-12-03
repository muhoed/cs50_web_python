import 'react-native-gesture-handler';
import { Drawer } from 'expo-router/drawer';
// import { Provider as PaperProvider } from 'react-native-paper';
import { Redirect } from 'expo-router';
import { useWGSelector } from '@/hooks/useWGSelector';

export default function PageLayout() {
  const user = useWGSelector(state => state.secure.user.auth);

  if (!user.authenticated) {
    return (<Redirect href='/Login' />)
  }

  return (
    // <PaperProvider>
    //   <Stack
    //     screenOptions={{ headerShown: false }}>
    //     <Stack.Screen name="WGDrawerNavigator" />
    //   </Stack>
    // </PaperProvider>
    <Drawer>
      <Drawer.Screen name="Home" />
      <Drawer.Screen name="Groceries" />
      <Drawer.Screen name="Products" />
      <Drawer.Screen name="Shopping" />
      <Drawer.Screen name="Cooking" />
      <Drawer.Screen name="Equipment" />
      <Drawer.Screen name="Stock" />
      <Drawer.Screen name="Notifications" />
      <Drawer.Screen name="Settings" />
    </Drawer>
  );
};