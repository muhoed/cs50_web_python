import { createDrawerNavigator } from '@react-navigation/drawer';
import { NavigationContainer } from '@react-navigation/native';

import Register from '../../app/(pages)/Register';
import Login from '../../app/(pages)/Login';
import Notifications from '../../app/(pages)/Notifications';
import Home from '../../app/(pages)/Home';
import Settings from '../../app/(pages)/Settings';
import { useSelector } from 'react-redux';
import NavSideBar from '../NavSideBar';
import HomeDrawer from './HomeDrawer';

const Drawer = createDrawerNavigator();

export default function WGDrawerNavigator() {
    const user = useSelector(state => state.secure.user.auth);

    const config = {
        screens: {
            SignIn: 'login',
            SignUp: 'register',
            Home: 'home',
            Notifications: 'notifications',
            Settings: 'settings',
        },
    };

    const linking = {
        config,
    };

    return (
        <NavigationContainer linking={linking}>
            <Drawer.Navigator 
                initialRouteName={!user?.authenticated ? 'SignIn' : 'Home'} 
                drawerContent={(props) => <NavSideBar {...props} />}
                useLegacyImplementation={false}
                >
                {!user.authenticated ? (
                    <>
                    <Drawer.Screen 
                        name="SignIn" 
                        component={Login} 
                        options={{ 
                            //title: 'Sign In',
                            drawerLabel: 'Sign In',
                            groupName: 'Account',
                            activeTintColor: '#FF6F00', 
                        }} /> 
                    <Drawer.Screen 
                        name="SignUp" 
                        component={Register} 
                        options={{ 
                            //title: 'Sign Up',
                            drawerLabel: 'Sign Up',
                            groupName: 'Account',
                            activeTintColor: '#FF6F00',
                        }} />
                    </>
                ) : (
                    <>
                    <Drawer.Screen 
                        name="Home" 
                        component={Home} 
                        options={{ 
                            //title: 'Home',
                            drawerLabel: 'Home',
                            groupName: 'Main Menu',
                            activeTintColor: '#FF6F00', 
                        }} />
                    <Drawer.Screen 
                        name="Notifications" 
                        component={Notifications} 
                        options={{ 
                            //title: 'Notifications',
                            drawerLabel: 'Notifications',
                            groupName: 'Main Menu',
                            activeTintColor: '#FF6F00', 
                        }} />
                    <Drawer.Screen 
                        name="Settings" 
                        component={Settings} 
                        options={{ 
                            //title: 'Settings',
                            drawerLabel: 'Settings',
                            groupName: 'Main Menu',
                            activeTintColor: '#FF6F00',  
                        }} />
                    </>
                )}
            </Drawer.Navigator>
        </NavigationContainer>
    );
}

