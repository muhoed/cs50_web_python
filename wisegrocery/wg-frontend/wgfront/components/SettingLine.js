import { StyleSheet, Text, View } from "react-native";
import { CheckBox, Picker, TextInput } from "react-native-web";
import InputSpinner from "react-native-input-spinner";
import { pureFinalPropsSelectorFactory } from "react-redux/es/connect/selectorFactory";

export default function SettingLine(props) {
    let settingInput;

    switch(props.type) {
        case "checkbox":
            settingInput = <CheckBox
                                style={[{opacity: props.readonly ? 50 : 100}, styles.checkbox]}
                                value={props.value}
                                onValueChange={(val) => props.callback(val)}
                                disabled={props.readonly}
                                />;
            break;
        case "timedelta":
            settingInput = <InputSpinner
                                max={30}
                                min={0}
                                step={1}
                                height={30}
                                value={props.value}
                                fontSize={14}
                                editable={false}
                                skin="clean"
                                shadow={!props.readonly}
                                style={styles.timedelta}
                                onChange={(val) => props.callback(val + " 00:00:00")}
                                disabled={props.readonly}
                            />;
            break;
        case "select":
            settingInput = <Picker
                                style={[{opacity: props.readonly ? 50 : 100}, styles.picker]}
                                value={props.value}
                                onValueChange={(val) => props.callback(val)}
                                enabled={!props.readonly}>
                                {Object.values(props.choices).map((option) => {
                                    return (
                                        <Picker.Item
                                            key={option.key}
                                            value={option.key}
                                            label={option.label} />
                                    );
                                })}
                            </Picker>
            break;
        default:
            settingInput = <TextInput
                                style={[{opacity: props.readonly ? 50 : 100}, styles.textinput]}
                                value={props.value}
                                onChange={(val) => props.callback(val)}
                                disabled={props.readonly}
                                />;
            break;
    }

    return (
        <View style={styles.line}>
            <Text style={styles.label}>{props.label}</Text>
            <View style={styles.settingWrapper}>
            {settingInput}
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
  line: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    paddingLeft: "5%",
    paddingRight: "5%",
    marginTop: "4%",
    marginBottom: "3%",
  },
  label: {
    fontSize: "1em",
    textAlign: "left",
    width: "75%",
  },
  settingWrapper: {
    width: "25%",
    alignItems: "center",
    padding: "1%",
    overflow: "hidden",
  },
  picker: {
    width: "100%",
  },
});