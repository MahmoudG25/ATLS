import api from '../../services/api';

export const getFarms = async () => {
    const response = await api.get('farm/farms');
    return response.data;
};

export const getCropTypes = async () => {
    const response = await api.get('farm/croptypes');
    return response.data;
};

export const getFarmStructure = async (farmId = null) => {
    const params = farmId ? { farm_id: farmId } : {};
    const response = await api.get('farm/structure', { params });
    return response.data;
};

export const createSector = async (data) => {
    const response = await api.post('farm/sectors', data);
    return response.data;
};

export const createPlot = async (data) => {
    const response = await api.post('farm/plots', data);
    return response.data;
};

export const getPlotStats = async (id) => {
    const response = await api.get(`farm/plots/${id}/stats`);
    return response.data;
};
