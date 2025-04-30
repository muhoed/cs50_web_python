import React, { useState } from 'react';
import { StyleSheet, View, Text, TouchableOpacity, Platform } from "react-native";
import { Appbar, Divider, Menu, Searchbar, useTheme } from "react-native-paper";
import { settingsReset } from '../../store/redux/settingsSlice';
import { logoutUser } from '../../store/redux/userSlice';
import { Pressable } from 'react-native-web';
import useScreenSize from '../../hooks/useScreenSize';
import { Link, router, Href } from 'expo-router';
import { useWGDispatch } from '@/hooks/useWGDispatch';
import { useWGSelector } from '@/hooks/useWGSelector';

export default function NavbarMenu() {
    const dispatch = useWGDispatch();
    const user = useWGSelector(state => state.secure.user.auth);
    const [homeVisible, setHomeVisible] = useState(false);
    const [status, setStatus] = useState('idle');
    const [searchQuery, setSearchQuery] = useState('');
    const [isSearchFocused, setIsSearchFocused] = useState(false);
    const screenSize = useScreenSize();
    const theme = useTheme();

    const mainMenuItems = (
        <>
            <Menu.Item
                leadingIcon="home-outline"
                title="Home"
                /*titleStyle={styles.menuTitle}*/
                onPress={() => onMenuItemPress("/(pages)")} />
            <Divider bold={true} />
            <Menu.Item 
                title="Groceries" 
                /*titleStyle={styles.menuTitle}*/
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
            <View style={styles.navLinks}>
                {/* Search bar now here */}
                {user.authenticated && (
                    <View style={styles.searchContainer}> {/* Re-use container for potential sizing */} 
                        <Searchbar
                            placeholder="Search..."
                            onChangeText={setSearchQuery}
                            value={searchQuery}
                            style={[styles.searchBar, isSearchFocused && styles.searchBarFocused]}
                            iconColor='#ffffff'
                            placeholderTextColor='#ffffff'
                            inputStyle={styles.searchInput}
                            onFocus={() => setIsSearchFocused(true)}
                            onBlur={() => setIsSearchFocused(false)}
                        />
                    </View>
                )}
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

    const onMenuItemPress = (routeName: Href) => {
        router.push(routeName);
        setHomeVisible(false);
    };

    return Platform.OS === 'web' ? renderWebNav() : renderMobileNav();
}

const styles = StyleSheet.create({
    webNav: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 16,
        paddingVertical: 8,
        width: '100%',
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
        maxWidth: 300,
    },
    searchBar: {
        backgroundColor: 'transparent',
        borderRadius: 8,
        elevation: 0,
        height: 40,
        borderColor: '#ffffff',
        borderWidth: 1,
        alignItems: 'center',
    },
    searchBarFocused: {
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
    },
    searchInput: {
        color: '#ffffff',
        fontSize: 14,
        textAlignVertical: 'center',
        lineHeight: 40,
        height: 40,
        minHeight: 40,
    },
    navLinks: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'flex-end',
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