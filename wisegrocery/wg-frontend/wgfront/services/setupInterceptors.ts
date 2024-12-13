import { refreshUserTokens } from "../store/redux/userSlice";
import { protectedAxios, publicAxios } from "./api";
import authHeader from "./auth-header";

const setupInterceptors = (store: any) => {
  protectedAxios.interceptors.request.use(
    (config) => {
      const header = authHeader();
      if (header) {
        config.headers["Authorization"] = header.Authorization;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  const { dispatch } = store;
  protectedAxios.interceptors.response.use(
    (res) => {
      return res;
    },
    async (err) => {
      const originalConfig = err.config;

      if (err.response) {
        // Access Token was expired
        if (err.response.status === 401 && !originalConfig._retry) {
          originalConfig._retry = true;
          try {
            const state = store.getState();
            const rs = await publicAxios.post("/token/refresh/", {
              refresh: state.secure.user.auth.refresh,
            });
            dispatch(refreshUserTokens(rs.data));

            return protectedAxios(originalConfig);

          } catch (_error) {
            return Promise.reject(_error);
          }
        }
      }

      return Promise.reject(err);
    }
  );
};

export default setupInterceptors;