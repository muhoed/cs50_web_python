import { router } from "expo-router";
import { Pressable, StyleSheet, Text, Image, View } from "react-native";

const MODULE_IMAGES = {
  'Equipment': require('../assets/images/equipment.jpg'),
  'Shopping': require('../assets/images/shopping_plan.jpg'),
  'Cooking': require('../assets/images/cooking_plan.jpg'),
  'Groceries': require('../assets/images/groceries.jpg'),
};

export default function ModuleTile({ module }: { module: ModuleType }) {
    //const navigation = useNavigation();

    return (
        <Pressable 
            style={styles.container} 
            onPress={() => router.push(`/(pages)/${module.name}`)}
        >
            <Image 
                source={MODULE_IMAGES[module.name as keyof typeof MODULE_IMAGES] || MODULE_IMAGES['Groceries']}
                style={styles.image}
                resizeMode="cover"
            />
            <View style={styles.textContainer}>
                <Text style={styles.button}>{module.name}</Text>
                <Text style={styles.label}>{module.text}</Text>
            </View>
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
        margin: 8,
        borderRadius: 12,
        overflow: 'hidden',
        backgroundColor: '#2a2a2a',
        elevation: 4,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 3.84,
    },
    image: {
        width: '100%',
        height: '60%',
    },
    textContainer: {
        width: '100%',
        padding: 12,
        backgroundColor: '#2a2a2a',
    },
    button: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#ffffff',
        textAlign: 'center',
        marginBottom: 4,
    },
    label: {
        fontSize: 14,
        color: '#cccccc',
        textAlign: 'center',
        lineHeight: 20,
    },
});