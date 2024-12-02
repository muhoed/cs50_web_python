import secureLocalStorage from 'react-secure-storage';

function saveToStorage(key: string, value: string) {
    secureLocalStorage.setItem(key, value);
  }
  
function getValueFromStorageByKey(key: string) {
    let result = secureLocalStorage.getItem(key);
    if (!result) {
        throw 'No values stored under that key.';
    }
    return result;
}

function deleteValueFromStorageForKey(key: string) {
    secureLocalStorage.removeItem(key);
}

export { saveToStorage, getValueFromStorageByKey, deleteValueFromStorageForKey }