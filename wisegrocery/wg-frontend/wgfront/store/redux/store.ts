import AsyncStorage from "@react-native-async-storage/async-storage";
import { secureStore } from "../storage.native";
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
import { combineReducers } from "redux";
import { configureStore } from '@reduxjs/toolkit';
import settingsReducer from "./settingsSlice";
import userReducer from "./userSlice";
import { Platform } from "react-native";

const rootPersistConfig = {
    key: 'wgstoreroot',
    storage: AsyncStorage,
    blacklist: ['auth'],
};

const authPersistConfig = {
    key: 'wgstoreauth',
    storage: Platform.OS === 'web' ? AsyncStorage : secureStore,
};

const rootReducer = combineReducers({
    secure: persistReducer(authPersistConfig, userReducer),
    main: persistReducer(rootPersistConfig, settingsReducer),
  });

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
});
export type RootStateType = ReturnType<typeof store.getState>;
export type DispatchType = typeof store.dispatch;

export const persistor = persistStore(store)