import { store } from "../store/redux/store";

export default function authHeader(refresh=false) {
    let state = store.getState();
    const token = refresh ? state.secure.user.auth.refreshToken : state.secure.user.auth.accessToken;
    if (token) {
      return { Authorization: 'Bearer ' + token };
    } else {
      return {};
    }
  }