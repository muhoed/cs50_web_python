import { Appbar } from 'react-native-paper';

import NavbarMenu from './NavbarMenu';

export default function CustomNavigationBar(props: any) {

    return (
      <Appbar.Header>
        <Appbar.BackAction disabled={true} style={{visibility: "hidden"}} />
        <Appbar.Content title={<NavbarMenu {...props} />} />
      </Appbar.Header>
    );
  };