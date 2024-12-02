//import { PersistantRootStateType, RootStateType } from '@/store/redux/store';
import { RootStateType } from '@/store/redux/store';
import { useSelector } from 'react-redux';
import { Platform } from 'react-native';

// export const useWGSelector = Platform.OS === 'web' ? 
//                                 useSelector.withTypes<RootStateType>() : 
//                                 useSelector.withTypes<PersistantRootStateType>();

export const useWGSelector = useSelector.withTypes<RootStateType>();