import 'react-native-gesture-handler';
import { Provider as PaperProvider } from 'react-native-paper';
import { Stack } from 'expo-router';

import CustomNavigationBar from '../../components/navbar/CustomNavigationBar.web';
import { useWGSelector } from '@/hooks/useWGSelector';

export default function PageLayout() {
  const user = useWGSelector(state => state.secure.user.auth);

  return (
    <PaperProvider>
      <Stack 
        initialRouteName={!user?.authenticated ? 'Login' : 'index'}
        screenOptions={{
          header: (props: any) => <CustomNavigationBar {...props} />
        }}>
        {!user.authenticated ? 
        (
          <>
          <Stack.Screen name="Login" />
          <Stack.Screen name="Register" />
          </>
        ) : (
          <>
          <Stack.Screen name="index" />
          <Stack.Screen name="Groceries" />
          <Stack.Screen name="Products" />
          <Stack.Screen name="Equipment" />
          <Stack.Screen name="Stock" />
          <Stack.Screen name="Shopping" />
          <Stack.Screen name="Cooking" />
          <Stack.Screen name="Notifications" />
          <Stack.Screen name="Settings" />
          </>
        )}
      </Stack>
    </PaperProvider>
  );
};