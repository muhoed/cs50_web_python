// import createSecureStore from "redux-persist-expo-securestore";

// export const secureStore = createSecureStore();

import * as secureStore from 'expo-secure-store';

// async function saveToStorage(key: any, value: any) {
//     await secureStore.setItemAsync(key, value);
//   }
  
// async function getValueFromStorageByKey(key: any) {
//     let result = await secureStore.getItemAsync(key);
//     if (!result) {
//         throw 'No values stored under that key.';
//     }
//     return JSON.parse(result);
// }

// async function deleteValueFromStorageForKey(key: any) {
//     await secureStore.deleteItemAsync(key);
// }

// export { secureStore, saveToStorage, getValueFromStorageByKey, deleteValueFromStorageForKey }

async function getItem(key: string) {
    let result = await secureStore.getItemAsync(key);
    if (!result) {
        throw 'No values stored under that key.';
    }
    return JSON.parse(result);
}

async function setItem(key: string, value: string) {
    await secureStore.setItemAsync(key, value)
                    .catch((err) => { throw `Cannot store value under key ${key}.`; });
}

async function removeItem(key: string) {
    await secureStore.deleteItemAsync(key)
                    .catch((err) => { throw `Cannot delete value under key ${key}.`; });
}

export { secureStore, getItem, setItem, removeItem }