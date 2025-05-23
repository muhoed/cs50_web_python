import { FlatList, Platform, SafeAreaView, StyleSheet } from "react-native";

import ModuleTile from "../../components/ModuleTile";
import { MODULES } from "../../enumerations/modules";

export default function Groceries() {
    const groceryModules = MODULES.filter(module => module.parent === "Groceries");

    return (
        <SafeAreaView style={styles.container}>
            <FlatList
                contentContainerStyle={styles.innerContainer}
                horizontal={Platform.OS === 'web' ? true : false}
                data={groceryModules}
                renderItem={({item, index}) => {
                    return (
                    <ModuleTile key={index} module={item} />
                    );
                }}
            />
            {/* <StatusBar style="auto" /> */}
        </SafeAreaView>
    );
};

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