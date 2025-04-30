import { FlatList, Platform, SafeAreaView, StyleSheet, View, ListRenderItemInfo, Text, useWindowDimensions } from "react-native";
import { StatusBar } from "expo-status-bar";
import React from "react";
import { Link } from "expo-router";
import useScreenSize from "../../hooks/useScreenSize";

import ModuleTile from "../../components/ModuleTile";
import { MODULES } from "../../enumerations/modules";

export default function Home() {
  const screenSize = useScreenSize();
  const { width: screenWidth } = useWindowDimensions();
  const homeModules = MODULES.filter(module => module.parent === "Home");
  console.log("Home Modules Count:", homeModules.length);

  const isWeb = Platform.OS === 'web';
  const numColumns = isWeb ? 3 : 2;
  const padding = styles.listContentContainer.padding ?? 0;
  const gap = styles.listContentContainer.gap ?? 0;
  const totalHorizontalPadding = padding * 2;
  const totalGapWidth = isWeb ? gap * (numColumns - 1) : gap;
  const availableWidth = screenWidth - totalHorizontalPadding - totalGapWidth;
  const tileWidth = isWeb ? Math.floor(availableWidth / numColumns) : undefined;

  const renderItem = ({ item }: ListRenderItemInfo<ModuleType>): React.ReactElement => {
    return <ModuleTile module={item} tileWidth={isWeb ? tileWidth : undefined} />;
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.mainContent}>
        <FlatList<ModuleType>
          numColumns={Platform.OS === 'web' ? undefined : 2}
          data={homeModules}
          renderItem={renderItem}
          keyExtractor={(item) => item.name}
          style={Platform.OS === 'web' ? styles.webListStyle : undefined}
          contentContainerStyle={styles.listContentContainer}
        />
      </View>
      <View style={styles.footer}>
        <Text style={styles.footerText}>© 2024 WiseGrocery. All rights reserved.</Text>
        <View style={styles.footerLinks}>
          {/* Commenting out links until pages are created */}
          {/* <Link href="/Privacy" style={styles.footerLink}>
            <Text style={styles.footerLinkText}>Privacy Policy</Text>
          </Link>
          <Link href="/Terms" style={styles.footerLink}>
            <Text style={styles.footerLinkText}>Terms of Service</Text>
          </Link>
          <Link href="/Contact" style={styles.footerLink}>
            <Text style={styles.footerLinkText}>Contact Us</Text>
          </Link> */}
        </View>
      </View>
      <StatusBar style="light" />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Platform.OS === 'web' ? '#ffffff' : '#1a1a1a',
  },
  mainContent: {
    flex: 1,
    paddingTop: 20,
  },
  innerContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    gap: 16,
  },
  footer: {
    backgroundColor: '#2a2a2a',
    padding: 20,
    alignItems: 'center',
  },
  footerText: {
    color: '#888888',
    fontSize: 14,
    marginBottom: 12,
  },
  footerLinks: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 20,
  },
  footerLink: {
    padding: 8,
  },
  footerLinkText: {
    color: '#ffffff',
    fontSize: 14,
    textDecorationLine: 'underline',
  },
  webListStyle: {
    width: '100%',
    flex: 1,
  },
  listContentContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    alignItems: 'flex-start',
    padding: 16,
    gap: 16,
  },
}); 