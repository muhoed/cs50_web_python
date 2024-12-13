import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    TextInput,
    Pressable,
    FlatList,
  } from 'react-native';
import React, { useState } from 'react';
import { router } from 'expo-router';
import { useValidation } from 'react-simple-form-validator';

import { fetchSettings } from '@/store/redux/settingsSlice';
import Spinner from '@/components/Spinner';
import { loginUser } from '@/store/redux/userSlice';
import { useWGDispatch } from '@/hooks/useWGDispatch';
import { useWGSelector } from '@/hooks/useWGSelector';

type LoginFormType = {
    username: string | null,
    password: string | null,
    form: string[] | null
}
  
export default function Login() {
    // store
    const dispatch = useWGDispatch();
    const settingsStatus = useWGSelector(state => state.main.settings.status);
    const userStatus = useWGSelector(state => state.secure.user.status);
    // local state
    const [status, setStatus] = useState('idle');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [touchedFields, setTouchedFields] = useState({
        username: false,
        password: false,
      });
    const [formErrors, setFormErrors] = useState<LoginFormType>({
        username: null,
        password: null,
        form: null,
    });

    const { isFieldInError, getErrorsInField, isFormValid } =
    useValidation({
        fieldsRules: {
          username: { required: true },
          password: { required: true }
        },
        state: { username, password },
    });

    const onBlurHandler = (field: string) =>
        setTouchedFields((prevFields) => ({ ...prevFields, [field]: true }));

    const onLogin = async () => {
        if (isFormValid) 
        {
            try {
                setStatus('loading');
                if (userStatus !== 'loading') {
                    await dispatch(loginUser({
                        username, password,
                        email: null,
                        password1: null,
                        password2: null
                    })).unwrap()
                        .then((response: any) => {
                            if (settingsStatus !== 'loading') {
                                dispatch(fetchSettings());
                            }
                            setStatus('success');
                            router.navigate('/(pages)');
                        }).catch((error: any) => {
                            if (error.message) {
                                const errors = JSON.parse(error.message);
                                setFormErrors({
                                    ...formErrors,
                                    username: errors.username || null,
                                    password: errors.password || null,
                                    form: errors.detail ? [errors.detail] : null,
                                });
                            } else {
                                setFormErrors({
                                    ...formErrors,
                                    form: ["Login failed. " + JSON.stringify(error)],
                                });
                            }
                            setStatus('error');
                        });
                }
            } catch (error) {
                console.log(error);
                setFormErrors({
                    ...formErrors,
                    form: ["Login failed. " + JSON.stringify(error)],
                });
                setStatus('error');
            }
        }
        setTouchedFields({ username: false, password: false }); 

        if (status === 'success')
            router.navigate('/(pages)');
    };

    const renderFieldError = ({ item, index, separators }: {item: string, index: number, separators: any}) => {
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
                <TextInput
                    style={styles.input}
                    placeholder="Username"
                    keyboardType="default"
                    autoCapitalize="none"
                    onChangeText={text => setUsername(text)}
                    onBlur={() => onBlurHandler('username')}
                    value={username}
                />
                {touchedFields.username && isFieldInError('username') && getErrorsInField('username').map((errorMessage: string, index: number) => (
                  <Text key={index} style={styles.formErrorMessage}>{errorMessage}</Text>
                ))}
                <FlatList data={formErrors?.username} renderItem={renderFieldError} />

                <TextInput
                    style={styles.input}
                    placeholder="Password"
                    secureTextEntry
                    onChangeText={text => setPassword(text)}
                    onBlur={() => onBlurHandler('password')}
                    value={password}
                />
                {touchedFields.password && isFieldInError('password') && getErrorsInField('password').map((errorMessage: string, index: number) => (
                  <Text key={index} style={styles.formErrorMessage}>{errorMessage}</Text>
                ))}
                <FlatList data={formErrors?.password} renderItem={renderFieldError} />
            </View>
            <Pressable style={({ pressed }) => [{opacity: pressed ? 75 : 100}, styles.button]} onPress={() => onLogin()} disabled={!isFormValid}>
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
        margin: '5%',
    },
    form: {
        width: '80%',
        margin: '1%',
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