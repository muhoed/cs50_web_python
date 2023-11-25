import { createDrawerNavigator } from '@react-navigation/drawer';

import Register from '../../pages/Register';
import Login from '../../pages/Login';
import Notifications from '../../pages/Notifications';
import Home from '../../pages/Home';
import Settings from '../../pages/Settings';
import { useSelector } from 'react-redux';
import CustomDrawerContent from './CustomDrawerContent';
import { drawerItemsAccount, drawerItemsMain } from './drawerItems';
import Groceries from '../../pages/Groceries';
import Products from '../../pages/Products';
import Shopping from '../../pages/Shopping';
import Cooking from '../../pages/Cooking';
import Equipment from '../../pages/Equipment';
import Stock from '../../pages/Stock';

const Drawer = createDrawerNavigator();

export default function WGDrawerNavigator() {
    const user = useSelector(state => state.secure.user.auth);

    return (
        <Drawer.Navigator 
            initialRouteName={!user?.authenticated ? 'SignIn' : 'Home'} 
            drawerContent={
                (props) => <CustomDrawerContent 
                                drawerItems={!user?.authenticated ? drawerItemsAccount : drawerItemsMain} 
                                {...props} />
            }
            useLegacyImplementation={false}
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

