import * as secureStore from "../storage.native";
// import secureLocalStorage from 'react-secure-storage'; // No longer using this for web
import storage from 'redux-persist/lib/storage'; // Import default web storage
import { 
    persistReducer, 
    persistStore,
    FLUSH,
    REHYDRATE,
    PAUSE,
    PERSIST,
    PURGE,
    REGISTER,
} from 'redux-persist';
import { combineReducers, configureStore } from '@reduxjs/toolkit';
import settingsReducer from "./settingsSlice";
import userReducer from "./userSlice";
import { Platform } from "react-native";
import { setStoreForAuthHeader } from "@/services/auth-header";

const rootPersistConfig = {
    key: 'wgstoreroot',
    // Use standard localStorage for web (window defined), secureStore for native
    storage: typeof window !== 'undefined' ? storage : secureStore, 
    blacklist: ['wgstoreauth'],
};

const authPersistConfig = {
    key: 'wgstoreauth',
    // Use standard localStorage for web (window defined), secureStore for native
    storage: typeof window !== 'undefined' ? storage : secureStore,
    blacklist: ['wgstoreroot'],
};

// const rootReducer = combineReducers({
//     secure: userReducer,
//     main: settingsReducer,
//   });

const rootReducerPersistent = combineReducers({
  secure: persistReducer(authPersistConfig, userReducer),
  main: persistReducer(rootPersistConfig, settingsReducer),
});

export const persistantStore = configureStore({
  reducer: rootReducerPersistent,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
});

// export const storea = configureStore({
//   reducer: rootReducer,
// });

// let storeTmp = null;
// //let persistorTmp = null;

// // if (Platform.OS !== 'web')
// //   setStoreForAuthHeader(persistantStore);
// // else
// //   setStoreForAuthHeader(store);

// if (typeof window === 'undefined') { //(Platform.OS === 'web') {
//   storeTmp = configureStore({
//     reducer: rootReducerPersistent,
//     middleware: (getDefaultMiddleware) =>
//       getDefaultMiddleware({
//         serializableCheck: {
//           ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
//         },
//       }),
//   });
// } else {
//   storeTmp = configureStore({
//     reducer: rootReducerPersistent,
//     middleware: (getDefaultMiddleware) =>
//       getDefaultMiddleware({
//         serializableCheck: {
//           ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
//         },
//       }),
//   });
//   //persistorTmp = persistStore(storeTmp);
// }

export const store = persistantStore;

setStoreForAuthHeader(store);

export type store = typeof store;
//export type persistantStore = typeof persistantStore;
export type RootStateType = ReturnType<typeof store.getState>;
//export type PersistantRootStateType = ReturnType<typeof persistantStore.getState>;
export type DispatchType = typeof store.dispatch;
//export type PersistantDispatchType = typeof persistantStore.dispatch;

//export const persistor = persistStore(persistantStore);
export const persistor = persistStore(store); //persistorTmp;