import React, {useState} from 'react';
import { StyleSheet, View, Text, TouchableOpacity } from "react-native";
import { Appbar, Divider, List, Menu } from "react-native-paper";
import { settingsReset } from '../../store/redux/settingsSlice';
import { logoutUser } from '../../store/redux/userSlice';
import { Pressable } from 'react-native-web';
import useScreenSize from '../../hooks/useScreenSize';
import { Link, router } from 'expo-router';
import { useWGDispatch } from '@/hooks/useWGDispatch';
import { useWGSelector } from '@/hooks/useWGSelector';

export default function NavbarMenu (props: { navigation: { navigate: (arg0: any) => void; }; }) {
    const dispatch = useWGDispatch();
    const user = useWGSelector(state => state.secure.user.auth);
    const [homeVisible, setHomeVisible] = useState(false);
    const [status, setStatus] = useState('idle');
    const screenSize = useScreenSize();

    const mainMenuItems = (
        <>
        <Menu.Item
            leadingIcon="home-outline"
            title="Home"
            titleStyle={{fontSize: 16, fontWeight: "bold"}}
            onPress={() => onMenuItemPress("/(pages)")} />
        <Divider bold={true} />
        <Menu.Item 
            title="Groceries" 
            titleStyle={{fontWeight: "bold"}}
            onPress={() => onMenuItemPress("/(pages)/Groceries")} />
        <Divider />
        <Menu.Item
            leadingIcon="chevron-right" 
            title="Products" 
            onPress={() => onMenuItemPress("/(pages)/Products")} />
        <Menu.Item
            leadingIcon="chevron-right"  
            title="Equipment" 
            onPress={() => onMenuItemPress("/(pages)/Equipment")} />
        <Menu.Item 
            leadingIcon="chevron-right" 
            title="Stock" 
            onPress={() => onMenuItemPress("/(pages)/Stock")} />
        <Divider />
        <Menu.Item 
            title="Shopping" 
            onPress={() => onMenuItemPress("/(pages)/Shopping")} />
        <Divider />
        <Menu.Item 
            title="Cooking" 
            onPress={() => onMenuItemPress("/(pages)/Cooking")} />
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

    function onMenuItemPress(routeName: any) {
        router.push(routeName);
        closeHomeMenu();
    }

    if (screenSize.isDesktop || !screenSize.isPortrait) {
        return (
            <View style={styles.container}>
                <Link href='/' style={styles.navbarItem}>Wise Grocery</Link>
                <View style={{ flex: 1, flexGrow: 1, justifyContent: "flex-start" }}>
                    {/* <Link href='/(pages)' style={styles.navbarItem}>Wise Grocery</Link> */}
                </View>
                {!user.authenticated ? (
                    <>
                    <Link style={styles.navbarItem} href='/(pages)/Login'>Log In</Link>
                    <Link style={styles.navbarItem} href='/(pages)/Register'>Register</Link>
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
                    <Link style={styles.navbarItem} href='/(pages)/Notifications'>
                        Notifications
                    </Link>
                    <Link style={styles.navbarItem} href='/(pages)/Settings'>
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
                <Menu.Item style={styles.navbarItem} onPress={() => onMenuItemPress('/(pages)/Login')} title="Log In" />
                <Menu.Item style={styles.navbarItem} onPress={() => onMenuItemPress('/(pages)/Register')} title="Register" />
                </>
            ) : (
                <>
                {mainMenuItems}
                <Divider bold={true} />
                <Menu.Item style={styles.navbarItem} onPress={() => onMenuItemPress('/(pages)/Notifications')} title="Notifications" />
                <Menu.Item style={styles.navbarItem} onPress={() => onMenuItemPress('/(pages)/Settings')} title="Settings" />
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
    parentItem: {
      flexDirection: 'row',
      alignItems: 'center',
      borderBottomWidth: 1,
      borderBottomColor: '#F0F0F0',
      paddingTop: 4,
      paddingBottom: 4,
    },
    navbarItem: {
        fontSize: 16,
        fontWeight: "bold",
        marginLeft: "3%",
        marginRight: "3%",
        color: 'whitesmoke'
    }
});