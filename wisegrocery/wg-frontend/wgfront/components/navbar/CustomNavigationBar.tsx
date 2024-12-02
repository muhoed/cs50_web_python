import { Appbar } from 'react-native-paper';

import useScreenSize from '../../hooks/useScreenSize';
import NavbarMenu from './NavbarMenu';

export default function CustomNavigationBar(props: any) {
    const screenSize = useScreenSize();

    return (
      <Appbar.Header>
        {props.back ? <Appbar.BackAction onPress={props.navigation.goBack} /> : null}
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