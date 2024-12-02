import * as secureStore from 'expo-secure-store';

async function getItem(key: string) {
    let result = await secureStore.getItemAsync(key);
    if (!result) {
        throw 'No values stored under that key.';
    }
    return JSON.parse(result);
}

async function setItem(key: string, value: string) {
    await secureStore.setItemAsync(key, value)
                    .catch((err: any) => { throw `Cannot store value under key ${key}.`; });
}

async function removeItem(key: string) {
    await secureStore.deleteItemAsync(key)
                    .catch((err) => { throw `Cannot delete value under key ${key}.`; });
}

export { secureStore, getItem, setItem, removeItem }