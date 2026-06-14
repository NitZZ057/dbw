import axios from 'axios';
import { z } from 'zod';
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000' });
api.interceptors.request.use((config) => { config.headers['X-Request-ID'] = crypto.randomUUID(); return config; });
const envelope = z.object({ data: z.unknown(), license: z.string(), sources: z.array(z.string()) }).passthrough();
api.interceptors.response.use((response) => { envelope.parse(response.data); return response; });
export default api;
