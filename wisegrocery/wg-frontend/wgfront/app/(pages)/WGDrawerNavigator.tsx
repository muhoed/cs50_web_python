import { Drawer } from 'expo-router/drawer';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

import CustomDrawerContent from '@/components/navbar/CustomDrawerContent';
import { drawerItemsAccount, drawerItemsMain } from '@/components/navbar/drawerItems';
import { useWGSelector } from '@/hooks/useWGSelector';

export default function WGDrawerNavigator() {
    const user = useWGSelector(state => state.secure.user.auth);

    return (
        <GestureHandlerRootView style={{ flex: 1 }}>
            <Drawer 
                initialRouteName={!user?.authenticated ? 'Login' : 'Home'} 
                drawerContent={
                    (props: any) => <CustomDrawerContent 
                                        drawerItems={!user?.authenticated ? drawerItemsAccount : drawerItemsMain} 
                                        {...props} />
                }
                >
                {!user.authenticated ? (
                    <>
                    <Drawer.Screen name="Login" /> 
                    <Drawer.Screen name="Register" />
                    </>
                ) : (
                    <>
                    <Drawer.Screen name="Home" />
                    <Drawer.Screen name="Groceries" />
                    <Drawer.Screen name="Products" />
                    <Drawer.Screen name="Shopping" />
                    <Drawer.Screen name="Cooking" />
                    <Drawer.Screen name="Equipment" />
                    <Drawer.Screen name="Stock" />
                    <Drawer.Screen name="Notifications" />
                    <Drawer.Screen name="Settings" />
                    </>
                )}
            </Drawer>
        </GestureHandlerRootView>
    );
};

