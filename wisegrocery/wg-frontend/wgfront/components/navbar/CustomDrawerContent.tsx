import React, {useState} from 'react';
import { SafeAreaView, StyleSheet, ScrollView, View, Text, TouchableOpacity } from 'react-native';
import { settingsReset } from '../../store/redux/settingsSlice';
import { logoutUser } from '../../store/redux/userSlice';
import { useWGDispatch } from '@/hooks/useWGDispatch';
import { useWGSelector } from '@/hooks/useWGSelector';
import { drawerItemsAccount, drawerItemsMain } from '@/components/navbar/drawerItems';

var previousFilteredItems: any[] = [];
var returnName = 'Main menu';

export default function CustomDrawerContent(props: any) {
    const dispatch = useWGDispatch();
    const user = useWGSelector(state => state.secure.user.auth);
    const [mainDrawer, setMainDrawer] = useState(true);
    const [filteredItems, setFilteredItems] = useState<any>([]);
    const [status, setStatus] = useState('idle');

    const drawerItems = user.authenticated ? drawerItemsMain : drawerItemsAccount;
  
    const toggleMainDrawer = () => {
        setMainDrawer(true);
        setFilteredItems([]);
    };
  
    const onItemParentPress = (key: any) => {
        returnName = 'Main manu';
        const filteredMainDrawerRoutes = drawerItems.find((e: { key: any; }) => {
            return e.key === key;
        });
        if (filteredMainDrawerRoutes?.routes.length === 1) {
            const selectedRoute = filteredMainDrawerRoutes.routes[0];
            props.navigation.toggleDrawer();
            props.navigation.navigate(selectedRoute.routeName, {
                screen: selectedRoute.routeName,
            });
        } else {
            props.navigation.navigate(filteredMainDrawerRoutes?.routes[0].routeName, {
                screen: key,
            });
            setMainDrawer(false);
            previousFilteredItems = JSON.parse(JSON.stringify(filteredItems));
            setFilteredItems(filteredMainDrawerRoutes);
        }
    };

    const onItemChildPress = (route: any) => {
        returnName = route.parent;
        if (route.routes.length < 1) {
            props.navigation.navigate(route.routeName, {
                screen: route.routeName,
                });
        } else {
            props.navigation.navigate(route.routeName, {
                screen: route.routeName,
            });
            previousFilteredItems = JSON.parse(JSON.stringify(filteredItems));
            setFilteredItems(route);
        }
    };

    const onLogout = () => {
        setStatus('loading');
        try {
            dispatch(logoutUser());
            dispatch(settingsReset());
            setStatus('success');
        } catch (error) {
            console.log("Logout error: " + error);
            setStatus("error");
        } finally {
            props.navigation.closeDrawer();
        }
    };

    function renderMainDrawer() {
        return (
            <View>
                {drawerItems.map((parent: any) => (
                    <View key={parent.key}>
                        <TouchableOpacity
                            key={parent.key}
                            testID={parent.key}
                            onPress={() => {
                            onItemParentPress(parent.key);
                            }}>
                            <View style={styles.parentItem}>
                                <Text style={styles.title}>{parent.title}</Text>
                            </View>
                        </TouchableOpacity>
                    </View>
                ))}
                {renderLogoutBtn()}
            </View>
        );
    }

    function renderFilteredItemsDrawer() {
        return (
        <View>
            <TouchableOpacity
                onPress={() => {
                    if (drawerItems.findIndex((e) => {
                        return e.key === filteredItems.routes[0].parent;
                    }) < 0) {
                        returnName = filteredItems.routes[0].parent;
                        props.navigation.navigate(filteredItems.routes[0].routeName, {
                            screen: filteredItems.routes[0].parent,
                        });
                        setFilteredItems(previousFilteredItems);
                    } else {
                        returnName = 'Main manu';
                        props.navigation.navigate(filteredItems.routes[0].routeName, {
                            screen: filteredItems.routes[0].parent,
                        });
                        previousFilteredItems = [];
                        toggleMainDrawer();
                    } 
                }}
                style={styles.backButtonRow}>
                <Text style={[styles.backButtonText, styles.title]}>{'Back to ' + returnName}</Text>
            </TouchableOpacity>
            {filteredItems.routes.map((route: any) => {
                return (
                    <TouchableOpacity
                        key={route.routeName}
                        testID={route.routeName}
                        onPress={() => {
                                onItemChildPress(route);
                            }
                        }
                        style={styles.parentItem}>
                        <Text style={styles.title}>{route.title}</Text>
                    </TouchableOpacity>
                );
            })}
        </View>
        );
    }

    function renderLogoutBtn() {
        if (user.authenticated) {
            return (
                <View>
                    <TouchableOpacity onPress={onLogout} testID="customDrawer-logout">
                    <View style={styles.parentItem}>
                        <Text style={styles.title}>{'Sign Out'}</Text>
                    </View>
                    </TouchableOpacity>
                </View>
            );
        }
        return null;
    }

    return (
        <ScrollView style={styles.drawerContainer}>
        <SafeAreaView
            style={styles.container}
            // forceInset={{top: 'always', horizontal: 'never'}}
            >
            <View style={styles.centered}>
            <Text style={styles.headerText}>
                {'Wise Grocery'}
            </Text>
            </View>
            {mainDrawer ? renderMainDrawer() : renderFilteredItemsDrawer()}
        </SafeAreaView>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
  headerContainer: {
    height: 100,
    flexDirection: 'row',
    paddingVertical: 28,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerText: {
    fontWeight: "bold",
  },
  drawerContainer: {
    backgroundColor: '#222222',
  },
  container: {
    flex: 1,
    zIndex: 1000,
  },
  centered: {
    alignItems: 'center',
  },
  parentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
    paddingTop: 4,
    paddingBottom: 4,
  },
  title: {
    margin: 16,
    fontWeight: 'bold',
    color: '#F0F0F0',
    textAlign: 'center',
  },
  backButtonRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingBottom: 17,
    paddingLeft: 3,
    borderBottomColor: '#F0F0F0',
    borderBottomWidth: 1,
  },
  backButtonText: {
    marginLeft: 10,
    color: '#F0F0F0',
  },
});