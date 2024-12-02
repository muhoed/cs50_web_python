import { Drawer } from 'expo-router/drawer';
import NavSideBar from "../NavSideBar";

export default function HomeDrawer() {
    return (
        <Drawer 
            initialRouteName='/(pages)/Groceries'
            drawerContent={(props: any) => <NavSideBar {...props} />} 
            >
            <Drawer.Screen 
                name="/(pages)/Groceries" 
                options={{ 
                    drawerLabel: 'Groceries',
                }} />
            <Drawer.Screen 
                name="/(pages)/Shopping" 
                options={{ 
                    drawerLabel: 'Shopping',
                }} />
            <Drawer.Screen 
                name="/(pages)/Cooking" 
                options={{
                    drawerLabel: 'Cooking',
                }} />
        </Drawer>
    )
}