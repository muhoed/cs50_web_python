import { SafeAreaView, StyleSheet, Text } from "react-native";

export default function Notifications () {
    return (
        <SafeAreaView style={styles.container}>
            <Text>Notification screen.</Text>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
});