import { FlatList, Platform, SafeAreaView, StyleSheet, StatusBar, Text, View } from "react-native";

import ModuleTile from "../components/ModuleTile";
import { MODULES } from "../enumerations/modules";

export default function Products() {
    let productModules = MODULES.filter(module => module.parent === "Products");

    if (productModules) {
        return (
            <SafeAreaView style={styles.container}>
                <FlatList
                    contentContainerStyle={styles.innerContainer}
                    horizontal={Platform.OS === 'web' ? true : false}
                    data={productModules}
                    renderItem={(item, index) => {
                        return (
                            <ModuleTile key={index} module={item} />
                        );
                    }}
                />
                <StatusBar style="auto" />
            </SafeAreaView>
        );
    } else {
        return (
            <SafeAreaView style={styles.container}>
                <View>
                    <Text>{'Products'}</Text>
                </View>
                <StatusBar style="auto" />
            </SafeAreaView>
        )
    }
    
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    width: '100%',
    height: '100%',
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  innerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
});