declare module 'react-native-form-validator';

type ConfigType = {
  id?: string,
  notify_by_email?: boolean,
  notify_on_expiration?: boolean,
  notify_on_expiration_before?: string,
  notify_on_min_stock?: boolean,
  default_expired_action?: number,
  prolong_expired_for?: number,
  base_shop_plan_on_historic_data?: boolean,
  historic_period?: number,
  gen_shop_plan_on_min_stock?: boolean
}

type SettingsStateType = {
  settings: {
    config: ConfigType,
    status: string,
    error: any
  }
}

type UserStateType = {
    user: {
      auth: {
        accessToken: string?,
        refreshToken: string?,
        authenticated: boolean,
      },
      status: string,
      error: any,
    },
  };