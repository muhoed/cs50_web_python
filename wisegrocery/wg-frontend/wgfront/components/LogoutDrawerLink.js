import { DrawerContentScrollView, DrawerItem, DrawerItemList } from "@react-navigation/drawer";
import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { settingsReset } from "../store/redux/settingsSlice";
import Spinner from "./Spinner";
import { logoutUser } from "../store/redux/userSlice";

export default function LogoutDrawerLink (props) {
    const dispatch = useDispatch();
    const user = useSelector(state => state.secure.user.auth);
    const userError = useSelector(state => state.secure.user.error);
    const [status, setStatus] = useState('idle');

    const onLogout = () => {
        setStatus('loading');
        try {
            dispatch(logoutUser());
            dispatch(settingsReset());
            setStatus('success');
        } catch (error) {
            console.log("Logout error: " + error);
            setStatus("error");
        } finally {
            props.navigation.closeDrawer();
        }
    };

    if (status === 'loading') {
        return (
            <Spinner />
        );
    }

    return (
        <DrawerContentScrollView {...props}>
            <DrawerItemList {...props} />
            { user.authenticated ? (
                <DrawerItem label="Sign Out" onPress={() => onLogout()} /> ) : null}
        </DrawerContentScrollView>
    );
}