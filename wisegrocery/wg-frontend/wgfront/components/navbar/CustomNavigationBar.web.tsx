import { Appbar } from 'react-native-paper';
import NavbarMenu from './NavbarMenu';
import { StyleSheet } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';

export default function CustomNavigationBar() {
    return (
        <LinearGradient
            colors={['#000080', '#1E90FF']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.gradientContainer}
        >
            <Appbar.Header style={styles.header}>
                <NavbarMenu />
            </Appbar.Header>
        </LinearGradient>
    );
}

const styles = StyleSheet.create({
    gradientContainer: {
        // Ensure it doesn't add extra height if Appbar.Header has fixed height
    },
    header: {
        backgroundColor: 'transparent',
        elevation: 0,
        height: 64,
        width: '100%',
    },
});