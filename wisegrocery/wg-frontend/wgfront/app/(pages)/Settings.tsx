import { Platform, SafeAreaView, StyleSheet, Text, View } from "react-native";
import { useDispatch, useSelector } from "react-redux";
import { setSettings } from "../../store/redux/settingsSlice";
import SettingSection from "../../components/SettingSection";
import { EXPIRATION_ACTIONS } from "../../enumerations/expirationActions";
import { DispatchType, RootStateType } from "@/store/redux/store";

export default function Settings() {
    const settings = useSelector<RootStateType, ConfigType>(state => state.main.settings.config);
    const settingsStatus = useSelector<RootStateType, string>(state => state.main.settings.status);
    const dispatch = useDispatch<DispatchType>();

    const setConfigValue = (name: string) => {
      return function(value: string) {
        let id = settings.id;
        let payload = {[name]: value};
        id && dispatch(setSettings({id, payload}));
      };
    }

    const notificationSettings = [
      {
        label: 'Notify by email',
        type: 'checkbox',
        value: settings.notify_by_email,
        callback: setConfigValue('notify_by_email'),
      },
      {
        label: 'Notify on expiration',
        type: 'checkbox',
        value: settings.notify_on_expiration,
        callback: setConfigValue('notify_on_expiration'),
      },
      {
        label: 'Notify on expiration before, days',
        type: 'timedelta',
        value: settings.notify_on_expiration_before ? settings.notify_on_expiration_before.split(" ")[0] : 7,
        callback: setConfigValue('notify_on_expiration_before'),
      },
      {
        label: 'Notify on stock below minimum level',
        type: 'checkbox',
        value: settings.notify_on_min_stock,
        callback: setConfigValue('notify_on_min_stock'),
      },
      // {
      //   label: 'Notify after a shopping plan was generated',
      //   type: 'checkbox',
      //   value: settings.nofity_on_shopping_plan_generated,
      //   callback: setConfigValue('nofity_on_shopping_plan_generated'),
      // },
    ];

    const expirationSettings = [
      {
        label: 'Default action on product expiration',
        type: 'select',
        choices: {...EXPIRATION_ACTIONS},
        value: settings.default_expired_action,
        callback: setConfigValue('default_expired_action'),
      },
      {
        label: 'Prolong expiration term for, days',
        type: 'timedelta',
        value: settings.prolong_expired_for,
        readonly: settings.default_expired_action !== EXPIRATION_ACTIONS.PROLONG.key,
        callback: setConfigValue('prolong_expired_for'),
      },
    ];

    const shoppingPlanSettings = [
      // {
      //   label: 'Generate shopping plan automatically',
      //   type: 'checkbox',
      //   value: settings.auto_generate_shopping_plan,
      //   callback: setConfigValue('auto_generate_shopping_plan'),
      // },
      {
        label: 'Generate shopping plan on low stock',
        type: 'checkbox',
        value: settings.gen_shop_plan_on_min_stock,
        //readonly: !settings.auto_generate_shopping_plan,
        callback: setConfigValue('gen_shop_plan_on_min_stock'),
      },
      // {
      //   label: 'Generate shopping plan periodically',
      //   type: 'checkbox',
      //   value: settings.gen_shop_plan_repeatedly,
      //   readonly: !settings.auto_generate_shopping_plan,
      //   callback: setConfigValue('gen_shop_plan_repeatedly'),
      // },
      // {
      //   label: 'Generate shopping plan every, days',
      //   type: 'timedelta',
      //   value: settings.gen_shop_plan_period,
      //   readonly: settings.auto_generate_shopping_plan ? !settings.gen_shop_plan_repeatedly : true,
      //   callback: setConfigValue('gen_shop_plan_period'),
      // },
      {
        label: 'Generate shopping plan based on historic data',
        type: 'checkbox',
        value: settings.base_shop_plan_on_historic_data,
        callback: setConfigValue('base_shop_plan_on_historic_data'),
      },
      {
        label: 'Use historic data for a period, days',
        type: 'timedelta',
        value: settings.historic_period,
        readonly: !settings.base_shop_plan_on_historic_data,
        callback: setConfigValue('historic_period'),
      },
    ];

    return (
        <SafeAreaView style={[{ flexDirection: Platform.OS === "web" ? "row" : "column" }, styles.container]}>
          { settingsStatus === 'failed' ? (<Text style={styles.error}>Saving settings failed.</Text>) : null }
          <SettingSection title="Notification settings" settingsList={notificationSettings} />
          <SettingSection title="Manage product expiration" settingsList={expirationSettings} />
          <SettingSection title="Shopping plan settings" settingsList={shoppingPlanSettings} />
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "space-around",
  },
  error: {
    textAlign: "center",
    color: "red",
    fontWeight: "bold",
    marginTop: "2%",
  },
});