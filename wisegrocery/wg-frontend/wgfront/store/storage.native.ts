import createSecureStore from "redux-persist-expo-securestore";

export const secureStore = createSecureStore();

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