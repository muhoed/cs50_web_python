import { DrawerContentScrollView, DrawerItem } from "@react-navigation/drawer";
import { SafeAreaView } from "react-native-web";
import { StyleSheet, Text, View } from "react-native";
import LogoutDrawerLink from "./LogoutDrawerLink";

export default function NavSideBar (props: any) {
    const {state, descriptors, navigation} = props;
    let lastGroupName = '';
    let newGroup = true;

    return (
        <SafeAreaView style={ {flex: 1} }>
            <DrawerContentScrollView {...props}>
                {state.routes.map((route: any) => {
                    const { drawerLabel, activeTintColor, groupName } = descriptors[route.key].options;
                    if (lastGroupName !== groupName) {
                        newGroup = true;
                        lastGroupName = groupName;
                    } else {
                        newGroup = false;
                    }
                    return (
                        <>
                        {newGroup ? (
                            <View style={styles.sectionView}>
                                <Text key={groupName} style={{ marginLeft: 10 }}>
                                    {groupName}
                                </Text>
                                <View style={styles.separatorLine} />
                            </View>
                        ) : null}
                        <DrawerItem
                            key={route.name + '-' + route.key}
                            label={
                            ({ color }) =>
                                <Text style={{ color }}>
                                    {drawerLabel}
                                </Text>
                            }
                            focused={
                                state.routes.findIndex(
                                    (e: any) => e.name === route.name
                                ) === state.index
                            }
                            activeTintColor={activeTintColor}
                            onPress={() => navigation.navigate(route.name)}
                        />
                        </>
                    );
                })}
                <LogoutDrawerLink {...props} />
            </DrawerContentScrollView>
        </SafeAreaView>
    )
};
 
const styles = StyleSheet.create({
    sectionView: {
      flex: 1,
      flexDirection: 'row',
      alignItems: 'center',
      marginTop: 5,
    },
    separatorLine: {
      flex: 1,
      backgroundColor: 'black',
      height: 1.2,
      marginLeft: 12,
      marginRight: 24,
    },
  });