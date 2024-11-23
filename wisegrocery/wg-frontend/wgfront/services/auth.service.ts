import { publicAxios } from "./api";

const register = (username: string, email: string, password1: string, password2: string) => {
  return publicAxios
    .post('/register/', {
        username,
        email,
        password1,
        password2,
    }, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
};

const login = (username: string, password: string) => {
  return publicAxios
    .post("/login/", {
        username: username,
        password: password,
    }, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
};

export default {
  register,
  login,
};