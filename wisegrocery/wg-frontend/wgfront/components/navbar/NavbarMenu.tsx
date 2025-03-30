import React, { useState } from 'react';
import { StyleSheet, View, Text, TouchableOpacity, Platform } from "react-native";
import { Appbar, Divider, Menu, Searchbar, useTheme } from "react-native-paper";
import { settingsReset } from '../../store/redux/settingsSlice';
import { logoutUser } from '../../store/redux/userSlice';
import { Pressable } from 'react-native-web';
import useScreenSize from '../../hooks/useScreenSize';
import { Link, router } from 'expo-router';
import { useWGDispatch } from '@/hooks/useWGDispatch';
import { useWGSelector } from '@/hooks/useWGSelector';

export default function NavbarMenu() {
    const dispatch = useWGDispatch();
    const user = useWGSelector(state => state.secure.user.auth);
    const [homeVisible, setHomeVisible] = useState(false);
    const [status, setStatus] = useState('idle');
    const [searchQuery, setSearchQuery] = useState('');
    const screenSize = useScreenSize();
    const theme = useTheme();

    const mainMenuItems = (
        <>
            <Menu.Item
                leadingIcon="home-outline"
                title="Home"
                titleStyle={styles.menuTitle}
                onPress={() => onMenuItemPress("/(pages)")} />
            <Divider bold={true} />
            <Menu.Item 
                title="Groceries" 
                titleStyle={styles.menuTitle}
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
    );

    const handleLogout = () => {
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

    const renderWebNav = () => (
        <View style={styles.webNav}>
            <Link href='/' style={styles.logo}>
                <Text style={styles.logoText}>Wise Grocery</Text>
            </Link>
            
            <View style={styles.searchContainer}>
                <Searchbar
                    placeholder="Search..."
                    onChangeText={setSearchQuery}
                    value={searchQuery}
                    style={styles.searchBar}
                    iconColor={theme.colors.primary}
                    placeholderTextColor="#666"
                />
            </View>

            <View style={styles.navLinks}>
                {!user.authenticated ? (
                    <>
                        <Link style={styles.navLink} href='/Login'>
                            <Text style={styles.navLinkText}>Log In</Text>
                        </Link>
                        <Link style={styles.navLink} href='/Register'>
                            <Text style={styles.navLinkText}>Register</Text>
                        </Link>
                    </>
                ) : (
                    <>
                        <View style={styles.menuContainer}>
                            <Menu
                                visible={homeVisible}
                                onDismiss={() => setHomeVisible(false)}
                                anchor={
                                    <Pressable onPress={() => setHomeVisible(true)}>
                                        <Text style={styles.navLinkText}>Menu</Text>
                                    </Pressable>
                                }
                                anchorPosition="bottom">
                                {mainMenuItems}
                            </Menu>
                        </View>
                        <Link style={styles.navLink} href='/(pages)/Notifications'>
                            <Text style={styles.navLinkText}>Notifications</Text>
                        </Link>
                        <Link style={styles.navLink} href='/(pages)/Settings'>
                            <Text style={styles.navLinkText}>Settings</Text>
                        </Link>
                        <TouchableOpacity onPress={handleLogout} style={styles.navLink}>
                            <Text style={styles.navLinkText}>Logout</Text>
                        </TouchableOpacity>
                    </>
                )}
            </View>
        </View>
    );

    const renderMobileNav = () => (
        <Menu 
            visible={homeVisible}
            onDismiss={() => setHomeVisible(false)}
            anchor={
                <Appbar.Action icon="menu" onPress={() => setHomeVisible(true)} />
            }>
            {!user.authenticated ? (
                <>
                    <Menu.Item style={styles.menuItem} onPress={() => onMenuItemPress('/Login')} title="Log In" />
                    <Menu.Item style={styles.menuItem} onPress={() => onMenuItemPress('/Register')} title="Register" />
                </>
            ) : (
                <>
                    {mainMenuItems}
                    <Divider bold={true} />
                    <Menu.Item style={styles.menuItem} onPress={() => onMenuItemPress('/(pages)/Notifications')} title="Notifications" />
                    <Menu.Item style={styles.menuItem} onPress={() => onMenuItemPress('/(pages)/Settings')} title="Settings" />
                    <Divider bold={true} />
                    <Menu.Item style={styles.menuItem} onPress={handleLogout} title="Log Out" />
                </>
            )}
        </Menu>
    );

    const onMenuItemPress = (routeName: string) => {
        router.push(routeName);
        setHomeVisible(false);
    };

    return Platform.OS === 'web' ? renderWebNav() : renderMobileNav();
}

const styles = StyleSheet.create({
    webNav: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 16,
        backgroundColor: '#2a2a2a',
        justifyContent: 'space-between',
    },
    logo: {
        marginRight: 24,
    },
    logoText: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#ffffff',
    },
    searchContainer: {
        flex: 1,
        maxWidth: 400,
        marginHorizontal: 16,
    },
    searchBar: {
        backgroundColor: '#1a1a1a',
        borderRadius: 8,
        elevation: 0,
    },
    navLinks: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 16,
    },
    navLink: {
        padding: 8,
    },
    navLinkText: {
        color: '#ffffff',
        fontSize: 16,
        fontWeight: '500',
    },
    menuContainer: {
        marginLeft: "3%",
        marginRight: "3%",
    },
    menuTitle: {
        fontSize: 16,
        fontWeight: "bold",
        color: '#ffffff',
    },
    menuItem: {
        color: '#ffffff',
    },
});