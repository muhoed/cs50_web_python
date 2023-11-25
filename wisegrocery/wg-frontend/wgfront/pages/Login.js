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
import { useValidation } from 'react-native-form-validator';
import { useDispatch, useSelector } from 'react-redux';

import { fetchSettings, settingsSet } from '../store/redux/settingsSlice';
import Spinner from '../components/Spinner';
import { loginUser } from '../store/redux/userSlice';
  
export default function Login ({ navigation }) {
    // store
    const dispatch = useDispatch();
    const settingsStatus = useSelector(state => state.main.settings.status);
    const userStatus = useSelector(state => state.secure.user.status);
    // local state
    const [status, setStatus] = useState('idle');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [formErrors, setFormErrors] = useState({
        username: null,
        password: null,
        form: null,
    });

    const { validate, isFieldInError, getErrorsInField, getErrorMessages } =
    useValidation({
      state: { username, password },
    });

    const onLogin = async () => {
        if (
            validate({
                username: { required: true },
                password: { required: true },
            })
        ) 
        {
            try {
                setStatus('loading');
                if (userStatus !== 'loading') {
                    await dispatch(loginUser({username, password})).unwrap()
                        .then((response) => {
                            if (settingsStatus !== 'loading') {
                                dispatch(fetchSettings())
                            }
                            setStatus('success');
                        }).catch((error) => {
                            if (error.message) {
                                const errors = JSON.parse(error.message);
                                setFormErrors({
                                    ...formErrors,
                                    username: errors.username || null,
                                    password: errors.password || null,
                                    form: [errors.detail] || null,
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
                setStatus('error');
            }
        }   
    };

    const renderFieldError = ({ item, index, separators }) => {
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
                    value={username}
                />
                {isFieldInError('username') && getErrorsInField('username').map((errorMessage, index) => (
                  <Text key={index} style={styles.formErrorMessage}>{errorMessage}</Text>
                ))}
                <FlatList data={formErrors?.username} renderItem={renderFieldError} />

                <TextInput
                    style={styles.input}
                    placeholder="Password"
                    secureTextEntry
                    onChangeText={text => setPassword(text)}
                    value={password}
                />
                {isFieldInError('password') && getErrorsInField('password').map((errorMessage, index) => (
                  <Text key={index} style={styles.formErrorMessage}>{errorMessage}</Text>
                ))}
                <FlatList data={formErrors?.password} renderItem={renderFieldError} />
            </View>
            <Pressable style={({ pressed }) => [{opacity: pressed ? 75 : 100}, styles.button]} onPress={() => onLogin()}>
                <Text style={styles.buttonText}>Login</Text>
            </Pressable>
            <View>
                <Text style={styles.signUpText}>or</Text>
                <Pressable style={({ pressed }) => {opacity: pressed ? 75 : 100}} onPress={() => navigation.navigate('SignUp')}>
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
       borderRadius: 4,
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