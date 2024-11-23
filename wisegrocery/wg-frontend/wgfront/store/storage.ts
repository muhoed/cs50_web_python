import AsyncStorage from '@react-native-async-storage/async-storage';

async function saveToStorage(key: string, value: string) {
    await AsyncStorage.setItem(key, value);
  }
  
async function getValueFromStorageByKey(key: string) {
    let result = await AsyncStorage.getItem(key);
    if (!result) {
        throw 'No values stored under that key.';
    }
    return JSON.parse(result);
}

async function deleteValueFromStorageForKey(key: string) {
    await AsyncStorage.removeItem(key);
}

export { saveToStorage, getValueFromStorageByKey, deleteValueFromStorageForKey }