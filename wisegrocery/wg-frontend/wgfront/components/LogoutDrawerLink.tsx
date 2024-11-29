import { DrawerContentScrollView, DrawerItem, DrawerItemList } from "@react-navigation/drawer";
import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import { settingsReset } from "../store/redux/settingsSlice";
import Spinner from "./Spinner";
import { logoutUser } from "../store/redux/userSlice";
import { RootStateType } from "@/store/redux/store";

export default function LogoutDrawerLink (props: any) {
    const dispatch = useDispatch();
    const user = useSelector<RootStateType, AuthType>(state => state.secure.user.auth);
    const userError = useSelector<RootStateType>(state => state.secure.user.error);
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