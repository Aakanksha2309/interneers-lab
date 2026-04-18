import { Product, PaginatedResponse } from "../type";
import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000/api/products/";
const CAT_URL = "http://127.0.0.1:8000/api/categories/";

export const fetchInventory = async (
  page: number,
): Promise<PaginatedResponse> => {
  const response = await axios.get(`${BASE_URL}?page=${page}`);
  return response.data;
};

export const fetchCategories = async () => {
  const response = await axios.get(CAT_URL);
  return response.data;
  // This should return the { status: "success", data: [...] } object
};

export const updateProduct = async (
  id: string,
  data: Partial<Product>,
): Promise<any> => {
  const response = await axios.patch(`${BASE_URL}${id}/`, data);
  return response.data;
};

export const fetchProductDetail = async (id: string): Promise<Product> => {
  const response = await axios.get(`${BASE_URL}${id}/`);
  return response.data; // This returns a single Product object {}
};

export const deleteProduct = async (id: string): Promise<void> => {
  await axios.delete(`${BASE_URL}${id}/`);
};
