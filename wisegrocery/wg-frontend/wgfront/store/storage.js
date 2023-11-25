import AsyncStorage from '@react-native-async-storage/async-storage';

async function saveToStorage(key, value) {
    await AsyncStorage.setItem(key, value);
  }
  
async function getValueFromStorageByKey(key) {
    let result = await AsyncStorage.getItem(key);
    if (!result) {
        throw 'No values stored under that key.';
    }
    return JSON.parse(result);
}

async function deleteValueFromStorageForKey(key) {
    await AsyncStorage.removeItem(key);
}

export { saveToStorage, getValueFromStorageByKey, deleteValueFromStorageForKey }