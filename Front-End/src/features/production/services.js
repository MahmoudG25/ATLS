import api from '../../services/api';

export const getYields = async (plotId, year) => {
    const params = {};
    if (plotId) params.plot = plotId;
    if (year) params.year = year;
    return (await api.get('production/yields', { params })).data;
};

export const createYield = async (data) => (await api.post('production/yields', data)).data;
