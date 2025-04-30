import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    TextInput,
    Pressable,
    FlatList,
    Platform
} from 'react-native';
import React, { useState } from 'react';
import { router } from 'expo-router';
import { useForm, Controller } from 'react-hook-form';

import { fetchSettings } from '@/store/redux/settingsSlice';
import Spinner from '@/components/Spinner';
import { loginUser } from '@/store/redux/userSlice';
import { useWGDispatch } from '@/hooks/useWGDispatch';
import { useWGSelector } from '@/hooks/useWGSelector';

type LoginFormType = {
    username: string;
    password: string;
}

export default function Login() {
    // store
    const dispatch = useWGDispatch();
    const settingsStatus = useWGSelector(state => state.main.settings.status);
    const userStatus = useWGSelector(state => state.secure.user.status);
    // local state
    const [status, setStatus] = useState('idle');
    const [formErrors, setFormErrors] = useState<{
        username?: string[];
        password?: string[];
        form?: string[];
    }>({});

    const { control, handleSubmit, formState: { errors, isValid } } = useForm<LoginFormType>({
        mode: 'onChange',
        defaultValues: {
            username: '',
            password: ''
        }
    });

    const onLogin = async (data: LoginFormType) => {
        try {
            setStatus('loading');
            setFormErrors({});
            dispatch(loginUser({
                username: data.username,
                password: data.password,
                email: null,
                password1: null,
                password2: null
            })).unwrap()
                .then(() => {
                    if (settingsStatus !== 'loading') {
                        dispatch(fetchSettings());
                    }
                    setStatus('success');
                    router.navigate('/(pages)');
                })
                .catch((error) => {
                    if (error.message) {
                        try {
                            const errors = JSON.parse(error.message);
                            setFormErrors({
                                username: errors.username || undefined,
                                password: errors.password || undefined,
                                form: errors.detail ? [errors.detail] : errors.non_field_errors || undefined
                            });
                        } catch (parseError) {
                            console.log("Error parsing login error:", parseError);
                            setFormErrors({ form: ["Login failed. Please try again."] });
                        }
                    } else {
                        setFormErrors({ form: ["Login failed. An unknown error occurred."] });
                    }
                    setStatus('error');
                });
        } catch (error) {
            console.log(error);
            setFormErrors({
                form: ["Login failed. " + JSON.stringify(error)],
            });
            setStatus('error');
        }
    };

    const renderFieldError = ({ item, index }: {item: string, index: number}) => {
        return (<Text key={index} style={styles.formErrorMessage}>{item}</Text>);
    };

    if (status === 'loading') {
        return (
            <Spinner />
        );
    }

    return (
        <SafeAreaView style={styles.container}>
            <Text style={[styles.logo, {textAlign: 'center'}]}>Wise Grocery</Text>
            <View style={styles.form}>
                <FlatList data={formErrors?.form} renderItem={renderFieldError} />
                
                <Controller
                    control={control}
                    rules={{
                        required: 'Username is required',
                    }}
                    render={({ field: { onChange, onBlur, value } }) => (
                        <TextInput
                            style={styles.input}
                            placeholder="Username"
                            keyboardType="default"
                            autoCapitalize="none"
                            onChangeText={onChange}
                            onBlur={onBlur}
                            value={value}
                        />
                    )}
                    name="username"
                />
                {errors.username && (
                    <Text style={styles.formErrorMessage}>{errors.username.message}</Text>
                )}
                <FlatList data={formErrors?.username} renderItem={renderFieldError} />

                <Controller
                    control={control}
                    rules={{
                        required: 'Password is required',
                    }}
                    render={({ field: { onChange, onBlur, value } }) => (
                        <TextInput
                            style={styles.input}
                            placeholder="Password"
                            secureTextEntry
                            onChangeText={onChange}
                            onBlur={onBlur}
                            value={value}
                            onSubmitEditing={handleSubmit(onLogin)}
                        />
                    )}
                    name="password"
                />
                {errors.password && (
                    <Text style={styles.formErrorMessage}>{errors.password.message}</Text>
                )}
                <FlatList data={formErrors?.password} renderItem={renderFieldError} />
            </View>
            <Pressable 
                style={({ pressed }) => [{opacity: pressed ? 75 : 100}, styles.button]} 
                onPress={handleSubmit(onLogin)} 
                disabled={!isValid}
            >
                <Text style={styles.buttonText}>Login</Text>
            </Pressable>
            <View>
                <Text style={styles.signUpText}>or</Text>
                <Pressable style={({ pressed }) => [{opacity: pressed ? 75 : 100}]} onPress={() => router.navigate('/Register')}>
                    <Text style={styles.signUpLink}>Sign Up</Text>
                </Pressable>
            </View>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'flex-start',
        width: '100%',
    },
    logo: {
        fontSize: 60,
        marginVertical: '5%',
        textAlign: 'center'
    },
    form: {
        width: Platform.OS === 'web' ? '25%' : '80%',
        alignSelf: 'center',
        marginVertical: '1%',
    },
    input: {
        fontSize: 20,
        paddingBottom: 10,
        borderBottomWidth: 1,
        marginVertical: 20,
    },
    button: {
       alignItems: 'center',
       justifyContent: 'center',
       paddingVertical: 12,
       paddingHorizontal: 32,
       elevation: 3,
       backgroundColor: 'blue',
       borderRadius: 25,
    },
    buttonText: {
       fontSize: 16,
       lineHeight: 21,
       fontWeight: 'bold',
       letterSpacing: 0.25,
       color: 'white',
    },
    signUpText: {
        marginTop: 10,
        fontSize: 12,
        textAlign: 'center',
    },
    signUpLink: {
        color:'blue',
        textDecorationLine: 'underline',
    },
    formErrorMessage: {
        color: 'red',
        fontWeight: 'bold',
        textAlign: 'left',
    },
});