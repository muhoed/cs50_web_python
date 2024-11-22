import { createDrawerNavigator } from "@react-navigation/drawer";
import Cooking from '../../app/(pages)/Cooking';
import Groceries from '../../app/(pages)/Groceries';
import Shopping from '../../app/(pages)/Shopping';
import Products from '../../app/(pages)/Products';
import Equipment from '../../app/(pages)/Equipment';
import Stock from '../../app/(pages)/Stock';
import NavSideBar from "../NavSideBar";

const Drawer = createDrawerNavigator();

export default function HomeDrawer() {
    return (
        <Drawer.Navigator 
            initialRouteName='Groceries'
            drawerContent={(props) => <NavSideBar {...props} />} 
            // useLegacyImplementation={false}
            >
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