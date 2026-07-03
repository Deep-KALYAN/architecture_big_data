import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';

// Async thunk for searching companies
export const searchCompanies = createAsyncThunk(
  'company/searchCompanies',
  async (query) => {
    const response = await axios.get(`${API_URL}/companies/search?q=${query}`);
    return response.data;
  }
);

// Async thunk for loading a unified profile sheet
export const fetchCompanyProfile = createAsyncThunk(
  'company/fetchCompanyProfile',
  async (bce) => {
    const response = await axios.get(`${API_URL}/companies/${bce}`);
    return response.data;
  }
);

const companySlice = createSlice({
  name: 'company',
  initialState: {
    searchResults: [],
    selectedProfile: null,
    loading: false,
    error: null,
  },
  reducers: {
    clearProfile: (state) => {
      state.selectedProfile = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Search
      .addCase(searchCompanies.pending, (state) => { state.loading = true; })
      .addCase(searchCompanies.fulfilled, (state, action) => {
        state.loading = false;
        state.searchResults = action.payload;
      })
      .addCase(searchCompanies.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      // Profile
      .addCase(fetchCompanyProfile.pending, (state) => { state.loading = true; })
      .addCase(fetchCompanyProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedProfile = action.payload;
      });
  },
});

export const { clearProfile } = companySlice.actions;
export default companySlice.reducer;