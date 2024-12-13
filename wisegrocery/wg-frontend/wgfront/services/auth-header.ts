let injStore: any; // initialize it undefined
export const setStoreForAuthHeader = (injectedStore: any) => injStore = injectedStore;

export default function authHeader(refresh=false) {
    let state = injStore.getState();
    const token = refresh ? state.secure.user.auth.refresh : state.secure.user.auth.access;
    if (token) {
      return { Authorization: 'Bearer ' + token };
    } else {
      return {};
    }
  };