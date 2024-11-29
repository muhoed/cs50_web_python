// import { createDrawerNavigator } from '@react-navigation/drawer';
import { Drawer } from 'expo-router/drawer';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

import Register from '../../app/(pages)/Register';
import Login from '../../app/(pages)/Login';
import Notifications from '../../app/(pages)/Notifications';
import Home from '../../app/(pages)';
import Settings from '../../app/(pages)/Settings';
import { useSelector } from 'react-redux';
import Groceries from '../../app/(pages)/Groceries';
import Products from '../../app/(pages)/Products';
import Shopping from '../../app/(pages)/Shopping';
import Cooking from '../../app/(pages)/Cooking';
import Equipment from '../../app/(pages)/Equipment';
import Stock from '../../app/(pages)/Stock';
import { RootStateType } from '@/store/redux/store';
import CustomDrawerContent from '@/components/navbar/CustomDrawerContent';
import { drawerItemsAccount, drawerItemsMain } from '@/components/navbar/drawerItems';

// const Drawer = createDrawerNavigator();

type AuthType = {
    accessToken: string | null, 
    refreshToken: string | null, 
    authenticated: boolean
};

export default function WGDrawerNavigator() {
    const user = useSelector<RootStateType, AuthType>(state => state.secure.user.auth);

    return (
        <GestureHandlerRootView style={{ flex: 1 }}>
            {/* <Drawer.Navigator */}
            <Drawer 
                initialRouteName={!user?.authenticated ? 'Login' : 'index'} 
                drawerContent={
                    (props: any) => <CustomDrawerContent 
                                        drawerItems={!user?.authenticated ? drawerItemsAccount : drawerItemsMain} 
                                        {...props} />
                }
                // useLegacyImplementation={false}
                >
                {!user.authenticated ? (
                    <>
                    {/* <Drawer.Screen name="SignIn" component={Login} /> 
                    <Drawer.Screen name="SignUp" component={Register} /> */}
                    <Drawer.Screen name="Login" /> 
                    <Drawer.Screen name="Register" />
                    </>
                ) : (
                    <>
                    {/* <Drawer.Screen name="Home" component={Home} />
                    <Drawer.Screen name="Groceries" component={Groceries} />
                    <Drawer.Screen name="Products" component={Products} />
                    <Drawer.Screen name="Shopping" component={Shopping} />
                    <Drawer.Screen name="Cooking" component={Cooking} />
                    <Drawer.Screen name="Equipment" component={Equipment} />
                    <Drawer.Screen name="Stock" component={Stock} />
                    <Drawer.Screen name="Notifications" component={Notifications} />
                    <Drawer.Screen  name="Settings" component={Settings} /> */}
                    <Drawer.Screen name="index" />
                    <Drawer.Screen name="Groceries" />
                    <Drawer.Screen name="Products" />
                    <Drawer.Screen name="Shopping" />
                    <Drawer.Screen name="Cooking" />
                    <Drawer.Screen name="Equipment" />
                    <Drawer.Screen name="Stock" />
                    <Drawer.Screen name="Notifications" />
                    <Drawer.Screen  name="Settings" />
                    </>
                )}
            {/* </Drawer.Navigator> */}
            </Drawer>
        </GestureHandlerRootView>
    );
};

