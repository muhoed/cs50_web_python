import React from 'react';
import {ActivityIndicator, StyleSheet, View} from 'react-native';

export default function Spinner () {
    return (
        <View style={styles.container}>
            <ActivityIndicator size="large" color="#007aff" />
        </View>
    );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});