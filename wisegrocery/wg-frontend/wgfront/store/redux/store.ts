import * as secureStore from "../storage.native";
//import secureLocalStorage from 'react-secure-storage';
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
    storage: secureStore, // Platform.OS === 'web' ? secureLocalStorage : secureStore,
    blacklist: ['wgstoreauth'],
};

const authPersistConfig = {
    key: 'wgstoreauth',
    storage: secureStore, // Platform.OS === 'web' ? secureLocalStorage : secureStore,
    blacklist: ['wgstoreroot'],
};

const rootReducer = combineReducers({
    secure: userReducer,
    main: settingsReducer,
  });

const rootReducerPersistent = combineReducers({
  secure: persistReducer(authPersistConfig, userReducer),
  main: persistReducer(rootPersistConfig, settingsReducer),
});

// export const persistantStore = configureStore({
//   reducer: rootReducerPersistent,
//   middleware: (getDefaultMiddleware) =>
//     getDefaultMiddleware({
//       serializableCheck: {
//         ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
//       },
//     }),
// });

// export const storea = configureStore({
//   reducer: rootReducer,
// });

let storeTmp = null;
let persistorTmp = null;

// if (Platform.OS !== 'web')
//   setStoreForAuthHeader(persistantStore);
// else
//   setStoreForAuthHeader(store);

if (Platform.OS === 'web') {
  storeTmp = configureStore({
    reducer: rootReducer,
  });
} else {
  storeTmp = configureStore({
    reducer: rootReducerPersistent,
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        serializableCheck: {
          ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
        },
      }),
  });
  persistorTmp = persistStore(storeTmp);
}

export const store = storeTmp;

setStoreForAuthHeader(store);

export type store = typeof store;
//export type persistantStore = typeof persistantStore;
export type RootStateType = ReturnType<typeof store.getState>;
//export type PersistantRootStateType = ReturnType<typeof persistantStore.getState>;
export type DispatchType = typeof store.dispatch;
//export type PersistantDispatchType = typeof persistantStore.dispatch;

//export const persistor = persistStore(persistantStore);
export const persistor = persistorTmp;