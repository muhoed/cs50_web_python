import { createDrawerNavigator } from "@react-navigation/drawer";
import Cooking from '../../pages/Cooking';
import Groceries from '../../pages/Groceries';
import Shopping from '../../pages/Shopping';
import Products from '../../pages/Products';
import Equipment from '../../pages/Equipment';
import Stock from '../../pages/Stock';

const Drawer = createDrawerNavigator();

export default function HomeDrawer({navigation}) {
    return (
        <Drawer.Navigator 
            initialRouteName='Groceries'
            drawerContent={(props) => <NavSideBar {...props} />} 
            useLegacyImplementation={false}>
            <Drawer.Screen 
                name="Groceries" 
                component={Groceries} 
                options={{ 
                    //title: 'Groceries',
                    drawerLabel: 'Groceries',
                    groupName: 'Home',
                    activeTintColor: '#FF6F00', 
                }} />
            {/* <Drawer.Screen 
                name="Products" 
                component={Products} 
                options={{ 
                    //title: 'Products',
                    drawerLabel: 'Home',
                    groupName: 'Groceries',
                    activeTintColor: '#FF6F00',  
                }} />
            <Drawer.Screen 
                name="Equipment" 
                component={Equipment} 
                options={{ 
                    //title: 'Equipment',
                    drawerLabel: 'Home',
                    groupName: 'Groceries',
                    activeTintColor: '#FF6F00', 
                }} />
            <Drawer.Screen 
                name="Stock" 
                component={Stock} 
                options={{ 
                    //title: 'Available stock',
                    drawerLabel: 'Home',
                    groupName: 'Groceries',
                    activeTintColor: '#FF6F00', 
                }} /> */}
            <Drawer.Screen 
                name="Shopping" 
                component={Shopping} 
                options={{ 
                    //title: 'Shopping planning',
                    drawerLabel: 'Shopping',
                    groupName: 'Home',
                    activeTintColor: '#FF6F00', 
                }} />
            <Drawer.Screen 
                name="Cooking" 
                component={Cooking} 
                options={{
                    //title: 'Cooking planning',
                    drawerLabel: 'Cooking',
                    groupName: 'Home',
                    activeTintColor: '#FF6F00', 
                }} />
        </Drawer.Navigator>
    )
}