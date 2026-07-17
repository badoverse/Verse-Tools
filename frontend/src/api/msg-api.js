import axios from 'axios';

export async function getData() {
  const response = await axios.get("http://localhost:8000/api/dati");
  return response.data;
}