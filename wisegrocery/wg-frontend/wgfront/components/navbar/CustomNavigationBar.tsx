import { useEffect, useState } from 'react';
import { Appbar } from 'react-native-paper';
import { Platform } from 'react-native-web';
import useScreenSize from '../../hooks/useScreenSize';
import NavbarMenu from './NavbarMenu';

export default function CustomNavigationBar(props) {
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