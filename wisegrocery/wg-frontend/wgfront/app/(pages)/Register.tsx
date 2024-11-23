import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    TextInput,
    Pressable,
    FlatList,
  } from 'react-native';
import React, {useState} from 'react';
import { useValidation } from 'react-native-form-validator';
import { useDispatch, useSelector } from 'react-redux';

import Spinner from '../../components/Spinner';
import { fetchSettings, setSettings } from '../../store/redux/settingsSlice';
import { loginUser, registerUser } from '../../store/redux/userSlice';
import { DispatchType, RootStateType } from '@/store/redux/store';

type RegisterFormType = {
    username: string | null,
    email: string | null,
    password1: string | null,
    password2: string | null,
    form: string[] | null
}

export default function Register ({ navigation } : { navigation: any }) {
    // store
    const dispatch = useDispatch<DispatchType>();
    const settingsStatus = useSelector<RootStateType>(state => state.main.settings.status);

    // local state
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password1, setPassword1] = useState('');
    const [password2, setPassword2] = useState('');
    const [formErrors, setFormErrors] = useState<RegisterFormType>({
        username: null,
        email: null,
        password1: null,
        password2: null,
        form: null,
    });
    const [status, setStatus] = useState('idle');

    const { validate, isFieldInError, getErrorsInField } =
    useValidation({
      state: { username, email, password1, password2 },
    });

    const onRegister = async () => {
        setStatus('loading');
        if (
            validate({
                username: { required: true },
                email: { email: true, required: true },
                password1: { required: true },
                password2: { equalPassword: password1 },
            })
        ) 
        {
            await dispatch(registerUser({
                username, email, password1, password2,
                password: null
            })).unwrap()
                .then(async (response) => {
                    console.log(response);
                    let password = password1;
                    await dispatch(loginUser({
                        username, password,
                        email: null,
                        password1: null,
                        password2: null
                    }))
                        .then(() => {
                            if (settingsStatus !== 'loading') {
                                dispatch(fetchSettings());
                            }
                            setStatus('success');
                        }).catch((error) => {
                            console.log(error);
                            setStatus('érror');
                        });
                })
                .catch((error) => {
                    if (error.message) {
                        const errors = JSON.parse(error.message);
                        setFormErrors({
                            ...formErrors,
                            username: errors.username || null,
                            email: errors.email || null,
                            password1: errors.password1 || null,
                            password2: errors.password2 || null,
                            form: errors.detail ? [errors.detail] : null,
                        });
                    } else {
                        setFormErrors({
                            ...formErrors,
                            form: [JSON.stringify(error)],
                        });
                    }
                    setStatus('error');
                });
        } else {
            setStatus('error');
        }
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
                    value={username}
                />
                {isFieldInError('username') && getErrorsInField('username')
                    .map((errorMessage: string, index: number) => (
                  <Text key={index} style={styles.formErrorMessage}>{errorMessage}</Text>
                ))}
                <FlatList data={formErrors?.username} renderItem={renderFieldError} />
                <TextInput
                    style={styles.input}
                    placeholder="Email address"
                    keyboardType="email-address"
                    autoCapitalize="none"
                    onChangeText={text => setEmail(text)}
                    value={email}
                />
                {isFieldInError('email') && getErrorsInField('email')
                    .map((errorMessage: string, index: number) => (
                  <Text key={index} style={styles.formErrorMessage}>{errorMessage}</Text>
                ))}
                <FlatList data={formErrors?.email} renderItem={renderFieldError} />
                <TextInput
                    style={styles.input}
                    placeholder="Password"
                    keyboardType="visible-password"
                    secureTextEntry
                    onChangeText={text => setPassword1(text)}
                    value={password1}
                />
                {isFieldInError('password1') && getErrorsInField('password1')
                    .map((errorMessage: string, index: number) => (
                  <Text key={index} style={styles.formErrorMessage}>{errorMessage}</Text>
                ))}
                <FlatList data={formErrors?.password1} renderItem={renderFieldError} />
                <TextInput
                    style={styles.input}
                    placeholder="Confirm password"
                    keyboardType="visible-password"
                    secureTextEntry
                    onChangeText={text => setPassword2(text)}
                    value={password2}
                />
                {isFieldInError('password2') && getErrorsInField('password2')
                    .map((errorMessage: string, index: number) => (
                  <Text key={index} style={styles.formErrorMessage}>{errorMessage}</Text>
                ))}
                <FlatList data={formErrors?.password2} renderItem={renderFieldError} />
            </View>
            <Pressable style={({ pressed }) => [{opacity: pressed ? 75 : 100}, styles.button]} onPress={() => onRegister()}>
                <Text style={styles.buttonText}>Sign Up</Text>
            </Pressable>
            <View>
                <Text style={styles.signUpText}>or</Text>
                <Pressable style={({ pressed }) => [{opacity: pressed ? 75 : 100}, styles.signUpText]} onPress={() => navigation.navigate('SignIn')}>
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
    signInLink: {
        color:'blue',
        textDecorationLine: 'underline',
    },
    formErrorMessage: {
        color: 'red',
        fontWeight: 'bold',
        textAlign: 'left',
    },
});