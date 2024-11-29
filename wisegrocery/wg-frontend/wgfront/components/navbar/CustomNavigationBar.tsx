import { Appbar } from 'react-native-paper';
import useScreenSize from '../../hooks/useScreenSize';
import NavbarMenu from './NavbarMenu';
import { Platform } from 'react-native';

export default function CustomNavigationBar(props: any) {
    const screenSize = useScreenSize();

    return (
      <Appbar.Header>
        {Platform.OS === "web" ? 
            <Appbar.BackAction disabled={true} style={{visibility: "hidden"}} /> :
            props.back ? <Appbar.BackAction onPress={props.navigation.goBack} /> : null}
        {screenSize.isDesktop || !screenSize.isPortrait ?
            <Appbar.Content title={<NavbarMenu {...props} />} /> :
            <>
            <Appbar.Content title={'Wise Grocery'} />
            <NavbarMenu {...props} />
            </>
        }
      </Appbar.Header>
    );
  }