import React, {useState} from 'react';
import { Link } from "@react-navigation/native";
import { StyleSheet, View, Text, TouchableOpacity, SafeAreaView } from "react-native";
import { Appbar, Divider, List, Menu } from "react-native-paper";
import { useDispatch, useSelector } from "react-redux";
import { settingsReset } from '../../store/redux/settingsSlice';
import { logoutUser } from '../../store/redux/userSlice';
import { Pressable } from 'react-native-web';
import useScreenSize from '../../hooks/useScreenSize';

export default function NavbarMenu (props) {
    const dispatch = useDispatch();
    const user = useSelector(state => state.secure.user.auth);
    const [homeVisible, setHomeVisible] = useState(false);
    const screenSize = useScreenSize();

    const mainMenuItems = (
        <>
        <Menu.Item
            leadingIcon="home-outline"
            title="Home"
            titleStyle={{fontSize: 16, fontWeight: "bold"}}
            onPress={() => onMenuItemPress("Home")} />
        <Divider bold={true} />
        <Menu.Item 
            title="Groceries" 
            titleStyle={{fontWeight: "bold"}}
            onPress={() => onMenuItemPress("Groceries")} />
        <Divider />
        <Menu.Item
            leadingIcon="chevron-right" 
            title="Products" 
            onPress={() => onMenuItemPress("Products")} />
        <Menu.Item
            leadingIcon="chevron-right"  
            title="Equipment" 
            onPress={() => onMenuItemPress("Equipment")} />
        <Menu.Item 
            leadingIcon="chevron-right" 
            title="Stock" 
            onPress={() => onMenuItemPress("Stock")} />
        <Divider />
        <Menu.Item 
            title="Shopping" 
            onPress={() => onMenuItemPress("Shopping")} />
        <Divider />
        <Menu.Item 
            title="Cooking" 
            onPress={() => onMenuItemPress("Cooking")} />
        </>
    )
  
    const openHomeMenu = () => setHomeVisible(true);
  
    const closeHomeMenu = () => setHomeVisible(false);

    const onLogout = () => {
        setStatus('loading');
        try {
            dispatch(logoutUser());
            dispatch(settingsReset());
            setStatus('success');
        } catch (error) {
            console.log("Logout error: " + error);
            setStatus("error");
        }
    };

    function renderLogoutBtn() {
        if (user.authenticated) {
            return (
                <View style={{marginLeft: "3%", marginRight: "3%"}}>
                    <TouchableOpacity onPress={onLogout} testID="customDrawer-logout">
                        <View style={styles.parentItem}>
                            <Text style={{fontSize: 16, fontWeight: "bold"}}>{'Sign Out'}</Text>
                        </View>
                    </TouchableOpacity>
                </View>
            );
        }
        return null;
    }

    function onMenuPress() {
        openHomeMenu();
    }

    function onMenuItemPress(screen) {
        props.navigation.navigate(screen);
        closeHomeMenu();
    }

    if (screenSize.isDesktop || !screenSize.isPortrait) {
        return (
            <View style={styles.container}>
                <View style={{ flex: 1, flexGrow: 1, justifyContent: "start" }}>
                    <Link to={{ screen: "Home" }} style={styles.navbarItem}>Wise Grocery</Link>
                </View>
                {!user.authenticated ? (
                    <>
                    <Link style={styles.navbarItem} to={{ screen: 'SignIn' }}>Log In</Link>
                    <Link style={styles.navbarItem} to={{ screen: 'SignUn' }}>Register</Link>
                    </>
                ) : (
                    <>
                    <View style={{marginLeft: "3%", marginRight: "3%"}}>
                        <Menu
                            visible={homeVisible}
                            onDismiss={closeHomeMenu}
                            anchor={
                                <Pressable onPress={() => onMenuPress()}>
                                    <Text style={{fontSize: 16, fontWeight: "bold"}}>Menu</Text>
                                </Pressable>
                            }
                            anchorPosition="bottom">
                            {mainMenuItems}
                        </Menu>
                    </View>
                    <Link style={styles.navbarItem} to={{ screen: 'Notifications' }}>
                        Notifications
                    </Link>
                    <Link style={styles.navbarItem} to={{ screen: 'Settings' }}>
                        Settings
                    </Link>
                    {renderLogoutBtn()}
                    </>
                )}
            </View>
        );
    }

    return (
        <Menu 
            visible={homeVisible}
            onDismiss={closeHomeMenu}
            anchor={
                <Appbar.Action icon="menu" onPress={openHomeMenu} />
            }>
            {!user.authenticated ? (
                <>
                <Menu.Item style={styles.navbarItem} onPress={() => onMenuItemPress('SignIn')} title="Log In" />
                <Menu.Item style={styles.navbarItem} onPress={() => onMenuItemPress('SignUn')} title="Register" />
                </>
            ) : (
                <>
                {mainMenuItems}
                <Divider bold={true} />
                <Menu.Item style={styles.navbarItem} onPress={() => onMenuItemPress('Notifications')} title="Notifications" />
                <Menu.Item style={styles.navbarItem} onPress={() => onMenuItemPress('Settings')} title="Settings" />
                <Divider bold={true} />
                <Menu.Item style={styles.navbarItem} onPress={() => onLogout()} title="Log Out" />
                </>
            )}
        </Menu>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        flexDirection: "row",
    },
    navbarItem: {
        fontSize: 16,
        fontWeight: "bold",
        marginLeft: "3%",
        marginRight: "3%",
    }
});