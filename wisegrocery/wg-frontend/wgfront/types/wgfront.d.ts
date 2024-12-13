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

type UserType = {
  username: string,
  email: string | null,
  password: string | null,
  password1: string | null,
  password2: string | null
}
  
type AuthType = {
  access: string | null, 
  refresh: string | null, 
  authenticated: boolean
};

type UserStateType = {
    user: {
      auth: AuthType,
      status: string,
      error: any,
    },
  };

type ModuleType = {
  name: string,
  text: string,
  parent: string,
}