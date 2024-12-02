//import { DispatchType, PersistantDispatchType } from '@/store/redux/store';
import { DispatchType } from '@/store/redux/store';
import { Platform } from 'react-native';
import { useDispatch } from 'react-redux';

//export const useWGDispatch = Platform.OS === 'web' ? 
//                        useDispatch.withTypes<DispatchType>() : 
//                        useDispatch.withTypes<PersistantDispatchType>();

export const useWGDispatch = useDispatch.withTypes<DispatchType>();