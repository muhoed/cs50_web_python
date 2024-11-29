import { Storage } from 'redux-persist'
import { MMKV } from "react-native-mmkv"

export const rootStorage = new MMKV({
  id: `root-storage`,
  encryptionKey: 'wg-front-dev-encription-key',
  readOnly: false
})

export const authStorage = new MMKV({
  id: `auth-storage`,
  encryptionKey: 'wg-front-dev-encription-key',
  readOnly: false
})

export const reduxRootStorage: Storage = {
  setItem: (key, value) => {
    rootStorage.set(key, value)
    return Promise.resolve(true)
  },
  getItem: (key) => {
    const value = rootStorage.getString(key)
    return Promise.resolve(value)
  },
  removeItem: (key) => {
    rootStorage.delete(key)
    return Promise.resolve()
  },
}

export const reduxAuthStorage: Storage = {
  setItem: (key, value) => {
    authStorage.set(key, value)
    return Promise.resolve(true)
  },
  getItem: (key) => {
    const value = authStorage.getString(key)
    return Promise.resolve(value)
  },
  removeItem: (key) => {
    authStorage.delete(key)
    return Promise.resolve()
  },
}