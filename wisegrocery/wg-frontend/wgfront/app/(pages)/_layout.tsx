import 'react-native-gesture-handler';
import { Provider as PaperProvider } from 'react-native-paper';
import { Stack } from 'expo-router';

import { useWGSelector } from '@/hooks/useWGSelector';

export default function PageLayout() {
  const user = useWGSelector(state => state.secure.user.auth);

  return (
    <PaperProvider>
      <Stack
        screenOptions={{ headerShown: false }}>
        <Stack.Screen name="WGDrawerNavigator" />
      </Stack>
    </PaperProvider>
  );
};