import { router, Href } from "expo-router";
import { Pressable, StyleSheet, Text, ImageBackground, View, Platform } from "react-native";
import React, { useState } from 'react'; // Restore useState

const MODULE_IMAGES = {
  'Equipment': require('../assets/images/equipment.jpg'),
  'Shopping': require('../assets/images/shopping_plan.jpg'),
  'Cooking': require('../assets/images/cooking_plan.jpg'),
  'Groceries': require('../assets/images/groceries.jpg'),
};

interface ModuleTileProps {
    module: ModuleType;
    tileWidth?: number; // Add optional tileWidth prop
}

export default function ModuleTile({ module, tileWidth }: ModuleTileProps) { // Destructure tileWidth
    const [isHovered, setIsHovered] = useState(false); // Restore state

    const handlePress = () => router.push(`/(pages)/${module.name}` as Href);

    // Restore hoverProps
    const hoverProps = Platform.OS === 'web' ? {
        onHoverIn: () => setIsHovered(true),
        onHoverOut: () => setIsHovered(false),
    } : {};

    return (
        <Pressable 
            style={[styles.container, tileWidth ? { width: tileWidth, height: tileWidth } : styles.nativeContainer]} // Apply calculated size or default native size
            onPress={handlePress}
            {...hoverProps} // Restore hover props
        >
            <ImageBackground 
                source={MODULE_IMAGES[module.name as keyof typeof MODULE_IMAGES] || MODULE_IMAGES['Groceries']} // Restore dynamic source
                style={styles.imageBackground} 
                resizeMode="cover"
            >
                {/* Overlay only on hover, rendered first */}
                {isHovered && (
                    <View style={styles.overlay} />
                )}
                {/* Text background and name always visible, rendered last (on top) */}
                <View style={styles.textBackground}>
                    <Text style={styles.moduleName}>{module.name}</Text>
                </View>
            </ImageBackground>
        </Pressable>
    );
}

const styles = StyleSheet.create({
    container: {
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 12,
        overflow: 'hidden',
        elevation: 4, 
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.25,
        shadowRadius: 3.84,
        borderWidth: 3, // Add border width
        borderColor: '#1E90FF', // Add border color (lighter blue from top bar)
    },
    nativeContainer: {
        width: '45%', // Example native sizing (adjust as needed)
        aspectRatio: 1, 
    },
    imageBackground: {
        flex: 1, 
        width: '100%', 
        height: '100%', 
        justifyContent: 'flex-end', // Push text container to bottom
        alignItems: 'center', // Keep items centered horizontally
    },
    overlay: {
        ...StyleSheet.absoluteFillObject, 
        backgroundColor: 'rgba(0, 0, 0, 0.6)', 
    },
    // New style for the text background view
    textBackground: {
        width: '100%', // Span full width
        backgroundColor: 'rgba(0, 0, 0, 0.5)', // Semi-transparent background
        paddingVertical: 8, // Add vertical padding
        paddingHorizontal: 12, // Add horizontal padding
    },
    moduleName: {
        fontSize: 20, // Slightly smaller font size might look better
        fontWeight: 'bold',
        color: '#ffffff',
        textAlign: 'center',
    },
});