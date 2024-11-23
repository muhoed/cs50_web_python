import { StyleSheet, Text, View } from "react-native";
import { FlatList } from "react-native-web";
import SettingLine from "./SettingLine";

export default function SettingSection (props) {

    const renderItem = ({item, index, separator}) => {
        return (
            <SettingLine 
                key={index}
                type={item.type}
                value={item.value}
                label={item.label}
                choices={item.choices}
                readonly={item.readonly}
                callback={item.callback}
                />
        );
    };

    return (
        <View style={styles.section}>
            <Text style={styles.sectionTitle}>{props.title }: </Text>
            <FlatList
                data={props.settingsList}
                renderItem={renderItem}
                />
        </View>
    );
};

const styles = StyleSheet.create({
  section: {
    borderWidth: 2,
    borderRadius: 10,
    alignItems: "left",
    width: "30%",
    maxHeight: "80%",
    marginTop: "3%",
    marginLeft: "1%",
    marginRight: "1%",
  },
  sectionTitle: {
    fontSize: "1em",
    fontWeight: "bold",
    marginTop: "5%",
    marginBottom: "2%",
    textAlign: "center",
  },
});