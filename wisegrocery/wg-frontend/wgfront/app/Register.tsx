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
import { router } from 'expo-router';
import { useValidation } from 'react-simple-form-validator';

import Spinner from '@/components/Spinner';
import { loginUser, registerUser } from '@/store/redux/userSlice';
import { useWGDispatch } from '@/hooks/useWGDispatch';
import { useWGSelector } from '@/hooks/useWGSelector';
import { fetchSettings } from '@/store/redux/settingsSlice';

type RegisterFormType = {
    username: string | null,
    email: string | null,
    password1: string | null,
    password2: string | null,
    form: string[] | null
};

export default function Register() {
    // store
    const dispatch = useWGDispatch();
    const settingsStatus = useWGSelector(state => state.main.settings.status);

    // local state
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password1, setPassword1] = useState('');
    const [password2, setPassword2] = useState('');
    const [touchedFields, setTouchedFields] = useState({
        username: false,
        email: false,
        password1: false,
        password2: false,
      });
    const [formErrors, setFormErrors] = useState<RegisterFormType>({
        username: null,
        email: null,
        password1: null,
        password2: null,
        form: null,
    });
    const [status, setStatus] = useState('idle');

    const { isFieldInError, getErrorsInField, isFormValid } =
    useValidation({
        fieldsRules: {
          username: { required: true },
          email: { required: true, email: true },
          password1: { required: true, minlength: 8 },
          password2: { required: true, equalPassword: password1 }
        },
        state: { username, email, password1, password2 },
    });

    const onBlurHandler = (field: string) =>
        setTouchedFields((prevFields) => ({ ...prevFields, [field]: true }));

    const onRegister = async () => {
        setStatus('loading');
        if (isFormValid)
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
                            setStatus('error');
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
        setTouchedFields({ username: false, email: false, password1: false, password2: false });
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
                {touchedFields.username && isFieldInError('username') && getErrorsInField('username')
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
                    onBlur={() => onBlurHandler('email')}
                    value={email}
                />
                {touchedFields.email && isFieldInError('email') && getErrorsInField('email')
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
                    onBlur={() => onBlurHandler('password1')}
                    value={password1}
                />
                {touchedFields.password1 && isFieldInError('password1') && getErrorsInField('password1')
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
                    onBlur={() => onBlurHandler('password2')}
                    value={password2}
                />
                {touchedFields.password2 && isFieldInError('password2') && getErrorsInField('password2')
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
        textAlign: 'center',
    },
    formErrorMessage: {
        color: 'red',
        fontWeight: 'bold',
        textAlign: 'left',
    },
});