import { useNavigation } from "expo-router";
import { Button, Pressable, StyleSheet, Text, View } from "react-native";

export default function ModuleTile({ module }: { module: ModuleType }) {
    const navigation = useNavigation();

    return (
        <Pressable style={styles.container} onPress={() => navigation.navigate(module.name as never)}>
            <Text style={styles.button}>{module.name}</Text>
            <Text style={styles.label}>{module.text}</Text>
        </Pressable>
    );
}

const styles = StyleSheet.create({
    container: {
        width: '33.33%',
        height: '100%',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
    },
    button: {
        width: '100%',
        height: '100%',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 10,
        /*borderRadius: 100,*/
        backgroundColor: 'blue',
    },
    label: {
        width: 150,
        justifyContent: 'center',
        alignItems: 'center',
        fontWeight: 'bold',
    },
});