import axios from "axios";

const publicAxios = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    "Content-Type": "application/json",
  },
});

const protectedAxios = axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
      "Content-Type": "application/json",
    },
  });

export { publicAxios, protectedAxios };