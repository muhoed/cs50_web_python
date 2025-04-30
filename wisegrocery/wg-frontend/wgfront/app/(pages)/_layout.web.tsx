import 'react-native-gesture-handler';
import { Redirect, Stack } from 'expo-router';

import { useWGSelector } from '@/hooks/useWGSelector';
import CustomNavigationBar from '../../components/navbar/CustomNavigationBar.web';

export default function PageLayout() {
  const user = useWGSelector(state => state.secure.user.auth);

  if (!user.authenticated) {
    return (<Redirect href='/Login' />)
  }

  return (
    <Stack screenOptions={{
        header: (props: any) => <CustomNavigationBar {...props} /> 
      }}>
      <Stack.Screen name="Home" />
      <Stack.Screen name="Groceries" />
      <Stack.Screen name="Products" />
      <Stack.Screen name="Equipment" />
      <Stack.Screen name="Stock" />
      <Stack.Screen name="Shopping" />
      <Stack.Screen name="Cooking" />
      <Stack.Screen name="Notifications" />
      <Stack.Screen name="Settings" />
    </Stack>
  );
};