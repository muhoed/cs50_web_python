import { protectedAxios } from "./api";
import authHeader from "./auth-header";

const getSettings = () => {
  return protectedAxios.get("/config/", { headers: authHeader() });
};

const updateSettings = (id: string, payload: any) => {
  console.log(payload);
  return protectedAxios.patch(`/config/${id}/`, payload, { headers: authHeader(), });
} 

const saveSettings = (id: string, payload: any) => {
  return protectedAxios.put(`/config/${id}/`, payload, { headers: authHeader() });
};

export default { getSettings, updateSettings, saveSettings };