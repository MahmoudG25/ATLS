import api from './api';

export const reportsApi = {
  // Tasks
  getTasks: (params) => api.get('/reports/tasks/', { params }),
  getTask: (id) => api.get(`/reports/tasks/${id}/`),
  createTask: (data) => api.post('/reports/tasks/', data),
  updateTask: (id, data) => api.put(`/reports/tasks/${id}/`, data),
  deleteTask: (id) => api.delete(`/reports/tasks/${id}/`),
  getTasksSummary: (params) => api.get('/reports/tasks/summary/', { params }),
  exportTasks: (params) => api.get('/reports/tasks/export/', { params, responseType: 'blob' }),

  // Fertilization
  getFertilizations: (params) => api.get('/reports/fertilization/', { params }),
  getFertilization: (id) => api.get(`/reports/fertilization/${id}/`),
  createFertilization: (data) => api.post('/reports/fertilization/', data),
  updateFertilization: (id, data) => api.put(`/reports/fertilization/${id}/`, data),
  deleteFertilization: (id) => api.delete(`/reports/fertilization/${id}/`),

  // Irrigation
  getIrrigations: (params) => api.get('/reports/irrigation/', { params }),
  getIrrigation: (id) => api.get(`/reports/irrigation/${id}/`),
  createIrrigation: (data) => api.post('/reports/irrigation/', data),
  updateIrrigation: (id, data) => api.put(`/reports/irrigation/${id}/`, data),
  deleteIrrigation: (id) => api.delete(`/reports/irrigation/${id}/`),

  // Operations (Dropdown data)
  getOperations: () => api.get('/reports/operations/'),

  // Custom Fields
  getCustomFields: (modelName) => api.get('/reports/custom-fields/', { params: { applies_to_model: modelName } }),
  createCustomField: (data) => api.post('/reports/custom-fields/', data),
  updateCustomField: (id, data) => api.put(`/reports/custom-fields/${id}/`, data),
  deleteCustomField: (id) => api.delete(`/reports/custom-fields/${id}/`),

  // Custom Field Values
  saveCustomFieldValues: (data) => api.post('/reports/custom-field-values/', data),
  getCustomFieldValues: (contentType, objectId) => api.get('/reports/custom-field-values/', { params: { content_type: contentType, object_id: objectId } }),

  // Dropdown Options
  getOptions: (category) => api.get('/reports/options/', { params: { category } }),
  createOption: (data) => api.post('/reports/options/', data),
  updateOption: (id, data) => api.put(`/reports/options/${id}/`, data),
  deleteOption: (id) => api.delete(`/reports/options/${id}/`),

  // Additional APIS for Autocompletes
  getUsers: () => api.get('/users'),
  getSectors: () => api.get('/farm/sectors'),
};
