// Single place that talks to blog-api.
// Relative "/api" works everywhere: nginx proxies it in Docker/Kubernetes,
// and the CRA dev server proxies it to localhost:8000 during `npm start`.
const API_BASE = process.env.REACT_APP_API_URL || '/api';
const TOKEN_KEY = 'authToken';

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

// Called on any 401 so the app can log the user out (expired token etc.).
let onUnauthorized = () => {};
export const setUnauthorizedHandler = (fn) => { onUnauthorized = fn; };

const errorMessage = (data, fallback) => {
  if (!data || !data.detail) return fallback;
  if (typeof data.detail === 'string') return data.detail;
  // FastAPI validation errors: [{ loc, msg, ... }]
  return data.detail.map((d) => `${d.loc[d.loc.length - 1]}: ${d.msg}`).join(', ');
};

export async function request(path, { method = 'GET', body, signal } = {}) {
  const headers = {};
  const token = tokenStore.get();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers['Content-Type'] = 'application/json';

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
  });

  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);

  if (!res.ok) {
    if (res.status === 401 && token) onUnauthorized();
    throw new ApiError(res.status, errorMessage(data, `Request failed (${res.status})`));
  }
  return data;
}

export const api = {
  register: (user) => request('/auth/register', { method: 'POST', body: user }),
  login: (username, password) => request('/auth/login', { method: 'POST', body: { username, password } }),
  me: () => request('/users/me'),
  setAvatar: (avatar) => request('/users/me/avatar', { method: 'PATCH', body: { avatar } }),
  listBlogs: (opts) => request('/blogs', opts),
  getBlog: (id, opts) => request(`/blogs/${id}`, opts),
  createBlog: (blog) => request('/blogs', { method: 'POST', body: blog }),
  deleteBlog: (id) => request(`/blogs/${id}`, { method: 'DELETE' }),
};
