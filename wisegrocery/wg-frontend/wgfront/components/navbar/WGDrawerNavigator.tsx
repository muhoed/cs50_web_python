import { createDrawerNavigator } from '@react-navigation/drawer';

import Register from '../../app/(pages)/Register';
import Login from '../../app/(pages)/Login';
import Notifications from '../../app/(pages)/Notifications';
import Home from '../../app/(pages)/Home';
import Settings from '../../app/(pages)/Settings';
import { useSelector } from 'react-redux';
import CustomDrawerContent from './CustomDrawerContent';
import { drawerItemsAccount, drawerItemsMain } from './drawerItems';
import Groceries from '../../app/(pages)/Groceries';
import Products from '../../app/(pages)/Products';
import Shopping from '../../app/(pages)/Shopping';
import Cooking from '../../app/(pages)/Cooking';
import Equipment from '../../app/(pages)/Equipment';
import Stock from '../../app/(pages)/Stock';
import { RootStateType } from '@/store/redux/store';

const Drawer = createDrawerNavigator();

type AuthType = {
    accessToken: string | null, 
    refreshToken: string | null, 
    authenticated: boolean
}

export default function WGDrawerNavigator() {
    const user = useSelector<RootStateType, AuthType>(state => state.secure.user.auth);

    return (
        <Drawer.Navigator 
            initialRouteName={!user?.authenticated ? 'SignIn' : 'Home'} 
            drawerContent={
                (props) => <CustomDrawerContent 
                                drawerItems={!user?.authenticated ? drawerItemsAccount : drawerItemsMain} 
                                {...props} />
            }
            // useLegacyImplementation={false}
            >
            {!user.authenticated ? (
                <>
                <Drawer.Screen name="SignIn" component={Login} /> 
                <Drawer.Screen name="SignUp" component={Register} />
                </>
            ) : (
                <>
                <Drawer.Screen name="Home" component={Home} />
                <Drawer.Screen name="Groceries" component={Groceries} />
                <Drawer.Screen name="Products" component={Products} />
                <Drawer.Screen name="Shopping" component={Shopping} />
                <Drawer.Screen name="Cooking" component={Cooking} />
                <Drawer.Screen name="Equipment" component={Equipment} />
                <Drawer.Screen name="Stock" component={Stock} />
                <Drawer.Screen name="Notifications" component={Notifications} />
                <Drawer.Screen  name="Settings" component={Settings} />
                </>
            )}
        </Drawer.Navigator>
    );
}

