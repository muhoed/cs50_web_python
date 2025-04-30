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

import Spinner from '@/components/Spinner';
import { loginUser, registerUser } from '@/store/redux/userSlice';
import { useWGDispatch } from '@/hooks/useWGDispatch';
import { useWGSelector } from '@/hooks/useWGSelector';
import { fetchSettings } from '@/store/redux/settingsSlice';

type RegisterFormType = {
    username: string;
    email: string;
    password1: string;
    password2: string;
};

export default function Register() {
    // store
    const dispatch = useWGDispatch();
    const settingsStatus = useWGSelector(state => state.main.settings.status);

    // local state
    const [formErrors, setFormErrors] = useState<{
        username?: string[];
        email?: string[];
        password1?: string[];
        password2?: string[];
        form?: string[];
    }>({});
    const [status, setStatus] = useState('idle');

    const { control, handleSubmit, formState: { errors, isValid }, watch } = useForm<RegisterFormType>({
        mode: 'onChange',
        defaultValues: {
            username: '',
            email: '',
            password1: '',
            password2: ''
        }
    });

    const password1 = watch('password1');

    const onRegister = async (data: RegisterFormType) => {
        setStatus('loading');
        await dispatch(registerUser({
            username: data.username,
            email: data.email,
            password1: data.password1,
            password2: data.password2,
            password: null
        })).unwrap()
            .then(async (response) => {
                console.log(response);
                await dispatch(loginUser({
                    username: data.username,
                    password: data.password1,
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
                    .catch((loginError) => {
                        console.log("Login after register failed:", loginError);
                        setStatus('error');
                    });
            })
            .catch((error) => {
                if (error.message) {
                    const errors = JSON.parse(error.message);
                    setFormErrors({
                        username: errors.username || undefined,
                        email: errors.email || undefined,
                        password1: errors.password1 || undefined,
                        password2: errors.password2 || undefined,
                        form: errors.detail ? [errors.detail] : undefined,
                    });
                } else {
                    setFormErrors({
                        form: [JSON.stringify(error)],
                    });
                }
                setStatus('error');
            });
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
                        required: 'Email is required',
                        pattern: {
                            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                            message: 'Invalid email address'
                        }
                    }}
                    render={({ field: { onChange, onBlur, value } }) => (
                        <TextInput
                            style={styles.input}
                            placeholder="Email address"
                            keyboardType="email-address"
                            autoCapitalize="none"
                            onChangeText={onChange}
                            onBlur={onBlur}
                            value={value}
                        />
                    )}
                    name="email"
                />
                {errors.email && (
                    <Text style={styles.formErrorMessage}>{errors.email.message}</Text>
                )}
                <FlatList data={formErrors?.email} renderItem={renderFieldError} />

                <Controller
                    control={control}
                    rules={{
                        required: 'Password is required',
                        minLength: {
                            value: 8,
                            message: 'Password must be at least 8 characters'
                        }
                    }}
                    render={({ field: { onChange, onBlur, value } }) => (
                        <TextInput
                            style={styles.input}
                            placeholder="Password"
                            keyboardType="visible-password"
                            secureTextEntry
                            onChangeText={onChange}
                            onBlur={onBlur}
                            value={value}
                        />
                    )}
                    name="password1"
                />
                {errors.password1 && (
                    <Text style={styles.formErrorMessage}>{errors.password1.message}</Text>
                )}
                <FlatList data={formErrors?.password1} renderItem={renderFieldError} />

                <Controller
                    control={control}
                    rules={{
                        required: 'Please confirm your password',
                        validate: value => value === password1 || 'Passwords do not match'
                    }}
                    render={({ field: { onChange, onBlur, value } }) => (
                        <TextInput
                            style={styles.input}
                            placeholder="Confirm password"
                            keyboardType="visible-password"
                            secureTextEntry
                            onChangeText={onChange}
                            onBlur={onBlur}
                            value={value}
                            onSubmitEditing={handleSubmit(onRegister)}
                        />
                    )}
                    name="password2"
                />
                {errors.password2 && (
                    <Text style={styles.formErrorMessage}>{errors.password2.message}</Text>
                )}
                <FlatList data={formErrors?.password2} renderItem={renderFieldError} />
            </View>
            <Pressable 
                style={({ pressed }) => [{opacity: pressed ? 75 : 100}, styles.button]} 
                onPress={handleSubmit(onRegister)}
                disabled={!isValid}
            >
                <Text style={styles.buttonText}>Sign Up</Text>
            </Pressable>
            <View>
                <Text style={styles.signUpText}>or</Text>
                <Pressable style={({ pressed }) => [{opacity: pressed ? 75 : 100}, styles.signUpText]} onPress={() => router.navigate('/Login')}>
                    <Text style={styles.signInLink}>Sign In</Text>
                </Pressable>
                <Text style={styles.signUpText}>if already registered</Text>
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
        textAlign: 'center',
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
    signInLink: {
        color:'blue',
        textDecorationLine: 'underline',
        textAlign: 'center',
    },
    formErrorMessage: {
        color: 'red',
        fontWeight: 'bold',
        textAlign: 'left',
    },
});