import { publicAxios } from "./api";

const register = (username, email, password1, password2) => {
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

const login = (username, password) => {
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