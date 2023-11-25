import createSecureStore from "redux-persist-expo-securestore";

const secureStore = createSecureStore();

async function saveToStorage(key, value) {
    await secureStore.setItemAsync(key, value);
  }
  
async function getValueFromStorageByKey(key) {
    let result = await secureStore.getItemAsync(key);
    if (!result) {
        throw 'No values stored under that key.';
    }
    return JSON.parse(result);
}

async function deleteValueFromStorageForKey(key) {
    await secureStore.deleteItemAsync(key);
}

export { secureStore, saveToStorage, getValueFromStorageByKey, deleteValueFromStorageForKey }