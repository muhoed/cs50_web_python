import { Appbar } from 'react-native-paper';
import NavbarMenu from './NavbarMenu';
import { StyleSheet } from 'react-native';

export default function CustomNavigationBar() {
    return (
        <Appbar.Header style={styles.header}>
            <NavbarMenu />
        </Appbar.Header>
    );
}

const styles = StyleSheet.create({
    header: {
        backgroundColor: '#2a2a2a',
        elevation: 0,
        height: 64,
    },
});