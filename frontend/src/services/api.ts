import {
  Product,
  PaginatedResponse,
  Category,
  CategoryListResponse,
} from "../type";
import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000/api/products/";
const CAT_URL = "http://127.0.0.1:8000/api/categories/";

/*---PRODUCT API CALLS----*/
export const fetchInventory = async (
  page: number,
): Promise<PaginatedResponse> => {
  const response = await axios.get(`${BASE_URL}?page=${page}`);
  return response.data;
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

/*-----CATEGORY API CALLS-------*/
export const fetchCategories = async (): Promise<Category[]> => {
  const response = await axios.get(CAT_URL);
  return response.data;
};

export const fetchCategoryDetail = async (id: string): Promise<Category> => {
  const response = await axios.get(`${CAT_URL}${id}/`);
  return response.data;
};

export const createCategory = async (data: {
  title: string;
  description?: string;
}): Promise<{ id: string; message: string }> => {
  const response = await axios.post(CAT_URL, data);
  return response.data;
};

export const updateCategory = async (
  id: string,
  data: any,
): Promise<{ message: string; category: Category }> => {
  const response = await axios.patch(`${CAT_URL}${id}/`, data);
  return response.data;
};

export const deleteCategory = async (id: string): Promise<void> => {
  await axios.delete(`${CAT_URL}${id}/`);
};

export const fetchProductsByCategory = async (
  id: string,
): Promise<Product[]> => {
  const response = await axios.get(`${BASE_URL}category/${id}/`);
  return response.data;
};
