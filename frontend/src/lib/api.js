import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' }
});

// Auth
export const authAPI = {
  session: (sessionId) => API.post('/auth/session', { session_id: sessionId }),
  login: (email, password) => API.post('/auth/login', { email, password }),
  register: (email, password, name) => API.post('/auth/register', { email, password, name }),
  me: () => API.get('/auth/me'),
  logout: () => API.post('/auth/logout')
};

// Docks
export const docksAPI = {
  list: (status) => API.get('/coordination/docks', { params: status ? { status } : {} }),
  get: (id) => API.get(`/coordination/docks/${id}`),
  create: (data) => API.post('/coordination/docks', data),
  update: (id, data) => API.patch(`/coordination/docks/${id}`, data),
  assign: (dockId, carrierId, options) => API.post('/coordination/assign-dock', {
    dock_id: dockId,
    carrier_id: carrierId,
    ...options
  })
};

// Carriers
export const carriersAPI = {
  list: (status) => API.get('/carriers', { params: status ? { status } : {} }),
  get: (id) => API.get(`/carriers/${id}`),
  create: (data) => API.post('/carriers', data),
  updatePosition: (id, lat, lng) => API.patch(`/carriers/${id}/position`, { lat, lng })
};

// Routing
export const routingAPI = {
  plan: (carrierId, originLat, originLng, destDockId) => API.post('/v1/routing/plan', {
    carrier_id: carrierId,
    origin_lat: originLat,
    origin_lng: originLng,
    destination_dock_id: destDockId
  })
};

// Protocol
export const protocolAPI = {
  validate: (l1String) => API.post('/v1/protocol/validate', { l1_string: l1String }),
  generate: (lat, lng, alt = 0) => API.post('/v1/protocol/generate', { lat, lng, alt }),
  testVectors: () => API.get('/v1/protocol/test-vectors'),
  resolve: (handle) => API.get(`/v1/resolve/${handle}`)
};

// Analytics
export const analyticsAPI = {
  dashboard: () => API.get('/v1/analytics/dashboard'),
  slaCompliance: () => API.get('/v1/analytics/sla-compliance')
};

// Locations
export const locationsAPI = {
  list: () => API.get('/locations'),
  create: (data) => API.post('/locations', data)
};

// Notifications
export const notificationsAPI = {
  arrivalAlert: (carrierId, dockId, message) => API.post('/v1/notifications/arrival-alert', {
    carrier_id: carrierId,
    dock_id: dockId,
    message
  })
};

export default API;
